import pulumi
import pulumi_aws as aws

from iam import lambdaRole

function = aws.lambda_.Function(
    resource_name="hello-world",
    code=pulumi.AssetArchive(
        {".": pulumi.FileArchive("lambda/hello_world")}
    ),
    description="Hello world AWS Lambda function",
    environment=None,
    handler="hello_world.handler",
    name="hello-world",
    role=lambdaRole.arn,
    runtime="python3.8",
)
