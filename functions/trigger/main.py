import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Input:
    full_name: str
    email_address: str
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

    TOPIC_ARN = os.environ["TOPIC_ARN"]
    response = sns_client.publish(TopicArn=TOPIC_ARN, Message=event["body"])

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "success!"}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
