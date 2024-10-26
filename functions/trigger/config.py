from infra.services import Services


class TriggerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Trigger",
            path="./functions/trigger",
            description="Trigger the robots",
            environment={"TOPIC_ARN": services.sns.auctions_topic.topic_arn},
        )

        services.api_gateway.create_endpoint("POST", "/trigger", function, public=True)

        services.secrets_manager.google_sheets_secret.grant_read(function)

        services.sns.grant_publish("auctions_topic", function)
