import pandas as pd
import requests
import json
import numpy as np
from datetime import datetime
from dateutil import tz
from zoho_auth import get_zoho_access_token


def sanitize(value):
    if pd.isnull(value) or value in [np.nan, float("inf"), float("-inf")]:
        return ""
    return str(value).strip()

def sanitize_number(value):
    try:
        if pd.isnull(value) or value in [np.nan, float("inf"), float("-inf"), ""]:
            return None
        return float(str(value).replace("R$", "").replace(".", "").replace(",", "."))
    except:
        return None

def parse_excel_date(value):
    if not value:
        return None
    try:
        dt = pd.to_datetime(value)
        return dt.replace(hour=0, minute=0, second=0, tzinfo=tz.gettz("America/Sao_Paulo")).isoformat()
    except:
        return None

def get_or_create_client(access_token, client):
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    name = sanitize(client.get("Nome Completo:"))
    search_url = f"https://www.zohoapis.com/crm/v2/Clientes/search?criteria=(Nome_Completo:equals:{name})"
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if data.get("data"):
        return data["data"][0]["id"]

    payload = {
        "data": [
            {
                "Name": name,
                "Nome_Completo": name,
                "CNPJ_CPF": sanitize(client.get("CPF/CNPJ:")),
                "Email": sanitize(client.get("E-mail:")),
                "Endere_o": sanitize(client.get("Endereço:")),
                "Cidade": sanitize(client.get("Cidade:")),
                "Estado": sanitize(client.get("Estado:")),
                "Pais": sanitize(client.get("País")),
                "Data_de_Nascimento": sanitize(client.get("Data de Nascimento")),
                "Profiss_o": sanitize(client.get("Profissão:")),
                "Telefone": sanitize(client.get("Número do celular:"))
            }
        ]
    }

    create_resp = requests.post("https://www.zohoapis.com/crm/v2/Clientes", headers=headers, json=payload)
    create_data = create_resp.json()
    if create_resp.status_code == 201 and create_data.get("data"):
        return create_data["data"][0]["details"].get("id")

    raise Exception("Erro ao criar cliente no Zoho. Verifique a resposta acima.")


def send_to_zoho(auction, client):
    access_token = get_zoho_access_token()
    client_id = get_or_create_client(access_token, client)

    data_leilao_1 = parse_excel_date(auction.bids.first_bid.date)
    data_leilao_2 = parse_excel_date(auction.bids.second_bid.date)

    payload = {
        "data": [
            {
                "Nome_do_Im_vel": sanitize(auction.name),
                "Cliente_Relacionado": {"id": client_id},
                "Tipo_Imovel": sanitize(auction.type_),
                "Modalidade_de_venda": sanitize(auction.modality),
                "Estado": sanitize(auction.state),
                "Cidade": sanitize(auction.city),
                "Bairro": sanitize(auction.district),
                "Endere_o_Imovel": sanitize(auction.address),
                "Metragem_do_im_vel": sanitize(auction.m2),
                "Dormit_rios": sanitize(auction.bedrooms),
                "Vagas_de_garagem": sanitize(auction.parking),
                "Valor_de_Avalia_o": sanitize(auction.appraised_value),
                "Lance_Inicial": sanitize(auction.discount_value),
                "Valor_1o_Leil_o": sanitize(auction.bids.first_bid.value),
                "Data_do_Leil_o": data_leilao_1,
                "Valor_2o_Leil_o": sanitize(auction.bids.second_bid.value),
                "Data_do_2_leil_o": data_leilao_2,
                "Link_do_Im_vel": sanitize(auction.url),
                "Link_da_imagem": sanitize(auction.image),
                "Link_da_busca": "",  # pode ser customizado se quiser passar a URL da busca
            }
        ]
    }

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://www.zohoapis.com/crm/v2/Im_veis"
    response = requests.post(url, headers=headers, json=payload)

    print("📌 ZOHO STATUS:", response.status_code)
    print("📌 ZOHO RESPONSE:", json.dumps(response.json(), indent=2, ensure_ascii=False))
