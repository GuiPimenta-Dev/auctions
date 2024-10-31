import datetime
import json

import boto3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tenacity import retry, stop_after_attempt, wait_fixed

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

excel_client = gspread.authorize(creds)

# Access the spreadsheet by name and folder ID
spreadsheet_name = "Imóveis"
folder_id = ''  # Folder ID on Google Drive (if necessary)


@retry(wait=wait_fixed(30), stop=stop_after_attempt(10))  # Wait 5 seconds and retry up to 10 times
def update_auctions_spreadsheet(auction, client, search_url):

    # Spreadsheet columns for reference (including the "Atualizado em" column)
    columns = [
        "Atualizado em", "Criar Card", "Cliente",
        "Estado (sigla)", "Cidade", "Bairro", "Nome do Imóvel", "Endereço",
        "Data do Leilão 1a Hasta", "Data do Leilão 2a Hasta", "Valor de Avaliação", "Lance Inicial",
        "Deságio", "Valor 1a Hasta", "Valor 2a Hasta",
        "Valores somados com leiloeiro + taxas edital 1a Hasta",
        "Valores somados com leiloeiro + taxas edital 2a Hasta", "Tipo de Imóvel", "Modalidade de Venda","Metragem do imóvel",
        "Medida da área privativa ou de uso exclusivo", "Número dormitórios", "Vagas garagem",
        "Modelo de Leilão", "Status", "Fase do Leilão", "Site", "Observações",
        "Valor da Entrada 25% (1a Hasta)", 
        "Valor da Entrada 25% (2a Hasta)", "Mais 30 parcelas de:", "Valor m2 para região", "Imagem", "Busca"
    ]

    worksheet = excel_client.open(title=spreadsheet_name, folder_id=folder_id).get_worksheet(0)
    
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
        "Criar Card": None,
        "Cliente": client,
        "Estado (sigla)": auction.state,
        "Cidade": auction.city,
        "Endereço": auction.address,
        "Bairro": auction.district,
        "Nome do Imóvel": auction.name,
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
        "Busca": search_url,
    }

    # Prepare values in the order of the columns
    row_values = [data[col] for col in columns]

    if existing_row_index:
        # Update the entire row (including the "Atualizado em" field)
        worksheet.update(f'A{existing_row_index}:AH{existing_row_index}', [row_values], raw=False)
    else:
        # Add a new row
        next_row = len(sheet_data) + 2
        worksheet.insert_row(row_values, next_row)
        card = f"https://sv1th8vfbh.execute-api.us-east-2.amazonaws.com/prod/card?index={next_row}"
        worksheet.update_acell(f'B{next_row}', f"=HYPERLINK(\"{card}\"; \"Criar Card\")")
    
    

def update_clients_spreadsheet(client):

    columns = [
        "Data de Inclusão", "Nome Completo", "CPF/CNPJ", "E-mail", "Número do celular",
        "Endereço", "Cidade", "Estado", "País", "Profissão",
        "Possui experiência anteriores em leiloes?", "Qual sua principal dúvida sobre leiloes?",
        "Valor de orçamento destinado ao investimento", "Estado de interesse", "Cidade de interesse",
        "Bairros de interesse", "Tipo de imóvel", "Finalidade do imóvel", "Formas de pagamento relevantes"
    ]
    worksheet = excel_client.open(title=spreadsheet_name, folder_id=folder_id).get_worksheet(1)
    
    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y")

    sheet_data = worksheet.get_all_records()

    data = {
        "Data de Inclusão": current_date,
        "Nome Completo": client["personal_information"]["full_name"],
        "CPF/CNPJ": client["personal_information"]["cpf_cnpj"],
        "E-mail": client["personal_information"]["email"],
        "Número do celular": client["personal_information"]["phone_number"],
        "Endereço": client["personal_information"]["address"],
        "Cidade": client["personal_information"]["city"],
        "Estado": client["personal_information"]["state"],
        "País": client["personal_information"]["country"],
        "Profissão": client["personal_information"]["profession"],
        "Possui experiência anteriores em leiloes?": client["personal_information"]["auction_experience"],
        "Qual sua principal dúvida sobre leiloes?": client["personal_information"]["auction_question"],
        "Valor de orçamento destinado ao investimento": str(client["property_information"]["budget"]),
        "Estado de interesse": client["property_information"]["property_state"],
        "Cidade de interesse": client["property_information"]["property_city"],
        "Bairros de interesse": ", ".join(client["property_information"]["property_neighborhood"]),
        "Tipo de imóvel": client["property_information"]["property_type"],
        "Finalidade do imóvel": client["personal_information"]["property_purpose"],
        "Formas de pagamento relevantes": client["property_information"]["payment_method"],
    }

    # Prepare values in the order of the columns
    row_values = [data[col] for col in columns]
    
    next_row = len(sheet_data) + 2  # Start from the next empty row
    worksheet.insert_row(row_values, next_row)

def calculate_desagio(auction):
    try:
        appraised_value = auction.appraised_value
        first_bid_value = auction.bids.first_bid.value if auction.bids and auction.bids.first_bid else None

        appraised_value_float = float(appraised_value.replace("R$ ", "").replace(".", "").replace(",", ".")) if appraised_value else None
        first_bid_value_float = float(first_bid_value.replace("R$ ", "").replace(".", "").replace(",", ".")) if first_bid_value else None

        if appraised_value_float and first_bid_value_float:
            desagio = f"R$ {round(appraised_value_float - first_bid_value_float,2)}"
        else:
            desagio = None
    except:
        desagio = None
    
    return desagio

def get_clients():
    worksheet = excel_client.open(title=spreadsheet_name, folder_id=folder_id).get_worksheet(1)
    return worksheet.get_all_records()


def get_auction_row(row_number):
    worksheet = excel_client.open(title=spreadsheet_name, folder_id=folder_id).get_worksheet(0)
    columns = worksheet.row_values(1)
    values = worksheet.row_values(row_number)
    
    # Format values to currency if they appear to be numeric
    return dict(zip(columns, values))