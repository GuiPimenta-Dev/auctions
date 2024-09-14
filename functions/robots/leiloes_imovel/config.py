from infra.services import Services


class LeiloesImovelConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="LeiloesImovel",
            path="./functions/robots",
            description="A scraper",
            directory="leiloes_imovel",
  
        )

        services.api_gateway.create_endpoint("POST", "/robots", function, public=True)
