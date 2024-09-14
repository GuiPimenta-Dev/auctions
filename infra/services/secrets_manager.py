from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:

        self.trello_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="TrelloSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:Trello-szuLNz",
        )
