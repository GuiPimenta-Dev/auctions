import requests
from bs4 import BeautifulSoup
import utils
import excel

def lambda_handler(event, context):

    all_states = utils.get_all_states()


    for state in all_states:
        
        # Find types of property
        url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&estado={state['id']}"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
        number_of_pages = (total_results // 20) + 1

        for page in range(1, number_of_pages + 1):
            url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&estado={state['id']}&pag={page}"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, "html.parser")

            boxes = soup.select("div.place-box")
            for box in boxes:
                auction = utils.get_auction(box, state["state"])

                excel.update_spreadsheet(auction)
                

              
# Test locally (optional)
if __name__ == "__main__":
    lambda_handler({}, {})
