import re

import requests
from fuzzywuzzy import process

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

    for s in inputs:
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

    return results


def css_select(element, selector):
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else "-"

def css_select_list(element, selector):
    return [e.get_text(strip=True) for e in element.select(selector)]


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



