import json
import os
from dataclasses import dataclass
import excel
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


    body = json.loads(event["body"])

    excel.update_clients_spreadsheet(body)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "success!"}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }





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
