import json
from dataclasses import dataclass

import boto3
import requests
from auction import Auction

LIST_ID = "901105021286"  # ClickUp List ID


@dataclass
class PersonalInformation:
    full_name: str
    cpf_cnpj: str
    email: str
    phone_number: str
    address: str
    profession: str
    state: str
    city: str
    country: str
    property_purpose: str
    auction_experience: str
    auction_question: str = ""


@dataclass
class PropertyInformation:
    property_type: str
    property_city: str
    property_state: str
    property_neighborhood: list
    budget: float
    payment_method: str


@dataclass
class Files:
    title: str
    link: str


@dataclass
class GeneralInfo:
    title: str
    text: str


@dataclass
class Task:
    personal_information: PersonalInformation
    property_information: PropertyInformation
    auction: Auction


def create_client(client: PersonalInformation, property: PropertyInformation):

    LIST_ID = '901105017897'  
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId="Clickup")
    secret = json.loads(response["SecretString"])

    API_TOKEN = secret["PERSONAL"]
    
    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json',
    }

    response = requests.get(f'https://api.clickup.com/api/v2/list/{LIST_ID}/field', headers=headers)
    custom_fields = response.json().get('fields', [])
    custom_fields = {field["name"]: field["id"] for field in custom_fields}


    task_data = {
        'name': client.full_name,
        'assignees': [],    
        'tags': [],
        'custom_fields': [
        
            {
                "id": custom_fields["CPF/CNPJ"],
                "value": client.cpf_cnpj
            },
            {
                "id": custom_fields["Email"],
                "value": client.email
            },
            {
                "id": custom_fields["Número celular:"],
                "value": client.phone_number
            },
            {
                "id": custom_fields["Endereço"],
                "value": client.address
            },
            {
                "id": custom_fields["Cidade"],
                "value": client.city
            },
            {
                "id": custom_fields["Estado"],
                "value": client.state
            },
            {
                "id": custom_fields["País:"],
                "value": client.country
            },
            {
                "id": custom_fields["Profissão:"],
                "value": client.profession
            },
            {
                "id": custom_fields["Experiência em Leilão"],
                "value": client.auction_experience
            },
            {
                "id": custom_fields["Dúvidas"],
                "value": client.auction_question or "Nenhuma"
            },
            {
                "id": custom_fields["Valor de Investimento:"],
                "value": str(property.budget)
            },
            {
                "id": custom_fields["Estado de Interesse:"],
                "value": property.property_state
            },
            {
                "id": custom_fields["Cidade de Interesse:"],
                "value": property.property_city
            },
            {
                "id": custom_fields["Bairros de Interesse:"],
                "value": ", ".join(property.property_neighborhood)
            },
            {
                "id": custom_fields["Tipo de Imóvel"],
                "value": property.property_type
            },
            {
                "id": custom_fields["Finalidade do Imóvel:"],
                "value": client.property_purpose
            },
            {
                "id": custom_fields["Forma de Pagamento"],
                "value": ", ".join(property.payment_method)
            }
        ]
    }


    response = requests.post(f'https://api.clickup.com/api/v2/list/{LIST_ID}/task', json=task_data, headers=headers)
    print(f"Clickup: {response.json()} ")
    return response.json()



def create_auction(auction, client):
    LIST_ID = '901105512625'
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId="Clickup")
    secret = json.loads(response["SecretString"])

    API_TOKEN = secret["PERSONAL"]

    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json',
    }

    # Fetch custom fields from ClickUp
    response = requests.get(f'https://api.clickup.com/api/v2/list/{LIST_ID}/field', headers=headers)
    custom_fields = response.json().get('fields', [])
    custom_fields = {field["name"]: field["id"] for field in custom_fields}

    # Task data
    task_data = {
        'name': f"{client} - {auction.name}",
        'assignees': [],
        'tags': [],
        "custom_fields": [
            {"id": custom_fields["Tipo de Imóvel"], "value": auction.type_},
            {"id": custom_fields["Modalidade de Venda"], "value": auction.modality},
            {"id": custom_fields["Estado"], "value": auction.state},
            {"id": custom_fields["Cidade"], "value": auction.city},
            {"id": custom_fields["Endereço"], "value": auction.address},
            {"id": custom_fields["Bairro"], "value": auction.district},
            {"id": custom_fields["Valor de Avaliação"], "value": auction.appraised_value},
            {"id": custom_fields["Lance Inicial"], "value": auction.discount_value},
            {"id": custom_fields["Data 1o Leilão"], "value": auction.bids.first_bid.date},
            {"id": custom_fields["Data 2o Leilão"], "value": auction.bids.second_bid.date},
            {"id": custom_fields["Dormitórios"], "value": auction.bedrooms},
            {"id": custom_fields["Vagas de Garagem"], "value": auction.parking},
            {"id": custom_fields["🌐 Site"], "value": auction.url},
            {"id": custom_fields["Metragem do Imóvel"], "value": auction.m2},
        ]
    }

    # Create the task
    response = requests.post(f'https://api.clickup.com/api/v2/list/{LIST_ID}/task', json=task_data, headers=headers)
    task = response.json()

    if auction.image:
        task_id = task['id']
        
        # Fetch image content from the URL
        image_response = requests.get(auction.image)
        if image_response.status_code == 200:
            files = {
                'attachment': (f'{auction.name}.jpg', image_response.content, 'image/jpeg')
            }
            attachment_response = requests.post(
                f'https://api.clickup.com/api/v2/task/{task_id}/attachment?custom_task_ids=true&set_cover=true',
                headers={'Authorization': API_TOKEN},
                files=files
            )
            attachment_response.raise_for_status()  # Raises an error if the request failed
        else:
            print(f"Failed to fetch cover image. Status code: {image_response.status_code}")

    return task

