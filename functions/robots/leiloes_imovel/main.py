import excel
import requests
import string_utils
# from . import utils
import utils
from bs4 import BeautifulSoup



def lambda_handler(event, context):

    clients = excel.get_clients()

    for client in clients:
        print(client["Nome Completo:"])
        property_types = utils.find_property_types(client["Tipo de imóvel:"])
        state_of_interest = string_utils.find_state_based_on_state_of_interest(client["Estado de interesse:"])
        city_of_interest = f"{client['Cidade de interesse:']}/{state_of_interest['abbreviation']}"
        city = utils.find_most_probable_city(city_of_interest)
        if not city:
            continue

        district_codes = utils.find_district_codes(client["Bairros de interesse:"], city)
        if not district_codes:
            continue

        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&tipo={property_types}&cidade={city}&bairro={district_codes}"
        response = requests.get(url)


        soup = BeautifulSoup(response.text, "html.parser")

        try:
            total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
        except:
            continue
        number_of_pages = (total_results // 20) + 1

        for page in range(1, number_of_pages + 1):
            url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&tipo={property_types}&cidade={city}&pag={page}&bairro={district_codes}"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, "html.parser")

            boxes = soup.select("div.place-box")
            for box in boxes:
                auction = utils.get_auction(box, client["Estado de interesse:"])

                excel.update_auctions_spreadsheet(auction, client["Nome Completo:"], url)
                

              
# Test locally (optional)
if __name__ == "__main__":
    lambda_handler({}, {})
