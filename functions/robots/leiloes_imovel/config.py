from infra.services import Services


class LeiloesImovelConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="LeiloesImovel",
            path="./functions/robots",
            description="A scraper",
            directory="leiloes_imovel",
        )

        services.sns.create_trigger("auctions_topic", function)

        services.event_bridge.schedule(
            expression="rate(1 day)",
            rule_name="auctions",
            function=function,
        )