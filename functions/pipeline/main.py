import boto3
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import ast

# Initialize AWS Secrets Manager
secrets_manager = boto3.client('secretsmanager')

# Fetch Google credentials from Secrets Manager
def get_google_credentials(secret_name):
    response = secrets_manager.get_secret_value(SecretId=secret_name)
    secret_string = response['SecretString']
    return json.loads(secret_string)  # Assuming the secret is stored as a JSON string

# Authenticate with Google service account using credentials from Secrets Manager
secret_name = 'GoogleSheets'  # Replace with your secret name in Secrets Manager
google_creds = get_google_credentials(secret_name)
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds)

client = gspread.authorize(creds)

# Access the spreadsheet by name and folder ID
spreadsheet_name = "Imóveis"
folder_id = ''  # Folder ID on Google Drive (if necessary)
worksheet = client.open(title=spreadsheet_name, folder_id=folder_id).get_worksheet(0)

# Spreadsheet columns for reference (including the "Atualizado em" column)
columns = [
    "Estado (sigla)", "Cidade", "Bairro", "Endereço",
    "Data do Leilão 1a Hasta", "Data do Leilão 2a Hasta", "Valor de Avaliação", "Lance Inicial",
    "Deságio", "Valor 1a Hasta", "Valor 2a Hasta",
    "Valores somados com leiloeiro + taxas edital 1a Hasta",
    "Valores somados com leiloeiro + taxas edital 2a Hasta", "Tipo de Imóvel", "Metragem do imóvel",
    "Medida da área privativa ou de uso exclusivo", "Número dormitórios", "Vagas garagem",
    "Modelo de Leilão", "Status", "Fase do Leilão", "Cliente", "Site", "Observações",
    "Valor da Entrada 25% (1a Hasta)", 
    "Valor da Entrada 25% (2a Hasta)", "Mais 30 parcelas de:", "Valor m2 para região",
    "Atualizado em"  # New column to track the update date
]

def lambda_handler(event, context):
    # Get the current date
    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y")
    
    # Assume the SQS message is in the event, with records under 'Records' key
    for record in event.get('Records', []):
        # Parse the SQS message body
        message_body = json.loads(record["body"])

        # Process the message
        update_spreadsheet(message_body, current_date)

    return {"statusCode": 200, "body": json.dumps(f"Spreadsheet successfully updated for {current_date}")}

def update_spreadsheet(item, current_date):
    # Get all values from the sheet
    sheet_data = worksheet.get_all_records()

    auction = item["auction"]
    property_info = item["property_info"]
    personal_info = item["personal_info"]
    url = auction.get("url")

    # Check if URL already exists in the sheet
    existing_row_index = None
    for idx, record in enumerate(sheet_data):
        if record.get("Site") == url:
            existing_row_index = idx + 2  # Adjust index for row number in the sheet
            break

    # Prepare the data dictionary mapped to column keys
    data = {
        "Estado (sigla)": auction.get("state"),
        "Cidade": property_info.get("property_city"),
        "Bairro": ", ".join(property_info.get("property_neighborhood", [])),
        "Endereço": auction.get("address"),
        "Data do Leilão 1a Hasta": auction.get("bids", {}).get("first_bid", {}).get("date"),
        "Data do Leilão 2a Hasta": auction.get("bids", {}).get("second_bid", {}).get("date"),
        "Valor de Avaliação": auction.get("appraised_value"),
        "Lance Inicial": auction.get("discount_value"),
        "Deságio": None,
        "Valor 1a Hasta": auction.get("bids", {}).get("first_bid", {}).get("value"),
        "Valor 2a Hasta": auction.get("bids", {}).get("second_bid", {}).get("value"),
        "Valores somados com leiloeiro + taxas edital 1a Hasta": None,
        "Valores somados com leiloeiro + taxas edital 2a Hasta": None,
        "Tipo de Imóvel": auction.get("type_"),
        "Metragem do imóvel": auction.get("m2"),
        "Medida da área privativa ou de uso exclusivo": None,
        "Número dormitórios": auction.get("bedrooms"),
        "Vagas garagem": auction.get("parking"),
        "Modelo de Leilão": None,
        "Status": None,
        "Fase do Leilão": None,
        "Cliente": personal_info["full_name"],
        "Site": url,
        "Observações": None,
        "Valor da Entrada 25% (1a Hasta)": None,
        "Mais 30 parcelas de:": None,
        "Valor da Entrada 25% (2a Hasta)": None,
        "Valor m2 para região": None,
        "Atualizado em": current_date  # New column value for tracking updates
    }

    # Prepare values in the order of the columns
    row_values = [data[col] for col in columns]

    if existing_row_index:
        # Update the entire row (including the "Atualizado em" field)
        worksheet.update(f'A{existing_row_index}:AC{existing_row_index}', [row_values])
    else:
        # Add a new row
        next_row = len(sheet_data) + 2  # Start from the next empty row
        worksheet.insert_row(row_values, next_row)

if __name__ == '__main__':
    lambda_handler({}, {})
