import json
from dataclasses import dataclass
import excel
from clickup import create_client, PersonalInformation, PropertyInformation

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


def lambda_handler(event, context):  # sourcery skip: avoid-builtin-shadow


    body = json.loads(event["body"])

    excel.update_clients_spreadsheet(body)

    client = PersonalInformation(
        full_name=body["personal_information"]["full_name"],
        cpf_cnpj=body["personal_information"]["cpf_cnpj"],
        email=body["personal_information"]["email"],
        phone_number=body["personal_information"]["phone_number"],
        address=body["personal_information"]["address"],
        profession=body["personal_information"]["profession"],
        state=body["personal_information"]["state"],
        city=body["personal_information"]["city"],
        country=body["personal_information"]["country"],
        property_purpose=body["personal_information"]["property_purpose"],
        auction_experience=body["personal_information"]["auction_experience"],
        auction_question=body["personal_information"]["auction_question"],
    )

    property = PropertyInformation(
        property_type=body["property_information"]["property_type"],
        property_state=body["property_information"]["property_state"],
        property_city=body["property_information"]["property_city"],
        property_neighborhood=body["property_information"]["property_neighborhood"],
        budget=body["property_information"]["budget"],
        payment_method=body["property_information"]["payment_method"],
    )

    create_client(client, property)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "success!"}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }





# event = {
#     "body": json.dumps(
#         {
#             "personal_information": {
#                 "full_name": "John Doe",
#                 "cpf_cnpj": "12345678900",
#                 "email": "jhon@example.com",
#                 "phone_number": "123456789",
#                 "address": "Rua A, 123",
#                 "profession": "Developer",
#                 "state": "SP",
#                 "city": "São Paulo",
#                 "country": "Brazil",
#                 "property_purpose": "residence",
#                 "auction_experience": "no",
#                 "auction_question": None,
#             },
#             "property_information": {
#                 "property_type": "apartment",
#                 "property_state": "SP",
#                 "property_city": "São Paulo",
#                 "property_neighborhood": ["Vila Mariana"],
#                 "budget": 500000,
#                 "payment_method": "financing",
#             },
#         }
#     )
# }
# lambda_handler(event, {})
