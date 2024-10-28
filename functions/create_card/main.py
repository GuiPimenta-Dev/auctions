import json
from dataclasses import dataclass
from auction import Auction, Bid, Bids
import excel
import clickup

@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    index = event["queryStringParameters"]["index"]

    row = excel.get_auction_row(index)
    auction = Auction(
        name=row[0],
        type_=row[15],
        modality=row[15],
        state=row[2],
        city=row[3],
        address=row[5],
        district=row[6],
        appraised_value=row[8],
        discount_value=row[9],
        bids=Bids(
            first_bid=Bid(date=row[6], value=row[11]),
            second_bid=Bid(date=row[7], value=row[12])
        ),
        bedrooms=row[19],
        parking=row[20],
        image=row[30],
        url=row[24],
        files=row[17],
        general_info=row[18],
        m2=row[17]
    )
    clickup.create_auction(auction, row[1])

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello World!"}),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }

if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "index": "8"
        }
    }
    lambda_handler(event, {})