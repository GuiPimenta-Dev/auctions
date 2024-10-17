import json
import requests
import string_utils
import clickup
from bs4 import BeautifulSoup
import utils
import boto3  
from pprint import pprint
import uuid
import datetime

dynamodb = boto3.resource('dynamodb')
clients_table_name = 'Clientes'  
clients_table = dynamodb.Table(clients_table_name)

properties_table_name = 'Properties'  
property_table = dynamodb.Table(properties_table_name)

def lambda_handler(event, context):

    response = clients_table.scan()
    items = response.get('Items', [])

    for item in items:
        personal_info = item['personal_information']
        property_info = item['property_information']

        property_type = property_info.get("property_type")
        state_of_interest = property_info.get("property_state")
        city_of_interest = property_info.get("property_city")
        investment_amount = property_info.get("budget")

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
                auction = utils.get_auction(box, chosen_city["state"])
                current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
                unique_id = str(uuid.uuid4())

                property_table.put_item(
                    Item={
                        'PK': current_date,  
                        'SK': unique_id,  
                        'property_info': property_info,
                        "personal_info": personal_info,
                        "auction": utils.dataclass_to_dict(auction),
                    }
                )


                card = clickup.Task(
                    personal_information=clickup.PersonalInformation(**personal_info),
                    property_information=clickup.PropertyInformation(**property_info),
                    auction=auction,
                )

                clickup.create_task(card)
lambda_handler({}, {})