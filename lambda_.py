import pulumi
import pulumi_aws as aws

from iam import lambdaRole

function = aws.lambda_.Function(
    resource_name="start-query-execution",
    code=pulumi.AssetArchive({".": pulumi.FileArchive("lambda/start_query_execution")}),
    description="Starts the execution of an Amazon Athena query",
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={"AWS_ACCOUNT_ID": aws.config.allowed_account_ids[0]}
    ),
    handler="start_query_execution.handler",
    name="start-query-execution",
    role=lambdaRole.arn,
    runtime="python3.8",
)
