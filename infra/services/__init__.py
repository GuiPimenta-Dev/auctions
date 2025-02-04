from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.event_bridge import EventBridge
from infra.services.layers import Layers
from infra.services.secrets_manager import SecretsManager


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.layers = Layers(scope)
        self.secrets_manager = SecretsManager(scope, context)
        self.aws_lambda = Lambda(scope, context, self.layers, self.secrets_manager)
        self.event_bridge = EventBridge(scope, context)
