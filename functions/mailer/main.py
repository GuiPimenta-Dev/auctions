import boto3
import datetime
import csv
import io
import json
from boto3.dynamodb.conditions import Key
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Inicializar os recursos
dynamodb = boto3.resource("dynamodb")
ses = boto3.client("ses")  # SES para envio de emails
table_name = "Properties"  # Substitua pelo nome da sua tabela do DynamoDB
table = dynamodb.Table(table_name)

# Configurações de email
# sender_email = "guialvespimenta27@gmail.com"
sender_email = "marportesrocha@gmail.com"
# recipient_email = "guialvespimenta27@gmail.com"
recipient_email = "marportesrocha@gmail.com"
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

subject = f"Imóveis em Leilão ({current_date})"  # Assunto do email
body_text = ""

# Colunas do CSV para referência
columns = [
    "Estado (sigla)", "Cidade", "Bairro", "Endereço",
    "Data do Leilão 1a Hasta", "Data do Leilão 2a Hasta", "Valor de Avaliação", "Lance Inicial",
    "Deságio", "Valor 1a Hasta", "Valor 2a Hasta",
    "Valores somados com leiloeiro + taxas edital 1a Hasta",
    "Valores somados com leiloeiro + taxas edital 2a Hasta", "Tipo de Imóvel", "Metragem do imóvel",
    "Medida da área privativa ou de uso exclusivo", "Número dormitórios", "Vagas garagem",
    "Modelo de Leilão", "Status", "Fase do Leilão", "Cliente", "Site", "Observações",
    "Valor da Entrada 25% (1a Hasta)", 
    "Valor da Entrada 25% (2a Hasta)", "Mais 30 parcelas de:", "Valor m2 para região"
]

def lambda_handler(event, context):
    # Query no DynamoDB para registros de hoje
    response = table.query(
        KeyConditionExpression=Key("PK").eq(current_date)
    )
    items = response.get("Items", [])

    if not items:
        return {"statusCode": 200, "body": json.dumps(f"No data found for {current_date}")}

    # Criar CSV na memória
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Escrever o cabeçalho
    csv_writer.writerow(columns)

    # Iterar sobre os itens e organizar os dados em dicionário
    for item in items:
        auction = item["auction"]
        property_info = item["property_info"]
        personal_info = item["personal_info"]

        # Criar um dicionário com os valores mapeados por chave
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
            "Site": auction.get("url"),
            "Observações": None,
            "Valor da Entrada 25% (1a Hasta)": None,
            "Mais 30 parcelas de:": None,
            "Valor da Entrada 25% (2a Hasta)": None,
            "Valor m2 para região": None
        }

        # Escrever os valores na ordem das colunas
        csv_writer.writerow([data[col] for col in columns])

    # Converter CSV para string
    csv_data = csv_buffer.getvalue()

    # Enviar o CSV por email como anexo
    send_email_with_attachment(current_date, csv_data)

    return {"statusCode": 200, "body": json.dumps(f"Email sent for {current_date}")}

def send_email_with_attachment(current_date, csv_data):
    # Criar email multipart
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # Anexar o corpo do email
    msg.attach(MIMEText(body_text))

    # Anexar o CSV
    part = MIMEBase("application", "octet-stream")
    part.set_payload(csv_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{current_date}.csv"')

    msg.attach(part)

    # Enviar email usando AWS SES
    response = ses.send_raw_email(
        Source=sender_email,
        Destinations=[recipient_email],
        RawMessage={
            "Data": msg.as_string(),
        },
    )
    print(f"Email sent! Message ID: {response['MessageId']}")

lambda_handler({}, {})
