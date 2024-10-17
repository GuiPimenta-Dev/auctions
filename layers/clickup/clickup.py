import json
import os
from dataclasses import dataclass

from auction.auction import Auction
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()
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


def create_task(task: Task):
    url = f"https://api.clickup.com/api/v2/list/{LIST_ID}/task"
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId="Clickup")
    secret = json.loads(response["SecretString"])

    API_TOKEN = secret["PERSONAL"]

    title = create_title(task)
    description = create_description(task)

    headers = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

    payload = {
        "name": title,
        "description": description,
        "assignees": [],  # Add assignee IDs if needed
        "tags": ["property"],
        "status": "to do",
        "priority": 3,
        "due_date": None,  # Add a timestamp if applicable
        "due_date_time": False,
        "time_estimate": None,
        "start_date": None,
        "start_date_time": False,
        "notify_all": True,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        task_id = response.json().get("id")
    else:
        print(f"Failed to create task: {response.text}")


def create_description(task: Task) -> str:
    # Seção de Informações do Cliente
    personal_info_section = f"""
Informações do Cliente:

Nome Completo: {task.personal_information.full_name}
CPF/CNPJ: {task.personal_information.cpf_cnpj}
Telefone: {task.personal_information.phone_number}
Email: {task.personal_information.email}
Profissão: {task.personal_information.profession}
Endereço: {task.personal_information.address}
Cidade: {task.personal_information.city}
Estado: {task.personal_information.state}
País: {task.personal_information.country}
Finalidade da Propriedade: {task.personal_information.property_purpose}
Experiência em Leilões: {task.personal_information.auction_experience}
Perguntas: {task.personal_information.auction_question}

"""

    # Seção de Informações da Propriedade Desejada
    property_info_section = f"""
Informações da Propriedade Desejada:

Tipo de Propriedade: {task.property_information.property_type}
Cidade: {task.property_information.property_city}
Estado: {task.property_information.property_state}
Bairros: {', '.join(task.property_information.property_neighborhood)}
Orçamento: {format_money(task.property_information.budget)}
Método de Pagamento: {task.property_information.payment_method}

"""

    # Seção de Informações Gerais
    general_info_text = (
        "\n".join(
            f"{item['title']}: {item['text']}" for item in task.auction.general_info
        )
        if task.auction.general_info
        else "Informações Gerais: Nenhum detalhe disponível."
    )

    # Seção de Arquivos
    files_text = (
        "\n".join(f"{item['title']}: {item['link']}" for item in task.auction.files)
        if task.auction.files
        else "Arquivos Relacionados: Nenhum arquivo disponível."
    )

    # Seção de Detalhes da Propriedade Encontrada
    auction_section = f"""
Detalhes da Propriedade Encontrada:

Nome da Propriedade: {task.auction.name}
Endereço: {task.auction.address}
Preço: {task.auction.discount_value}
{general_info_text}

Arquivos Relacionados:
{files_text}

Link da Propriedade:
{task.auction.url}

"""

    # Combina todas as seções em uma única descrição
    full_description = personal_info_section + property_info_section + auction_section

    return full_description


def format_money(amount):
    amount = float(amount)
    formatted_amount = (
        f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    return formatted_amount


def create_title(task: Task):
    return f"{task.personal_information.full_name} - {task.auction.name}"
