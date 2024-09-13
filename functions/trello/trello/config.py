from infra.services import Services

class TrelloConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Trello",
            path="./functions/trello",
            description="save attachment on trello",
            directory="trello"
        )

        services.api_gateway.create_endpoint("POST", "/trello", function, public=True)

            