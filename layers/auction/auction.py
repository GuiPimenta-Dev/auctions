from dataclasses import dataclass
from typing import List


@dataclass
class Bid:
    date: str
    value: str

@dataclass
class Bids:
    first_bid: Bid 
    second_bid: Bid 

@dataclass
class Auction:
    name: str
    type_: str
    modality: str
    state: str
    city: str
    address: str
    appraised_value: str
    discount_value: str
    bids: Bids 
    bedrooms: str
    parking: str
    image: str
    url: str
    files: List[str]
    general_info: str
    m2: str
