from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:

        self.clickup_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="Clickup",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:412381763358:secret:Clickup-zy6sCf",
        )

        self.google_sheets_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="GoogleSheetsSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:412381763358:secret:GoogleSheets-t7tlvt",
        )
