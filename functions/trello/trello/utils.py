import requests
import os

API_KEY = os.environ["TRELLO_API_KEY"] = os.getenv("TRELLO_API_KEY")
TOKEN = os.environ["TRELLO_TOKEN"] = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.environ["TRELLO_BOARD_ID"] = os.getenv("TRELLO_BOARD_ID")


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
