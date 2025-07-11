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
            layer_version_arn="arn:aws:lambda:us-east-2:412381763358:layer:robots:2",
        )

        self.clickup_layer = _lambda.LayerVersion(
            scope,
            id="ClickupLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/clickup")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.auction_layer = _lambda.LayerVersion(
            scope,
            id="AuctionLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/auction")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.excel_layer = _lambda.LayerVersion(
            scope,
            id='ExcelLayer',
            code=_lambda.Code.from_asset(Path.layer('layers/excel')),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='',
         )

        self.pandas_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id='PandasLayer',
            layer_version_arn='arn:aws:lambda:us-east-2:336392948345:layer:AWSSDKPandas-Python39:28',
        )
        self.xlsxwriter_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id='XlsxwriterLayer',
            layer_version_arn='arn:aws:lambda:us-east-2:412381763358:layer:xlsxwriter:1',
         )

        self.cloudscraper_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id='CloudscraperLayer',
            layer_version_arn='arn:aws:lambda:us-east-2:412381763358:layer:cloudscraper:3',
         )
