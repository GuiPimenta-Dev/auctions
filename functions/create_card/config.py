from infra.services import Services

class CreateCardConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateCard",
            path="./functions/create_card",
            description="create clickup card",
            
        )

        services.api_gateway.create_endpoint("GET", "/create_card", function, public=True)

        services.secrets_manager.google_sheets_secret.grant_read(function)

            