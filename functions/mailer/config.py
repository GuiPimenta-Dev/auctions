from infra.services import Services


class MailerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Mailer",
            path="./functions/mailer",
            description="Send email about what was scraped",
        )
