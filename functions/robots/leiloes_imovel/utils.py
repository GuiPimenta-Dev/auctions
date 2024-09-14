from fuzzywuzzy import process
import re
import requests
import os
import sm_utils

TRELLO_SECRET = sm_utils.get_secret("Trello")
API_KEY = TRELLO_SECRET["KEY"]
TOKEN = TRELLO_SECRET["TOKEN"]
BOARD_ID = "oMpUvmUW"

def add_link_to_card(card_id, attachment_url, description=None):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    query = {
        'key': API_KEY,
        'token': TOKEN,
        'url': attachment_url
    }
    data = {
        'description': description
    } if description else {}
    
    response = requests.post(url, params=query, data=data)
    
    

# Dictionary with property types and their IDs
PROPERTY_TYPES = {
    "agencia": 22,
    "apartamento": 2,
    "area_industrial": 16,
    "area_rural": 5,
    "casa": 1,
    "comercial": 6,
    "galpao": 20,
    "garagem": 13,
    "outros": 11,
    "terreno": 3,
}


def find_property_types(inputs: list) -> list:
    results = []

    for s in inputs:
        # Normalize the input string
        s_normalized = re.sub(r"\s+", " ", s.strip()).lower()

        # Normalize the dictionary keys
        normalized_property_types = {
            re.sub(r"\s+", " ", k).lower(): v for k, v in PROPERTY_TYPES.items()
        }

        # Find the closest property type using fuzzy matching
        closest_property_type = process.extractOne(
            s_normalized, normalized_property_types.keys()
        )

        if not closest_property_type:
            continue
        type_id = normalized_property_types[closest_property_type[0]]
        results.append(str(type_id))

    return results


def xpath(element, xpath):
    elements = element.xpath(xpath)
    if not elements:
        return None
    return elements[0].strip()


def xpath_list(element, xpath):
    elements = element.xpath(xpath)
    if not elements:
        return []
    return elements


def get_lists():

    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"

    querystring = {"key": API_KEY, "token": TOKEN}

    response = requests.request("GET", url, params=querystring)

    return response.json()


def create_a_card(list_id, name, description):

    url = "https://api.trello.com/1/cards"

    query = {
        "idList": list_id,
        "key": API_KEY,
        "token": TOKEN,
        "name": name,
        "desc": description,
    }

    response = requests.request("POST", url, params=query)

    return response.json()


def create_attachment(card_id, filename):

    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    files = {"file": open(filename, "rb")}

    querystring = {"key": API_KEY, "token": TOKEN}

    response = requests.request("POST", url, params=querystring, files=files)


def set_cover(card_id, image_url):

    attach_url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    attach_query = {"key": API_KEY, "token": TOKEN, "url": image_url}

    attach_response = requests.post(attach_url, params=attach_query)
    if attach_response.status_code != 200:
        return f"Failed to attach image: {attach_response.text}"

    attachment_id = attach_response.json().get("id")
    if not attachment_id:
        return "Failed to retrieve attachment ID."

    cover_url = f"https://api.trello.com/1/cards/{card_id}"
    cover_query = {"key": API_KEY, "token": TOKEN}
    cover_data = {"cover": {"idAttachment": attachment_id, "brightness": "dark"}}

    requests.put(cover_url, params=cover_query, json=cover_data)


def css_select(element, selector):
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else None

def css_select_list(element, selector):
    return [e.get_text(strip=True) for e in element.select(selector)]


def get_general_info(soup):
    general_info = soup.select('div.more.row.pb-2 div')
    info = []
    for i in general_info:
        title = "".join(css_select_list(i, "b"))
        text = "".join(css_select_list(i, "*")).replace("\n", "").replace(f"{title}", "").strip()
        if text:
            info.append(f"**{title}** {text}")
    return info


def get_files(soup):
    general_files = soup.select("div.documments.row.pb-4 a")
    files = []
    for i in general_files:
        title = css_select(i, "*")
        link = i.get("href", "").strip()
        if title and link:
            files.append({"title": title, "link": link})
    return files


def create_card_description(price, discount, name, address, image, url, general_info, files):
    general_info_text = '\n'.join(f"- {item}" for item in general_info)
    files_text = '\n'.join(f"- [{item['title']}]({item['link']})" for item in files)

    return f"""
- **Nome:** {name}
- **Endereço:** {address}  
- **Preço:** {price}  
- **Desconto:** {discount}  
{general_info_text}
- [Site do Imóvel]({url})
{files_text}
    """