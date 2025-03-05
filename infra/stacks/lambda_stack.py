from functions.reminder.config import ReminderConfig
from aws_cdk import Stack
from constructs import Construct

from functions.create_card.config import CreateCardConfig
from functions.robots.leiloes_imovel.config import LeiloesImovelConfig
from functions.trigger.config import TriggerConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Robots
        LeiloesImovelConfig(self.services)

        # Trigger
        TriggerConfig(self.services)

        # CreateCard
        CreateCardConfig(self.services)

        # Reminder
        ReminderConfig(self.services)
