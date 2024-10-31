import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import requests
from auction import Auction, Bid, Bids
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from geopy.geocoders import Photon
from tenacity import retry, stop_after_attempt, wait_fixed

# Dictionary with property types and their IDs
PROPERTY_TYPES = {
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

def find_property_types(inputs: list) -> list:
    results = []

    for s in inputs.split(","):
        # Normalize the input string
        s_normalized = re.sub(r"\s+", " ", s.strip()).lower()

        # Normalize the dictionary keys
        normalized_property_types = {
            re.sub(r"\s+", " ", k).lower(): v for k, v in PROPERTY_TYPES.items()
        }

        # Find the closest property type using fuzzy matching
        closest_property_type = process.extractOne(
            s_normalized, normalized_property_types.keys()
        )

        if not closest_property_type:
            continue
        type_id = normalized_property_types[closest_property_type[0]]
        results.append(str(type_id))

    return ",".join(results)

from fuzzywuzzy import fuzz, process


def find_most_probable_city(city_name):
    all_cities = requests.get("https://www.leilaoimovel.com.br/getAllCities").json()["locations"]

    # Create a list of all names from the data array for fuzzy matching
    name_list = [entry['name'] for entry in all_cities]
    
    # Use process.extractOne to find the best match
    best_match = process.extractOne(city_name, name_list, scorer=fuzz.ratio)
    
    if best_match:
        # Find the corresponding entry in data
        matched_entry = next(entry for entry in all_cities if entry['name'] == best_match[0])
        return matched_entry["id"]
    return None

def get_auction(box, state):
    name = css_select(box, "div.address p b")
    address = css_select(box, "div.address p span")
    image = box.select_one("img").get("src")
    property_url = "https://www.leilaoimovel.com.br" + box.select_one("a").get("href")

    response = requests.get(property_url)
    soup = BeautifulSoup(response.text, "html.parser")

    city = css_select(soup, "nav#breadcrumb li:nth-child(4) span")
    m2 = get_details(soup, "Área Útil")
    bedrooms = get_details(soup, "Quartos")
    parking = get_details(soup, "Vagas")
    appraised_value = css_select(soup, "div.appraised h2")
    discount_value = css_select(soup, "h2.discount-price")
    bids = extract_bid(css_select(soup, "div.bids"))
    district = find_district(soup)
    general_info = get_general_info(soup)
    type_modality = next(
        (i["text"] for i in general_info if i["title"] == "Tipo:"), None
    )
    try:
        type_ = type_modality.split("/")[0].strip()
        modality = type_modality.split("/")[-1].strip()
    except:
        type_ = None
        modality = None
    files = get_files(soup)
    auction = Auction(
        name=name,
        type_=type_,
        modality=modality,
        state=state,
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
    return auction

def css_select(element, selector):
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else "-"

def css_select_list(element, selector):
    return [e.get_text(strip=True) for e in element.select(selector)]


def extract_bid(input_string):
    # Define regex patterns to match dates/times and values
    date_pattern = r"(\d{2}/\d{2}/\d{4} às \d{2}:\d{2})"
    value_pattern = r"R\$ ([\d.,]+)"
    
    # Find all date and value matches
    dates = re.findall(date_pattern, input_string)
    values = re.findall(value_pattern, input_string)

    # Convert the date strings to datetime objects (optional)
    date_objs = [datetime.strptime(date, '%d/%m/%Y às %H:%M') for date in dates]

    # Prepare the dictionary with dates and values
    result = {
        'first_date': date_objs[0].strftime('%d/%m/%Y %H:%M') if date_objs else None,
        'first_value': values[0] if values else None,
        'second_date': date_objs[1].strftime('%d/%m/%Y %H:%M') if len(date_objs) > 1 else None,
        'second_value': values[1] if len(values) > 1 else None
    }
    first_bid = Bid(date=result['first_date'], value=result['first_value'])
    second_bid = Bid(date=result['second_date'], value=result['second_value'])
    return Bids(first_bid=first_bid, second_bid=second_bid)

def get_general_info(soup):
    general_info = soup.select('div.more.row.pb-2 div')
    info = []
    for i in general_info:
        title = "".join(css_select_list(i, "b"))
        text = "".join(css_select_list(i, "*")).replace("\n", "").replace(f"{title}", "").strip()
        if text:
            info.append({"title": title, "text": text})
    return info


def get_files(soup):
    general_files = soup.select("div.documments.row.pb-4 a")
    files = []
    for i in general_files:
        title = css_select(i, "span")
        link = i.get("href", "").strip()
        if title and link:
            files.append({"title": title, "link": link})
    return files

def find_district_codes(client_districts, city):
    districts = []
    response = requests.get(f"https://www.leilaoimovel.com.br/getAreas?list={city}")
    
    try:
        areas = response.json()["areas"]
        client_districts = client_districts.split(",")  # Convert to list

        for area in areas:
            # Use fuzzy matching to find the best match in client_districts
            _, score = process.extractOne(area["name"], client_districts)
            
            # Set a threshold score (e.g., 80) to accept the match
            if score >= 95:
                districts.append(str(area["id"]))

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return ",".join(districts)
def get_details(soup, wanted):
    details = css_select_list(soup, "div.detail")
    for detail in details:
        if wanted in detail:
            return detail.split(":")[-1].strip()


def format_currency(value):
    sanitized_value = re.sub(r'[^\d,.-]', '', str(value))
    
    sanitized_value = sanitized_value.replace(',', '.')
    
    try:
        return int(float(sanitized_value)) * 100
    except ValueError:
        return value * 100
        


def find_district(soup):

    # Find the iframe element by title
    iframe_element = soup.find('iframe', title='geolocalização')

    # Extract the src attribute
    if iframe_element:
        iframe_src = iframe_element.get('src')
        
        # Parse the URL to extract latitude and longitude
        parsed_url = urlparse(iframe_src)
        query_params = parse_qs(parsed_url.query)
        
        # Extract latitude and longitude from the query parameters
        if 'q' in query_params:
            coordinates = query_params['q'][0]  # Get the first coordinate value
            latitude, longitude = coordinates.split(',')
            geolocator = Photon(user_agent="measurements")
            
            try:
                location = geolocator.reverse((latitude, longitude), exactly_one=True)
                neighborhood = location.raw["properties"].get("district") or location.raw["properties"].get("name")
                return neighborhood
            except:
                return None
          
    


def format_currency(value):
    numeric_value = re.sub(r'\D', '', str(value))
    try:
        # Converte para inteiro
        return int(numeric_value)
    except ValueError:
        # Se não for possível converter, retorna o valor original
        return value