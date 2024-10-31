from infra.services import Services


class LeiloesImovelConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="LeiloesImovel",
            path="./functions/robots",
            description="A scraper",
            directory="leiloes_imovel",
            timeout=15  
        )

        services.secrets_manager.google_sheets_secret.grant_read(function)

        services.event_bridge.schedule(
            expression="cron(0 10 * * ? *)",
            rule_name="auctions",
            function=function,
        )