import boto3

client = boto3.client("athena", region_name="eu-west-1")


def handler(event, context):
    response = client.get_query_execution(QueryExecutionId=event)
    status = response["QueryExecution"]["Status"]["State"]
    return status
