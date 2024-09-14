import json

import get_location
import requests
from bs4 import BeautifulSoup
from . import utils


def lambda_handler(event, context):

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    property_type = message["property_information"].get("property_type")
    state_of_interest = message["property_information"].get("state_of_interest")
    city_of_interest = message["property_information"].get("city_of_interest")
    top_neighborhoods = message["property_information"].get("top_neighborhoods")
    investment_amount = message["property_information"].get("investment_amount")
    payment_methods = message["property_information"].get("payment_methods")

    personal_information = message["personal_information"]

    state_of_interest = get_location.find_state(state_of_interest)
    all_cities = requests.get("https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

    chosen_city = next((city for city in all_cities if city_of_interest in city["name"]), None)

    types = utils.find_property_types(property_type.split(","))
    url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&tipo={','.join(types)}&preco_min={investment_amount}"
    response = requests.get(url)

    # Faz o parse do html para podermos pegar os dados
    soup = BeautifulSoup(response.text, "html.parser")

    # Pega o numero de paginas que temos que percorrer
    total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
    number_of_pages = (total_results // 20) + 1

    for page in range(1, number_of_pages + 1):
        # Faz a request para a pagina de busca
        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&pag={page}&tipo={','.join(types)}&preco_min={investment_amount}"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        # Pega todos os boxes de imoveis
        boxes = soup.select("div.place-box")
        for box in boxes:
            # Pega o preço, nome, endereço e url do imovel
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

            # card_titile should be each key of personal_information : value
            card_title = f"""
Informações do Cliente:
Cliente: {personal_information['full_name']}
RG: {personal_information['rg']}
CPF: {personal_information['cpf']}
Telefone: {personal_information['phone_number']}
Email: {personal_information['email_address']}
Profissão: {personal_information['profession']}
Endereço: {personal_information['address']}

Informações do Imóvel Desejado:
Tipo de imóvel: {property_type}
Cidade: {city_of_interest}
Estado: {state_of_interest['state']}
Bairro: {top_neighborhoods}
Valor de Investimento: {investment_amount}
Formas de pagamento: {payment_methods}
"""

            lists = utils.get_lists()
            first_list = lists[0]

            card_description = utils.create_card_description(
                price, discount, name, address, image, property_url, general_info, files
            )
            card = utils.create_a_card(first_list["id"], card_title, card_description)
            utils.set_cover(card["id"], image)
