import pandas as pd
from io import BytesIO

def generate_excel_binary(data):
    """Generate an Excel file in memory and return its binary content."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for category, items in data.items():
            if not items:
                continue
            df = pd.DataFrame(items)
            formatted_headers = [col.replace("_", " ").title() for col in df.columns]
            df.columns = formatted_headers  # Format headers
            df.to_excel(writer, sheet_name=category[:31], index=False)  # Excel sheet names max 31 chars

    output.seek(0)  # Move to the start of the stream
    return output.read()  # Return binary content


