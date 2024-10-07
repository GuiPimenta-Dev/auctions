from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.string_utils = _lambda.LayerVersion(
            scope,
            id="StringUtilsLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/string_utils")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.robots_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="LxmlLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:robots:1",
        )

        self.trello_layer = _lambda.LayerVersion(
            scope,
            id="TrelloLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/trello")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.clickup_layer = _lambda.LayerVersion(
            scope,
            id='ClickupLayer',
            code=_lambda.Code.from_asset(Path.layer('layers/clickup')),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='',
         )
