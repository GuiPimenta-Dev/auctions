import json

import get_location
import requests
from bs4 import BeautifulSoup

from . import utils


def lambda_handler(event, context):

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    full_name = message.get("full_name")
    property_type = message.get("property_type")
    state_of_interest = message.get("state_of_interest")
    city_of_interest = message.get("city_of_interest")
    top_neighborhoods = message.get("top_neighborhoods")
    investment_amount = message.get("investment_amount")
    payment_methods = message.get("payment_methods")

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

            card_title = f"""Cliente: {full_name}
Tipo de imóvel: {property_type}
Cidade: {city_of_interest}
Estado: {state_of_interest['state']}
Bairro: {', '.join(top_neighborhoods)}
Valor de Investimento: {investment_amount}
Formas de pagamento: {', '.join(payment_methods)}
"""

            lists = utils.get_lists()
            first_list = lists[0]

            card_description = utils.create_card_description(
                price, discount, name, address, image, property_url, general_info, files
            )
            card = utils.create_a_card(first_list["id"], card_title, card_description)
            utils.set_cover(card["id"], image)

