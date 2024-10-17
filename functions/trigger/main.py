import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Input:
    full_name: str
    email: str
    birth_date: str
    phone_number: str
    property_type: str
    state_of_interest: str
    city_of_interest: str
    top_neighborhoods: list
    investment_amount: int
    payment_methods: list


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    sns_client = boto3.client("sns")

    dynamodb = boto3.resource("dynamodb")
    table_name = "Clientes"
    table = dynamodb.Table(table_name)

    body = json.loads(event["body"])
    personal_info = body["personal_information"]
    property_info = body["property_information"]

    unique_id = f"{personal_info['cpf_cnpj']}-{property_info['property_city']}-{property_info['property_type']}"

    table.put_item(
        Item={
            "PK": unique_id,
            "personal_information": personal_info,
            "property_information": property_info,
        }
    )

    TOPIC_ARN = os.environ["TOPIC_ARN"]
    response = sns_client.publish(TopicArn=TOPIC_ARN, Message=event["body"])

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "success!"}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }


# class PersonalInformation:
#     full_name: str
#     cpf_cnpj: str
#     email: str
#     phone_number: str
#     address: str
#     profession: str
#     state: str
#     city: str
#     country: str
#     property_purpose: str
#     auction_experience: str
#     auction_question: str


event = {
    "body": json.dumps(
        {
            "personal_information": {
                "full_name": "John Doe",
                "cpf_cnpj": "12345678900",
                "email": "jhon@example.com",
                "phone_number": "123456789",
                "address": "Rua A, 123",
                "profession": "Developer",
                "state": "SP",
                "city": "São Paulo",
                "country": "Brazil",
                "property_purpose": "residence",
                "auction_experience": "no",
                "auction_question": "none",
            },
            "property_information": {
                "property_type": "apartment",
                "property_state": "SP",
                "property_city": "São Paulo",
                "property_neighborhood": ["Vila Mariana"],
                "budget": 500000,
                "payment_method": ["financing"],
            },
        }
    )
}
lambda_handler(event, {})
