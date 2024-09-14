from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.get_location_layer = _lambda.LayerVersion(
            scope,
            id="GetLocationLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/get_location")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.robots_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id='LxmlLayer',
            layer_version_arn='arn:aws:lambda:us-east-2:211125768252:layer:robots:1',
         )
