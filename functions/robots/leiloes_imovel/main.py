import json
import requests
from bs4 import BeautifulSoup
import utils
import get_location





def lambda_handler(event, context):
    # Pega a cidade ou estado que a Marcela quer fazer a busca
    body = json.loads(event["body"])

    full_name = body.get("full_name")
    property_type = body.get("property_type")
    state_of_interest = body.get("state_of_interest")
    city_of_interest = body.get("city_of_interest")
    top_neighborhoods = body.get("top_neighborhoods")
    investment_amount = body.get("investment_amount")
    payment_methods = body.get("payment_methods")

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


# Sample event to test the lambda function
event = {
    "body": json.dumps(
        {
            "full_name": "Guilherme Pimenta",
            "email_address": "marcela@example.com",
            "birth_date": "1990-01-01",
            "phone_number": "11999999999",
            "property_type": "Apartamento",
            "state_of_interest": "Santa Catarina",
            "city_of_interest": "Balneário Camboriú",
            "top_neighborhoods": ["Centro", "Barra Sul"],
            "investment_amount": 100000,
            "payment_methods": ["Financiamento", "A vista"],
        }
    )
}
lambda_handler(event, {})
