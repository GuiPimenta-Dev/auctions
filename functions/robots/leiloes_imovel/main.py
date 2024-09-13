import json
import requests
from bs4 import BeautifulSoup
from lxml import etree
from utils import xpath, xpath_list, save_to_excel, get_lists, create_a_card, create_attachment, find_property_types
import get_location

PROPERTY_TYPES = {
    "agencia": 22,
    "apartamento": 2,
    "area_industrial": 16,
    "area_rural": 5,
    "casa": 1,
    "comercial": 6,
    "galpao": 20,
    "garagem": 13,
    "outros":  11,
    "terreno": 3
}

def lambda_handler(event, context):
    # Pega a cidade ou estado que a Marcela quer fazer a busca
    body = json.loads(event["body"])
    
    full_name = body.get("full_name")
    email_address = body.get("email_address")
    birth_date = body.get("birth_date")
    phone_number = body.get("phone_number")
    property_type = body.get("property_type")
    state_of_interest = body.get("state_of_interest")
    city_of_interest = body.get("city_of_interest")
    top_neighborhoods = body.get("top_neighborhoods")
    investment_amount = body.get("investment_amount")
    payment_methods = body.get("payment_methods")

    state_of_interest = get_location.find_state(state_of_interest)
    all_cities = requests.request("GET", "https://www.leilaoimovel.com.br/getAllCities").json()["locations"]
    all_states = requests.request("GET", "https://www.leilaoimovel.com.br/getAllStates").json()["locations"]
    
    locations = []
    chosen_city = None
    
    for city in all_cities:
        # Caso a cidade esteja entre o que a Marcela busca inserimos na lista de locais
        if city_of_interest in city["name"]:
            chosen_city = city
            break
    
    results = []

    types = find_property_types(property_type.split(","))
    url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&tipo={','.join(types)}&preco_min={investment_amount}"
    response = requests.request("GET", url)

    # Faz o parse do html para podermos pegar os dados
    soup = BeautifulSoup(response.text, 'html.parser')
    
    dom = etree.HTML(str(soup))
    # Pega o numero de paginas que temos que percorrer
    total_results = int(dom.xpath("//span[@class='count-places']/text()")[0].strip().split("Imóveis")[0].strip())
    number_of_pages = (total_results // 20) + 1
    
    for page in range(1, number_of_pages + 1):
        # Faz a request para a pagina de busca 
        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={chosen_city['id']}&pag={page}&tipo={','.join(types)}&preco_min={investment_amount}"
        response = requests.request("GET", url)
        
        # Faz o parse do html para podermos pegar os dados
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Faz o parse do html para podermos pegar os dados utilizando Xpath visto que BS4 nao tem suporte nativo para Xpath
        dom = etree.HTML(str(soup))
        # Pega todos os boxes de imoveis
        boxes = dom.xpath("//div[@class='place-box']")
        for box in boxes:
            # Pega o preço, nome, endereço e url do imovel
            price = xpath(box, './/span[@class="last-price"]/text()')
            discount = xpath(box, './/span[@class="discount-price font-1"]/text()')
            name = xpath(box, ".//div[@class='address']//p/b/text()")
            address = xpath(box, ".//div[@class='address']//p/span/text()")
            url = "https://www.leilaoimovel.com.br" + xpath(box, ".//a/@href")
            response = requests.get(url)
            
            soup = BeautifulSoup(response.text, 'html.parser')

            dom = etree.HTML(str(soup))
            
            place = "".join(xpath_list(dom, '//div[@class="more row pb-2"]//div[1]//a/text()'))
            type_ = "".join(xpath_list(dom, '//div[@class="more row pb-2"]//div[3]//a/text()'))
            bank = xpath(dom, '//div[@class="more row pb-2"]//div[4]//a/text()')
            description = "".join(xpath_list(dom, '//div[@class="more row pb-2"]//div[12]/text()'))
            
            results.append(
                {
                    "price": price,
                    "name": name,
                    "address": address,
                    "url": url,
                    "discount": discount,
                    "place": place,
                    "type": type_,
                    "bank": bank,
                    "description": description
                }
            )
    
    card_title = f"{full_name.title()} - {city_of_interest.title()}"
    save_to_excel(results, filename=f"{card_title}.xlsx")
    lists = get_lists()
    first_list = lists[0]
    for result in results:
        card_description = f"""
        Preço: {result["price"]}

        Desconto: {result["discount"]}

        Endereço: {result["address"]}

        Local: {result["place"]}

        Tipo: {result["type"]}

        Banco: {result["bank"]}

        Descrição: {result["description"]}

        URL: {result["url"]}

        """
        card = create_a_card(first_list["id"], card_title, card_description)
    
event = {
    "body": json.dumps({
        "full_name": "Marcela",
        "email_address": "marcela@example.com",
        "birth_date": "1990-01-01",
        "phone_number": "11999999999",
        "property_type": "Apartamento, casa",
        "state_of_interest": "Rio De Janeiro",
        "city_of_interest": "Niterói",
        "top_neighborhoods": ["Ingá"],
        "investment_amount": 100000,
        "payment_methods": ["Financiamento", "A vista"]
    })
}
lambda_handler(event, {})
