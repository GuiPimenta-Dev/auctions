import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import cloudscraper
from auction import Auction, Bid, Bids
from bs4 import BeautifulSoup
from fuzzywuzzy import process, fuzz
from geopy.geocoders import Photon

# Cria scraper que contorna o Cloudflare
scraper = cloudscraper.create_scraper()

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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.leilaoimovel.com.br/",
    "X-Requested-With": "XMLHttpRequest"
}


def find_property_types(inputs: list) -> list:
    results = []

    for s in inputs.split(","):
        s_normalized = re.sub(r"\s+", " ", s.strip()).lower()
        normalized_property_types = {
            re.sub(r"\s+", " ", k).lower(): v for k, v in PROPERTY_TYPES.items()
        }
        closest_property_type = process.extractOne(
            s_normalized, normalized_property_types.keys()
        )
        if not closest_property_type:
            continue
        type_id = normalized_property_types[closest_property_type[0]]
        results.append(str(type_id))

    return ",".join(results)


def find_most_probable_city(city_name):
    response = scraper.get("https://www.leilaoimovel.com.br/getAllCities", headers=headers)

    all_cities = response.json()["locations"]
    name_list = [entry['name'] for entry in all_cities]
    best_match = process.extractOne(city_name, name_list, scorer=fuzz.ratio)

    if best_match:
        matched_entry = next(entry for entry in all_cities if entry['name'] == best_match[0])
        return matched_entry["id"]

    return None


def get_auction(box, client):
    name = css_select(box, "div.address p b")
    address = css_select(box, "div.address p span")
    image = box.select_one("img").get("src")
    property_url = "https://www.leilaoimovel.com.br" + box.select_one("a").get("href")

    response = scraper.get(property_url)
    soup = BeautifulSoup(response.text, "html.parser")

    city = css_select(soup, "nav#breadcrumb li:nth-child(4) span")
    m2 = get_details(soup, "Área Útil")
    bedrooms = get_details(soup, "Quartos")
    parking = get_details(soup, "Vagas")
    appraised_value = css_select(soup, "div.appraised h2")
    discount_value = css_select(soup, "h2.discount-price")
    bids = extract_bid(css_select(soup, "div.bids"))
    district = find_district(soup, client, address)
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
    return auction


def css_select(element, selector):
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else "-"


def css_select_list(element, selector):
    return [e.get_text(strip=True) for e in element.select(selector)]


def extract_bid(input_string):
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
    response = scraper.get(f"https://www.leilaoimovel.com.br/getAreas?list={city}", headers=headers)

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


def get_details(soup, wanted):
    details = css_select_list(soup, "div.detail")
    for detail in details:
        if wanted in detail:
            return detail.split(":")[-1].strip()


def format_currency(value):
    sanitized_value = re.sub(r'[^\d,.-]', '', str(value)).replace(',', '.')
    try:
        return int(float(sanitized_value)) * 100
    except ValueError:
        return value * 100


def is_value_in_budget(value1, value2):
    def sanitize_money(value):
        clean_value = re.sub(r'[^\d.]', '', value)
        return float(clean_value)

    try:
        amount1 = sanitize_money(value1)
        amount2 = sanitize_money(value2)
        return amount1 > amount2
    except ValueError:
        raise ValueError(f"Invalid money format")


def find_district(soup, client, address):
    neighborhoods_of_interest = client["Bairros de interesse:"].split(",")
    for neighborhood in neighborhoods_of_interest:
        if fuzz.partial_ratio(neighborhood.strip().lower(), address.lower()) >= 90:
            return neighborhood.strip().title()

    iframe_element = soup.find('iframe', title='geolocalização')
    if iframe_element:
        iframe_src = iframe_element.get('src')
        parsed_url = urlparse(iframe_src)
        query_params = parse_qs(parsed_url.query)

        if 'q' in query_params:
            coordinates = query_params['q'][0]
            latitude, longitude = coordinates.split(',')
            try:
                geolocator = Photon(user_agent="measurements", timeout=5)
                location = geolocator.reverse((latitude, longitude), exactly_one=True)
                return location.raw["properties"].get("district") or location.raw["properties"].get("name")
            except:
                return None