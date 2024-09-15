import json
import os
from dataclasses import dataclass

import boto3
import requests

BOARD_ID = "oMpUvmUW"


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
class PropertyDetails:
    name: str
    address: str
    price: float
    discount: float
    url: str
    general_info: GeneralInfo
    files: Files


@dataclass
class Card:
    personal_information: PersonalInformation
    property_information: PropertyInformation
    property_details: PropertyDetails
    cover: str


def create_card(card: Card):
    url = "https://api.trello.com/1/cards"

    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId="Trello")
    secret = json.loads(response["SecretString"])

    API_KEY = secret["KEY"]
    TOKEN = secret["TOKEN"]

    lists = get_lists(api_key=API_KEY, token=TOKEN)
    first_list = lists[0]

    title = create_title(card)
    description = create_description(card)

    query = {
        "idList": first_list["id"],
        "key": API_KEY,
        "token": TOKEN,
        "name": title,
        "desc": description,
    }

    response = requests.request("POST", url, params=query).json()
    set_cover(response["id"], card.cover, API_KEY, TOKEN)


def get_lists(api_key, token):

    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"

    querystring = {"key": api_key, "token": token}

    response = requests.request("GET", url, params=querystring)

    return response.json()


def create_description(card: Card):
    personal_info_section = f"""
### 🧑 **Informações do Cliente**
- **Nome Completo:** {card.personal_information.full_name}
- **CPF/CNPJ:** {card.personal_information.cpf_cnpj}
- **Telefone:** {card.personal_information.phone_number}
- **Email:** {card.personal_information.email}
- **Profissão:** {card.personal_information.profession}
- **Endereço:** {card.personal_information.address}
- **Cidade:** {card.personal_information.city}
- **Estado:** {card.personal_information.state}
- **País:** {card.personal_information.country}
- **Finalidade do Imóvel:** {card.personal_information.property_purpose}
- **Experiência com Leilões:** {card.personal_information.auction_experience}
- **Dúvidas:** {card.personal_information.auction_question}
"""

    property_info_section = f"""
### 🏡 **Informações do Imóvel Desejado**
- **Tipo de Imóvel:** {card.property_information.property_type}
- **Cidade:** {card.property_information.property_city}
- **Estado:** {card.property_information.property_state}
- **Bairro:** {', '.join(card.property_information.property_neighborhood)}
- **Valor de Investimento:** { format_money(card.property_information.budget) }
- **Formas de Pagamento:** { card.property_information.payment_method }
"""

    # Detalhes gerais da propriedade (detalhes flexíveis)
    general_info_text = "\n".join(
        f"- **{item['title']}:** {item['text']}"
        for item in card.property_details.general_info
    )
    files_text = "\n".join(
        f"- [{item['title']}]({item['link']})" for item in card.property_details.files
    )

    # Detalhes específicos da transação/negócio
    property_details_section = f"""
### 💼 **Detalhes do Imóvel Encontrado**
- **Nome do Imóvel:** {card.property_details.name}
- **Endereço:** {card.property_details.address}
- **Preço:** {card.property_details.price}
{general_info_text}

---

### 🔗 **Arquivos Relacionados**
{files_text}

---

### 🌐 **Link do Imóvel**
[{card.property_details.url}]({card.property_details.url})

---
"""

    return f"{personal_info_section}\n---\n{property_info_section}\n---\n{property_details_section}"


def format_money(amount):
    formatted_amount = (
        f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    return formatted_amount


def set_cover(card_id, image_url, api_key, token):

    attach_url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    attach_query = {"key": api_key, "token": token, "url": image_url}

    attach_response = requests.post(attach_url, params=attach_query)
    if attach_response.status_code != 200:
        return f"Failed to attach image: {attach_response.text}"

    attachment_id = attach_response.json().get("id")
    if not attachment_id:
        return "Failed to retrieve attachment ID."

    cover_url = f"https://api.trello.com/1/cards/{card_id}"
    cover_query = {"key": api_key, "token": token}
    cover_data = {"cover": {"idAttachment": attachment_id, "brightness": "dark"}}

    requests.put(cover_url, params=cover_query, json=cover_data)


def create_title(card: Card):
    return f"{card.personal_information.full_name} - {card.property_details.name}"
