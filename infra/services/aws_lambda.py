from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, Runtime

from lambda_forge.path import Path
from lambda_forge.trackers import function


class Lambda:
    def __init__(self, scope, context, layers, sm) -> None:
        self.functions = {}
        self.scope = scope
        self.context = context
        self.layers = layers
        self.sm = sm

    @function
    def create_function(
        self,
        name,
        path,
        description,
        directory=None,
        layers=[],
        environment={},
        memory_size=128,
        runtime=Runtime.PYTHON_3_9,
        timeout=1,
    ):

        layers = layers + [ self.layers.get_location_layer, self.layers.robots_layer ]

        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=self.context.create_id(name),
            runtime=runtime,
            handler=Path.handler(directory),
            environment=environment,
            code=Code.from_asset(path=Path.function(path)),
            layers=layers,
            timeout=Duration.minutes(timeout),
            memory_size=memory_size,
        )

        self.sm.trello_secret.grant_read(function)

        self.functions[name] = function
        return function
