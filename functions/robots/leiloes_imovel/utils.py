from openpyxl import Workbook

from fuzzywuzzy import process
import re

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
    "terreno": 3
}

def find_property_types(inputs: list) -> list:
    results = []

    for s in inputs:
        # Normalize the input string
        s_normalized = re.sub(r'\s+', ' ', s.strip()).lower()

        # Normalize the dictionary keys
        normalized_property_types = {re.sub(r'\s+', ' ', k).lower(): v for k, v in PROPERTY_TYPES.items()}

        # Find the closest property type using fuzzy matching
        closest_property_type = process.extractOne(s_normalized, normalized_property_types.keys())

        if not closest_property_type:
            continue
        type_id = normalized_property_types[closest_property_type[0]]
        results.append(str(type_id))

    return results


def save_to_excel(results, filename="output.xlsx"):
  wb = Workbook()
  ws = wb.active

  headers = results[0].keys()
  ws.append(list(headers))

  for entry in results:
      ws.append(list(entry.values()))     

  wb.save(filename)
  

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

import requests
import os

API_KEY = os.environ["TRELLO_API_KEY"] = os.getenv("TRELLO_API_KEY")
TOKEN = os.environ["TRELLO_TOKEN"] = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.environ["TRELLO_BOARD_ID"] = os.getenv("TRELLO_BOARD_ID")

def get_lists():

  url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"

  querystring = {"key":API_KEY,"token":TOKEN}

  response = requests.request("GET", url, params=querystring)

  return response.json()

def create_a_card(list_id, name, description):

  url = "https://api.trello.com/1/cards"

  query = {
    'idList': list_id,
    'key': API_KEY,
    'token': TOKEN,
    "name": name,
    "desc": description
  }

  response = requests.request(
    "POST",
    url,
    params=query
  )
  
  return response.json()

def create_attachment(card_id, filename):

  url = f"https://api.trello.com/1/cards/{card_id}/attachments"
  files = {'file': open(filename, 'rb')}

  querystring = {"key":API_KEY,"token":TOKEN}

  response = requests.request(
    "POST",
    url,
    params=querystring,
    files=files
  )
