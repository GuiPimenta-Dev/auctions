import json
import os
import requests
import string_utils
import clickup
from bs4 import BeautifulSoup
import utils
import boto3
from pprint import pprint
import uuid
import datetime

# Initialize AWS SQS client
sqs = boto3.client('sqs')

def lambda_handler(event, context):

    SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

    # DynamoDB setup to get client data
    dynamodb = boto3.resource('dynamodb')
    clients_table = dynamodb.Table('Clientes')

    response = clients_table.scan()
    items = response.get('Items', [])

    for item in items:
        personal_info = item['personal_information']
        property_info = item['property_information']

        property_type = property_info.get("property_type")
        state_of_interest = property_info.get("property_state")
        city_of_interest = property_info.get("property_city")
        investment_amount = property_info.get("budget")

        # Convert state_of_interest to full state name
        state_of_interest = string_utils.find_state_based_on_state_of_interest(state_of_interest)
        all_cities = requests.get("https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

        chosen_city = next((city for city in all_cities if city_of_interest in city["name"]), None)
        if not chosen_city:
            print(f"City {city_of_interest} not found in the list of cities.")
            continue  # Skip to the next client

        # Find types of property
        types = utils.find_property_types(property_type.split(","))
        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&tipo={','.join(types)}&preco_min={investment_amount}"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        # Total results and pagination
        total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
        number_of_pages = (total_results // 20) + 1

        for page in range(1, number_of_pages + 1):
            url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&pag={page}&tipo={','.join(types)}&preco_min={investment_amount}"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, "html.parser")

            boxes = soup.select("div.place-box")
            for box in boxes:
                auction = utils.get_auction(box, chosen_city["state"])

                # Prepare the data to send to SQS
                auction_data = {
                    'property_info': property_info,
                    "personal_info": personal_info,
                    "auction": utils.dataclass_to_dict(auction),
                }

                # Send the auction data to the SQS queue
                response = sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps(auction_data)
                )

                # # Optional: Create a task in ClickUp (same as before)
                # card = clickup.Task(
                #     personal_information=clickup.PersonalInformation(**personal_info),
                #     property_information=clickup.PropertyInformation(**property_info),
                #     auction=auction,
                # )
                # clickup.create_task(card)

# Test locally (optional)
if __name__ == "__main__":
    lambda_handler({}, {})
