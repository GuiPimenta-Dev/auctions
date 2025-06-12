import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import re
from fuzzywuzzy import process, fuzz
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from oauth2client.service_account import ServiceAccountCredentials
import os
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import pandas as pd
import boto3
from botocore.exceptions import ClientError

@dataclass
class Bid:
    date: Optional[str]
    value: Optional[str]

@dataclass
class Bids:
    first_bid: Bid
    second_bid: Bid

@dataclass
class Auction:
    name: str
    type_: Optional[str]
    modality: Optional[str]
    state: str
    city: str
    address: str
    district: Optional[str]
    appraised_value: str
    discount_value: str
    m2: Optional[str]
    bedrooms: Optional[str]
    parking: Optional[str]
    image: str
    url: str
    files: List[Dict[str, str]]
    general_info: List[Dict[str, str]]
    bids: Bids

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type_,
            "modality": self.modality,
            "state": self.state,
            "city": self.city,
            "address": self.address,
            "district": self.district,
            "appraised_value": self.appraised_value,
            "discount_value": self.discount_value,
            "m2": self.m2,
            "bedrooms": self.bedrooms,
            "parking": self.parking,
            "image": self.image,
            "url": self.url,
            "files": self.files,
            "general_info": self.general_info,
            "bids": {
                "first_bid": {
                    "date": self.bids.first_bid.date,
                    "value": self.bids.first_bid.value
                },
                "second_bid": {
                    "date": self.bids.second_bid.date,
                    "value": self.bids.second_bid.value
                }
            }
        }

class GoogleSheetsClient:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open(".Imóveis")
        self.worksheet = self.spreadsheet.worksheet("Clientes")

    def _get_credentials(self):
        # Initialize AWS Secrets Manager
        secrets_manager = boto3.client('secretsmanager')

        # Fetch Google credentials from Secrets Manager
        def get_google_credentials(secret_name):
            response = secrets_manager.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            return json.loads(secret_string)  # Assuming the secret is stored as a JSON string

        # Authenticate with Google service account using credentials from Secrets Manager
        secret_name = 'GoogleSheets'  # Replace with your secret name in Secrets Manager
        google_creds = get_google_credentials(secret_name)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds)
        return creds
      
    def get_clients(self) -> List[Dict[str, str]]:
        data = self.worksheet.get_all_records()
        return data

    def update_auctions_spreadsheet(self, auction: Auction, client_name: str, search_url: str):
        # Get or create the Auctions worksheet
        try:
            auctions_worksheet = self.spreadsheet.worksheet("Leilões")
        except gspread.exceptions.WorksheetNotFound:
            auctions_worksheet = self.spreadsheet.add_worksheet(
                title="Leilões",
                rows=1000,
                cols=20
            )
            # Add headers
            headers = [
                "Nome do Cliente",
                "Nome do Imóvel",
                "Tipo",
                "Modalidade",
                "Estado",
                "Cidade",
                "Endereço",
                "Bairro",
                "Valor de Avaliação",
                "Valor com Desconto",
                "Área (m²)",
                "Quartos",
                "Vagas",
                "URL da Imagem",
                "URL do Imóvel",
                "URL da Busca",
                "Data do Leilão",
                "Valor do Leilão",
                "Data da Segunda Proposta",
                "Valor da Segunda Proposta"
            ]
            auctions_worksheet.append_row(headers)

        # Prepare row data
        row_data = [
            client_name,
            auction.name,
            auction.type_ or "-",
            auction.modality or "-",
            auction.state,
            auction.city,
            auction.address,
            auction.district or "-",
            auction.appraised_value,
            auction.discount_value,
            auction.m2 or "-",
            auction.bedrooms or "-",
            auction.parking or "-",
            auction.image,
            auction.url,
            search_url,
            auction.bids.first_bid.date or "-",
            auction.bids.first_bid.value or "-",
            auction.bids.second_bid.date or "-",
            auction.bids.second_bid.value or "-"
        ]

        # Check if auction already exists
        existing_data = auctions_worksheet.get_all_records()
        for row in existing_data:
            if row["URL do Imóvel"] == auction.url and row["Nome do Cliente"] == client_name:
                return  # Skip if auction already exists for this client

        # Append new auction
        auctions_worksheet.append_row(row_data)

