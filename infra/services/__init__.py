from infra.services.sqs import SQS
from infra.services.event_bridge import EventBridge
from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.layers import Layers
from infra.services.secrets_manager import SecretsManager
from infra.services.sns import SNS


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.layers = Layers(scope)
        self.secrets_manager = SecretsManager(scope, context)
        self.aws_lambda = Lambda(scope, context, self.layers, self.secrets_manager)
        self.sns = SNS(scope, context)
        self.event_bridge = EventBridge(scope, context)
        self.sqs = SQS(scope, context)
