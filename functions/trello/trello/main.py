from utils import *


def lambda_handler(event, context):
    lists = get_lists()
    first_list = lists[0]
    card = create_a_card(first_list["id"], "Campo Grande", "Imoveis em Campo Grande")
    attachment = create_attachment(card["id"], "campo_grande.xlsx")
    pass

lambda_handler({}, {})