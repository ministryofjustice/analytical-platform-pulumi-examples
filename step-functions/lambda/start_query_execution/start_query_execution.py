import boto3
import os


client = boto3.client("athena")

account_id = os.getenv("AWS_ACCOUNT_ID")


def handler(event, context):
    print(event)
    response = client.start_query_execution(
        QueryString=event,
        ResultConfiguration={
            "OutputLocation": f"s3://aws-athena-query-results-{account_id}-eu-west-1/",
            "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"},
        },
    )
    return response["QueryExecutionId"]