class LeiloesImovelRobot:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.leilaoimovel.com.br/",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.PROPERTY_TYPES = {
            "agencia": 22,
            "apartamento": 2,
            "area_industrial": 16,
            "area_rural": 5,
            "casa": 1,
            "comercial": 6,
            "galpao": 20,
            "garagem": 13,
            "outros": 11,
            "terreno": 3,
        }
        self.sheets_client = GoogleSheetsClient()

    def find_property_types(self, inputs: str) -> str:
        results = []
        for s in inputs.split(","):
            s_normalized = re.sub(r"\s+", " ", s.strip()).lower()
            normalized_property_types = {
                re.sub(r"\s+", " ", k).lower(): v for k, v in self.PROPERTY_TYPES.items()
            }
            closest_property_type = process.extractOne(
                s_normalized, normalized_property_types.keys()
            )
            if not closest_property_type:
                continue
            type_id = normalized_property_types[closest_property_type[0]]
            results.append(str(type_id))
        return ",".join(results)

    def find_most_probable_city(self, city_name: str) -> Optional[str]:
        print(f"[DEBUG] Input city_name: '{city_name}'")
        response = self.scraper.get("https://www.leilaoimovel.com.br/getAllCities", headers=self.headers)
        
        if "cf-chl-bypass" in response.text.lower() or "Cloudflare" in response.text or "/cdn-cgi/" in response.text:
            print("[WARNING] Detected Cloudflare challenge or bot protection.")
            return None

        try:
            all_cities = response.json().get("locations", [])
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return None

        if not city_name or not city_name.strip():
            print("[WARN] Empty city_name provided, skipping matching.")
            return None

        name_list = [entry['name'] for entry in all_cities]
        best_match = process.extractOne(city_name.strip(), name_list, scorer=fuzz.ratio)

        if best_match:
            print(f"[DEBUG] Best match: {best_match}")
            matched_entry = next(entry for entry in all_cities if entry['name'] == best_match[0])
            return matched_entry["id"]

        print("[INFO] No city match found.")
        return None

    def find_district_codes(self, client_districts: str, city: str) -> Optional[str]:
        response = self.scraper.get(f"https://www.leilaoimovel.com.br/getAreas?list={city}", headers=self.headers)

        try:
            areas = response.json()["areas"]
            client_districts = [district.strip() for district in client_districts.split(",")]

            districts = []
            for area in areas:
                _, score = process.extractOne(area["name"], client_districts)
                if score >= 95:
                    districts.append(str(area["id"]))
            return ",".join(districts)

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_auction(self, box, client) -> Auction:
        name = self.css_select(box, "div.address p b")
        address = self.css_select(box, "div.address p span")
        image = box.select_one("img").get("src")
        property_url = "https://www.leilaoimovel.com.br" + box.select_one("a").get("href")

        response = self.scraper.get(property_url)
        soup = BeautifulSoup(response.text, "html.parser")

        city = self.css_select(soup, "nav#breadcrumb li:nth-child(4) span")
        m2 = self.get_details(soup, "Área Útil")
        bedrooms = self.get_details(soup, "Quartos")
        parking = self.get_details(soup, "Vagas")
        appraised_value = self.css_select(soup, "div.appraised h2")
        discount_value = self.css_select(soup, "h2.discount-price")
        bids = self.extract_bid(self.css_select(soup, "div.bids"))
        district = self.find_district(soup, client, address)
        general_info = self.get_general_info(soup)

        type_modality = next(
            (i["text"] for i in general_info if i["title"] == "Tipo:"), None
        )
        try:
            type_ = type_modality.split("/")[0].strip()
            modality = type_modality.split("/")[-1].strip()
        except:
            type_ = None
            modality = None

        files = self.get_files(soup)

        return Auction(
            name=name,
            type_=type_,
            modality=modality,
            state=client["Estado de interesse:"],
            city=city,
            address=address,
            district=district,
            appraised_value=appraised_value,
            discount_value=discount_value,
            m2=m2,
            bedrooms=bedrooms,
            parking=parking,
            image=image,
            url=property_url,
            files=files,
            general_info=general_info,
            bids=bids
        )

    def css_select(self, element, selector: str) -> str:
        found = element.select_one(selector)
        return found.get_text(strip=True) if found else "-"

    def css_select_list(self, element, selector: str) -> List[str]:
        return [e.get_text(strip=True) for e in element.select(selector)]

    def extract_bid(self, input_string: str) -> Bids:
        date_pattern = r"(\d{2}/\d{2}/\d{4} às \d{2}:\d{2})"
        value_pattern = r"R\$ ([\d.,]+)"

        dates = re.findall(date_pattern, input_string)
        values = re.findall(value_pattern, input_string)
        date_objs = [datetime.strptime(date, '%d/%m/%Y às %H:%M') for date in dates]

        result = {
            'first_date': date_objs[0].strftime('%d/%m/%Y %H:%M') if date_objs else None,
            'first_value': values[0] if values else None,
            'second_date': date_objs[1].strftime('%d/%m/%Y %H:%M') if len(date_objs) > 1 else None,
            'second_value': values[1] if len(values) > 1 else None
        }

        return Bids(
            first_bid=Bid(date=result['first_date'], value=result['first_value']),
            second_bid=Bid(date=result['second_date'], value=result['second_value'])
        )

    def get_general_info(self, soup) -> List[Dict[str, str]]:
        general_info = soup.select('div.more.row.pb-2 div')
        info = []
        for i in general_info:
            title = "".join(self.css_select_list(i, "b"))
            text = "".join(self.css_select_list(i, "*")).replace("\n", "").replace(f"{title}", "").strip()
            if text:
                info.append({"title": title, "text": text})
        return info

    def get_files(self, soup) -> List[Dict[str, str]]:
        general_files = soup.select("div.documments.row.pb-4 a")
        files = []
        for i in general_files:
            title = self.css_select(i, "span")
            link = i.get("href", "").strip()
            if title and link:
                files.append({"title": title, "link": link})
        return files

    def get_details(self, soup, wanted: str) -> Optional[str]:
        details = self.css_select_list(soup, "div.detail")
        for detail in details:
            if wanted in detail:
                return detail.split(":")[-1].strip()
        return None

    def find_district(self, soup, client, address: str) -> Optional[str]:
        neighborhoods_of_interest = client["Bairros de interesse:"].split(",")
        for neighborhood in neighborhoods_of_interest:
            if fuzz.partial_ratio(neighborhood.strip().lower(), address.lower()) >= 90:
                return neighborhood.strip().title()
        return None

    def run(self):
        clients = self.sheets_client.get_clients()
        for client in clients:
            property_types = self.find_property_types(client["Tipo de imóvel:"])
            state_of_interest = client["Estado de interesse:"]
            city_of_interest = f"{client['Cidade de interesse:']}/{state_of_interest}"
            city = self.find_most_probable_city(city_of_interest)
            if not city:
                continue

            district_codes = self.find_district_codes(client["Bairros de interesse:"], city)
            if not district_codes:
                continue

            try:
                budget = float(client["Valor de orçamento destinado ao investimento:"].replace(".", "").replace(",", "."))
                budget = str(budget * 100).replace(".", "").replace(",", "")
            except:
                continue

            url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&tipo={property_types}&cidade={city}&bairro={district_codes}&preco_max={budget}"
            print(url)
            response = self.scraper.get(url)

            soup = BeautifulSoup(response.text, "html.parser")

            try:
                total_results = int(soup.select_one("span.count-places").get_text().strip().split("Imóveis")[0])
            except:
                continue

            number_of_pages = (total_results // 20) + 1

            for page in range(1, number_of_pages + 1):
                url = f"https://www.leilaoimovel.com.br/encontre-seu-imovel?s=&tipo={property_types}&cidade={city}&pag={page}&bairro={district_codes}&preco_max={budget}"
                response = self.scraper.get(url)
                soup = BeautifulSoup(response.text, "html.parser")

                boxes = soup.select("div.place-box")
                for box in boxes:
                    auction = self.get_auction(box, client)
                    print(auction)

                    if auction.url == "https://www.leilaoimovel.com.br/imoveis-springfield":
                        continue
                    self.sheets_client.update_auctions_spreadsheet(auction, client["Nome Completo:"], url)

def lambda_handler(event, context):
    robot = LeiloesImovelRobot()
    robot.run()

if __name__ == "__main__":
    lambda_handler({}, {}) 