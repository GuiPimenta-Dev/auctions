import boto3
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import ast
from tenacity import retry, wait_fixed, stop_after_attempt


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
    "Atualizado em",
    "Estado (sigla)", "Cidade", "Endereço",
    "Data do Leilão 1a Hasta", "Data do Leilão 2a Hasta", "Valor de Avaliação", "Lance Inicial",
    "Deságio", "Valor 1a Hasta", "Valor 2a Hasta",
    "Valores somados com leiloeiro + taxas edital 1a Hasta",
    "Valores somados com leiloeiro + taxas edital 2a Hasta", "Tipo de Imóvel", "Modalidade de Venda","Metragem do imóvel",
    "Medida da área privativa ou de uso exclusivo", "Número dormitórios", "Vagas garagem",
    "Modelo de Leilão", "Status", "Fase do Leilão", "Site", "Observações",
    "Valor da Entrada 25% (1a Hasta)", 
    "Valor da Entrada 25% (2a Hasta)", "Mais 30 parcelas de:", "Valor m2 para região", "Imagem"
]

@retry(wait=wait_fixed(30), stop=stop_after_attempt(10))  # Wait 5 seconds and retry up to 10 times
def update_spreadsheet(auction):
    # Get all values from the sheet
    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y")

    sheet_data = worksheet.get_all_records()

    existing_row_index = next(
        (
            idx + 2
            for idx, record in enumerate(sheet_data)
            if record.get("Site") == auction.url
        ),
        None,
    )
    
    desagio = calculate_desagio(auction)

    data = {
        "Atualizado em": current_date,
        "Estado (sigla)": auction.state,
        "Cidade": auction.city,
        "Endereço": auction.address,
        "Data do Leilão 1a Hasta": auction.bids.first_bid.date,
        "Data do Leilão 2a Hasta": auction.bids.second_bid.date,
        "Valor de Avaliação": auction.appraised_value,
        "Lance Inicial": auction.discount_value,
        "Deságio": desagio,
        "Valor 1a Hasta": auction.bids.first_bid.value,
        "Valor 2a Hasta": auction.bids.second_bid.value,
        "Valores somados com leiloeiro + taxas edital 1a Hasta": None,
        "Valores somados com leiloeiro + taxas edital 2a Hasta": None,
        "Tipo de Imóvel": auction.type_,
        "Modalidade de Venda": auction.modality,
        "Metragem do imóvel": auction.m2,
        "Medida da área privativa ou de uso exclusivo": None,
        "Número dormitórios": auction.bedrooms,
        "Vagas garagem": auction.parking,
        "Modelo de Leilão": None,
        "Status": None,
        "Fase do Leilão": None,
        "Site": auction.url,
        "Observações": None,
        "Valor da Entrada 25% (1a Hasta)": None,
        "Mais 30 parcelas de:": None,
        "Valor da Entrada 25% (2a Hasta)": None,
        "Valor m2 para região": None,
        "Imagem": auction.image,
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


def calculate_desagio(auction):
    try:
        appraised_value = auction.appraised_value
        first_bid_value = auction.bids.first_bid.value if auction.bids and auction.bids.first_bid else None

        appraised_value_float = float(appraised_value.replace("R$ ", "").replace(".", "").replace(",", ".")) if appraised_value else None
        first_bid_value_float = float(first_bid_value.replace("R$ ", "").replace(".", "").replace(",", ".")) if first_bid_value else None

        if appraised_value_float or first_bid_value_float:
            desagio = None
        else:
            desagio = f"R$ {appraised_value_float - first_bid_value_float}"
    except:
        desagio = None
    
    return desagio