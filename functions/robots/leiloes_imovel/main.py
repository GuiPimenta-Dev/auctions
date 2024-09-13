import json
import requests
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
from utils import xpath, xpath_list, save_to_excel, get_lists, create_a_card, create_attachment

LOCATION = "Campo Grande"
SLUG = LOCATION.lower().replace(" ", "_")

def lambda_handler(event, context):
    # Pega a cidade ou estado que a Marcela quer fazer a busca
    body = json.loads(event["body"])
    location = body["location"]

    # Pega todas as cidades disponiveis no site, pois precisamos do id e nao do nome
    all_cities = requests.request("GET", "https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

    # Pega todas os estados disponiveis no site, pois precisamos do id e nao do nome
    all_states = requests.request("GET", "https://www.leilaoimovel.com.br/getAllStates").json()["locations"]
    
    locations = []
    
    for city in all_cities:
        # Caso a cidade esteja entre o que a Marcela busca inserimos na lista de locais
        if location in city["name"]:
            locations.append(city)
    
    for state in all_states:
        # Caso o estado esteja entre o que a Marcela busca inserimos na lista de locais
        if location in state["name"]:
            locations.append(state)
    
    results = []
    for location in locations:
        # Pega o numero de paginas que temos que percorrer
        number_of_pages = (location["qty"] // 20) + 1
        
        # Create a progress bar for pages
        with tqdm(total=number_of_pages, desc=f"Coletando Dados de {location['name']}") as page_progress_bar:
            for page in range(1, number_of_pages + 1):
                # Faz a request para a pagina de busca 
                response = requests.request("GET", f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={location['id']}&pag={page}")
                
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
                
                # Update the page progress bar
                page_progress_bar.update(1)
    
    save_to_excel(results, filename=f"{SLUG}.xlsx")
    lists = get_lists()
    first_list = lists[0]
    card = create_a_card(first_list["id"], LOCATION, f"Imoveis em {LOCATION}")
    attachment = create_attachment(card["id"], f"{SLUG}.xlsx")
    
event = {
    "body": json.dumps({"location": LOCATION})
}
lambda_handler(event, {})
