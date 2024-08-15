import json
import requests
from bs4 import BeautifulSoup
from lxml import etree


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
        for page in range(1, number_of_pages + 1):
            
            # Faz a request para a pagina de busca 
            response = requests.request("GET", f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&cidade={location['id']}&pag={page}")
            
            # Faz o parse do html para podermos pegar os dados
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Faz o parse do html para podermos pegar os dados utilizando Xpath visto que BS4 nao tem suporte nativo para Xpath
            # Isso é questão de conforto, poderiamos usar a forma nativa do beautifulsoup tambem
            dom = etree.HTML(str(soup))
            
            # Pega todos os boxes de imoveis
            boxes = dom.xpath("//div[@class='place-box']")
            for box in boxes:
                try:
                    # Pega o preço, nome, endereço e url do imovel
                    price = box.xpath(".//span[@class='discount-price font-1']/text()")[0].strip()
                    name = box.xpath(".//div[@class='address']//p/b/text()")[0].strip()
                    address = box.xpath(".//div[@class='address']//p/span/text()")[0].strip()
                    url = "https://www.leilaoimovel.com.br" + box.xpath(".//a/@href")[0].strip()
                    
                    # Adiciona os dados na lista de resultados
                    results.append(
                        {
                            "price": price,
                            "name": name,
                            "address": address,
                            "url": url
                        }
                    )
                except:
                    continue

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results}),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }

event = {
    "body": json.dumps({ "location": "Campo Grande" })
}
lambda_handler(event, {})