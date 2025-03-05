from infra.services import Services

class ReminderConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Reminder",
            path="./functions/reminder",
            description="pacients reminder",
            timeout=15              
        )

        services.event_bridge.schedule(
            expression="cron(0 11 * * ? *)",
            rule_name="pacients",
            function=function,
        )

            