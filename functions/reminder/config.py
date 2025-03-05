from infra.services import Services

class ReminderConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Reminder",
            path="./functions/reminder",
            description="pacients reminder",
            layers=[services.layers.pandas_layer, services.layers.robots_layer, services.layers.xlsxwriter_layer],
            timeout=15,   
            use_default=False           
        )

        services.event_bridge.schedule(
            expression="cron(0 11 * * ? *)",
            rule_name="pacients",
            function=function,
        )

            