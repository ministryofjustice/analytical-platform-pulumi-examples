import pulumi
import pulumi_aws as aws

from iam import lambdaRole

config = pulumi.Config()

startQueryExecutionFunction = aws.lambda_.Function(
    resource_name="start-query-execution",
    code=pulumi.AssetArchive({".": pulumi.FileArchive("lambda/start_query_execution")}),
    description="Starts the execution of an Amazon Athena query",
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={"AWS_ACCOUNT_ID": config.require("awsAccountId")}
    ),
    handler="start_query_execution.handler",
    name="start-query-execution",
    role=lambdaRole.arn,
    runtime="python3.8",
)

getQueryExecutionFunction = aws.lambda_.Function(
    resource_name="get-query-execution",
    code=pulumi.AssetArchive({".": pulumi.FileArchive("lambda/get_query_execution")}),
    description="Gets information about the execution of an Amazon Athena query",
    handler="get_query_execution.handler",
    name="get-query-execution",
    role=lambdaRole.arn,
    runtime="python3.8",
)
