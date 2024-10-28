import re

from fuzzywuzzy import process

states = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}


def find_state_based_on_state_of_interest(s: str) -> dict:
    s = re.sub(r"\s+", " ", s.strip()).lower()

    normalized_states = {re.sub(r"\s+", " ", k).lower(): v for k, v in states.items()}

    closest_state = process.extractOne(s, normalized_states.keys())
    if closest_state:
        state_name = closest_state[0]
        abbreviation = normalized_states[state_name]
        return {"state": state_name.title(), "abbreviation": abbreviation}
    else:
        return {"state": None, "abbreviation": None}

from geopy.geocoders import Nominatim


def find_neighborhood(dms_string):
    # Function to convert DMS to decimal
    def convert(dms):
        degrees, minutes = dms[:-1].split('°')
        minutes, seconds = minutes.split("'")
        seconds = seconds[:-1]  # Remove the seconds symbol

        # Calculate the decimal value
        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        
        # Apply the negative sign if direction is South or West
        if 'S' in dms or 'W' in dms:
            decimal = -decimal
        
        return decimal

    # Split the input string and convert to decimal
    parts = dms_string.strip().split()
    lat_dms = parts[0]  # Latitude in DMS
    lon_dms = parts[1]  # Longitude in DMS

    latitude = convert(lat_dms)
    longitude = convert(lon_dms)

    # Initialize geolocator
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Get the location based on latitude and longitude
    location = geolocator.reverse((latitude, longitude), exactly_one=True)

    # Return the neighborhood if available
    if location:
        neighborhood = location.raw['address'].get('suburb', "Bairro não encontrado")
        return neighborhood
    else:
        return "Bairro não encontrado"
