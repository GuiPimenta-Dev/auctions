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
