import json

import requests
import string_utils
import trello
from bs4 import BeautifulSoup

from . import utils


def lambda_handler(event, context):

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    property_type = message["property_information"].get("property_type")
    state_of_interest = message["property_information"].get("property_state")
    city_of_interest = message["property_information"].get("property_city")
    top_neighborhoods = message["property_information"].get("property_neighborhood")
    investment_amount = message["property_information"].get("budget")
    payment_methods = message["property_information"].get("payment_methods")

    state_of_interest = string_utils.find_state_based_on_state_of_interest(state_of_interest)
    all_cities = requests.get("https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

    chosen_city = next((city for city in all_cities if city_of_interest in city["name"]), None)

    types = utils.find_property_types(property_type.split(","))
    url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&tipo={','.join(types)}&preco_min={investment_amount}"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
    number_of_pages = (total_results // 20) + 1

    for page in range(1, number_of_pages + 1):
        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&pag={page}&tipo={','.join(types)}&preco_min={investment_amount}"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        boxes = soup.select("div.place-box")
        for box in boxes:
            price = utils.css_select(box, 'span.last-price')
            discount = utils.css_select(box, 'span.discount-price.font-1')
            name = utils.css_select(box, "div.address p b")
            address = utils.css_select(box, "div.address p span")
            image = box.select_one("img").get("src")
            property_url = "https://www.leilaoimovel.com.br" + box.select_one("a").get("href")

            response = requests.get(property_url)
            soup = BeautifulSoup(response.text, "html.parser")

            general_info = utils.get_general_info(soup)
            files = utils.get_files(soup)

            property_details = {
                "price": price,
                "discount": discount,
                "name": name,
                "address": address,
                "general_info": general_info,
                "files": files,
                "url": property_url,
            }

            card = trello.Card(
                property_details=trello.PropertyDetails(**property_details),
                cover=image,
            )

            trello.create_card(card)

