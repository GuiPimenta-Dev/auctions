import json
import requests
import string_utils
import clickup
from bs4 import BeautifulSoup
import utils
import boto3  # Import Boto3
from pprint import pprint

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = 'Clientes'  # Replace with your actual DynamoDB table name
table = dynamodb.Table(table_name)

def lambda_handler(event, context):

    response = table.scan()
    items = response.get('Items', [])

    for item in items:
        personal_info = item['personal_information']
        property_info = item['property_information']

        property_type = property_info.get("property_type")
        state_of_interest = property_info.get("property_state")
        city_of_interest = property_info.get("property_city")
        top_neighborhoods = property_info.get("property_neighborhood")
        investment_amount = property_info.get("budget")
        payment_methods = property_info.get("payment_methods")

        state_of_interest = string_utils.find_state_based_on_state_of_interest(state_of_interest)
        all_cities = requests.get("https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

        chosen_city = next((city for city in all_cities if city_of_interest in city["name"]), None)
        if not chosen_city:
            print(f"City {city_of_interest} not found in the list of cities.")
            return
            
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

                card = clickup.Task(
                    personal_information=clickup.PersonalInformation(**personal_info),
                    property_information=clickup.PropertyInformation(**property_info),
                    property_details=clickup.PropertyDetails(**property_details),
                    cover=image,
                )

                clickup.create_task(card)
