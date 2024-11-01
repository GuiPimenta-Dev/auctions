import json
from dataclasses import dataclass

import clickup
import excel
from auction import Auction, Bid, Bids


@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    name = event["queryStringParameters"]["name"]
    url = event["queryStringParameters"]["url"]

    row = excel.get_auction_row(name, url)

    #  ['Data de Inclusão', 'Criar Card', 'Cliente', 'Estado', 'Cidade', 'Bairro', 'Nome do Imóvel', 'Endereço', 'Data 1o Leilão', 'Data 2o Leilão', 'Valor de Avaliação', 'Lance Inicial', 'Deságio', 'Valor 1a Hasta', 'Valor 2a Hasta', 'Valores somados com leiloeiro + taxas edital 1a Hasta', 'Valores somados com leiloeiro + taxas edital 2a Hasta', 'Tipo de Imóvel', 'Modalidade de Venda', 'Metragem do imóvel', 'Medida da área privativa ou de uso exclusivo', 'Número dormitórios', 'Vagas garagem', 'Modelo de Leilão (Judicial, Extra...)', 'Status', 'Fase do Leilão', 'Site', 'Observações', 'Valor da Entrada 25% (1a Hasta)', 'Valor da Entrada 25% (2a Hasta)', 'Mais 30 parcelas de:', 'Valor m2 para região', 'Imagem']
    auction = Auction(
        name=row["Nome do Imóvel"],
        type_=row["Tipo de Imóvel"],
        modality=row["Modalidade de Venda"],
        state=row["Estado"],
        city=row["Cidade"],
        address=row["Endereço"],
        district=row["Bairro"],
        appraised_value=row["Valor de Avaliação"],
        discount_value=row["Lance Inicial"],
        bids=Bids(
            first_bid=Bid(date=row["Data 1o Leilão"], value=row["Valor 1a Hasta"]),
            second_bid=Bid(date=row["Data 2o Leilão"], value=row["Valor 2a Hasta"])
        ),
        bedrooms=row["Dormitórios"],
        parking=row["Vagas garagem"],
        image=row["Imagem"],
        url=row["Site"],
        files=None,
        general_info=None,
        m2=row["Metragem do imóvel"]
    )
    response = clickup.create_auction(auction, row["Cliente"])

    return {
        "statusCode": 302,
        "headers": {
            "Location": response["url"]
        }
    }

if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "name": "Carlos Wolff",
            "url": "https://www.leilaoimovel.com.br/imovel/pr/curitiba/residencial-felice-cond-club-1-vaga-na-garagem-imovel-caixa-economica-federal-cef-1957424-1555526404587-venda-direta-caixa"
        }
    }
    lambda_handler(event, {})