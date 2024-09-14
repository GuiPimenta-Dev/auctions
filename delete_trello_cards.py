import os

import requests

API_KEY = os.environ["TRELLO_API_KEY"] = os.getenv("TRELLO_API_KEY")
TOKEN = os.environ["TRELLO_TOKEN"] = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.environ["TRELLO_BOARD_ID"] = os.getenv("TRELLO_BOARD_ID")


def get_lists():

    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"

    querystring = {"key": API_KEY, "token": TOKEN}

    response = requests.request("GET", url, params=querystring)

    return response.json()


def delete_all_cards_in_column():

    lists = get_lists()
    first_list = lists[0]
    get_cards_url = f"https://api.trello.com/1/lists/{first_list['id']}/cards"
    query = {"key": API_KEY, "token": TOKEN}

    response = requests.get(get_cards_url, params=query)

    if response.status_code != 200:
        return f"Failed to retrieve cards from the list: {response.text}"

    cards = response.json()
    if not cards:
        return "No cards found in the list."

    # Step 2: Delete each card
    for card in cards:
        card_id = card["id"]
        delete_card_url = f"https://api.trello.com/1/cards/{card_id}"

        delete_response = requests.delete(delete_card_url, params=query)

        if delete_response.status_code == 200:
            print(f"Deleted card with ID: {card_id}")
        else:
            print(f"Failed to delete card with ID {card_id}: {delete_response.text}")


# Example usage
delete_all_cards_in_column()
