from infra.services import Services


class PipelineConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Pipeline",
            path="./functions/pipeline",
            description="Pipeline for processing auction data",
        )

        services.sqs.create_trigger("results_queue", function)
