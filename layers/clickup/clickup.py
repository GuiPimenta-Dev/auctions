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
    auction_question: str


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

    description = f"""
Informações do Cliente:

Nome Completo: {client.full_name}
CPF/CNPJ: {client.cpf_cnpj}
Telefone: {client.phone_number}
Email: {client.email}
Profissão: {client.profession}
Endereço: {client.address}
Cidade: {client.city}
Estado: {client.state}
País: {client.country}
Finalidade da Propriedade: {client.property_purpose}
Experiência em Leilões: {client.auction_experience}
Perguntas: {client.auction_question}

Informações da Propriedade Desejada:

Tipo de Propriedade: {property.property_type}
Cidade: {property.property_city}
Estado: {property.property_state}
Bairros: {', '.join(property.property_neighborhood)}
Orçamento: {property.budget}
Método de Pagamento: {property.payment_method}

"""

    task_data = {
        'name': client.full_name,
        'description': description,
        'assignees': [],    
        'tags': [],         
    }

    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json',
    }

    response = requests.post(f'https://api.clickup.com/api/v2/list/{LIST_ID}/task', json=task_data, headers=headers)
    print(response.json())



def create_auction(auction: Auction, client):
    LIST_ID = '901105512625'  
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

    
    description = f"""
    Informações do Leilão:

    Nome: {auction.name}
    Tipo: {auction.type_}
    Modalidade: {auction.modality}
    Estado: {auction.state}
    Cidade: {auction.city}
    Endereço: {auction.address}
    Bairro: {auction.district}
    Valor Avaliado: {auction.appraised_value}
    Valor de Deságio: {auction.discount_value}
    Primeiro Lance: {auction.bids.first_bid.value} em {auction.bids.first_bid.date}
    Segundo Lance: {auction.bids.second_bid.value} em {auction.bids.second_bid.date}
    Dormitórios: {auction.bedrooms}
    Vagas de Garagem: {auction.parking}
    Metragem: {auction.m2}
    Imagem: {auction.image}
    URL: {auction.url}
    """


    task_data = {
        'name': auction.name,
        'description': description,
        'assignees': [],
        'tags': [],
    }

    response = requests.post(f'https://api.clickup.com/api/v2/list/{LIST_ID}/task', json=task_data, headers=headers)
    return response.json()

