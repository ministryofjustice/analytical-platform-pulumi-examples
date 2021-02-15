import json

import pulumi
import pulumi_aws as aws

from iam import stateMachineRole
from lambda_ import startQueryExecutionFunction, getQueryExecutionFunction

lambda_retry_parameters = [
    {
        "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
        ],
        "IntervalSeconds": 1,
        "MaxAttempts": 3,
        "BackoffRate": 2,
    }
]


def create_definition(get_query_execution_arn, start_query_execution_arn):
    return json.dumps(
        {
            "Comment": "An example state machine with a Lambda function",
            "StartAt": "Create Database If Not Exists",
            "States": {
                "Create Database If Not Exists": {
                    "Type": "Task",
                    "Resource": start_query_execution_arn,
                    "InputPath": "$.DatabaseQueryString",
                    "ResultPath": "$.DatabaseQueryExecutionId",
                    "Next": "Wait Create Database If Not Exists",
                    "Retry": lambda_retry_parameters,
                },
                "Wait Create Database If Not Exists": {
                    "Type": "Wait",
                    "Seconds": 10,
                    "Next": "Get Status Create Database If Not Exists",
                },
                "Get Status Create Database If Not Exists": {
                    "Type": "Task",
                    "Resource": get_query_execution_arn,
                    "InputPath": "$.DatabaseQueryExecutionId",
                    "ResultPath": "$.DatabaseQueryExecutionStatus",
                    "Next": "Create Database If Not Exists Successful?",
                    "Retry": lambda_retry_parameters,
                },
                "Create Database If Not Exists Successful?": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.DatabaseQueryExecutionStatus",
                            "StringEquals": "FAILED",
                            "Next": "Create Database If Not Exists Failed",
                        },
                        {
                            "Variable": "$.DatabaseQueryExecutionStatus",
                            "StringEquals": "SUCCEEDED",
                            "Next": "Create Database If Not Exists Succeeded",
                        },
                    ],
                    "Default": "Wait Create Database If Not Exists",
                },
                "Create Database If Not Exists Failed": {"Type": "Fail"},
                "Create Database If Not Exists Succeeded": {
                    "Type": "Pass",
                    "Next": "Table Map",
                },
                "Table Map": {
                    "Type": "Map",
                    "ItemsPath": "$.TableQueryStrings",
                    "Iterator": {
                        "StartAt": "Drop Table If Exists",
                        "States": {
                            "Drop Table If Exists": {
                                "Type": "Task",
                                "Resource": start_query_execution_arn,
                                "InputPath": "$.Drop",
                                "ResultPath": "$.DropQueryExecutionId",
                                "Next": "Wait Drop Table If Exists",
                                "Retry": lambda_retry_parameters,
                            },
                            "Wait Drop Table If Exists": {
                                "Type": "Wait",
                                "Seconds": 10,
                                "Next": "Get Status Drop Table If Exists",
                            },
                            "Get Status Drop Table If Exists": {
                                "Type": "Task",
                                "Resource": get_query_execution_arn,
                                "InputPath": "$.DropQueryExecutionId",
                                "ResultPath": "$.DropQueryExecutionStatus",
                                "Next": "Drop Table If Exists Successful?",
                                "Retry": lambda_retry_parameters,
                            },
                            "Drop Table If Exists Successful?": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.DropQueryExecutionStatus",
                                        "StringEquals": "FAILED",
                                        "Next": "Drop Table If Exists Failed",
                                    },
                                    {
                                        "Variable": "$.DropQueryExecutionStatus",
                                        "StringEquals": "SUCCEEDED",
                                        "Next": "Drop Table If Exists Succeeded",
                                    },
                                ],
                                "Default": "Wait Drop Table If Exists",
                            },
                            "Drop Table If Exists Failed": {"Type": "Fail"},
                            "Drop Table If Exists Succeeded": {
                                "Type": "Pass",
                                "Next": "Create Table",
                            },
                            "Create Table": {
                                "Type": "Task",
                                "Resource": start_query_execution_arn,
                                "InputPath": "$.Create",
                                "ResultPath": "$.CreateQueryExecutionId",
                                "Next": "Wait Create Table",
                                "Retry": lambda_retry_parameters,
                            },
                            "Wait Create Table": {
                                "Type": "Wait",
                                "Seconds": 10,
                                "Next": "Get Status Create Table",
                            },
                            "Get Status Create Table": {
                                "Type": "Task",
                                "Resource": get_query_execution_arn,
                                "InputPath": "$.CreateQueryExecutionId",
                                "ResultPath": "$.CreateQueryExecutionStatus",
                                "Next": "Create Table Successful?",
                                "Retry": lambda_retry_parameters,
                            },
                            "Create Table Successful?": {
                                "Type": "Choice",
                                "Choices": [
                                    {
                                        "Variable": "$.CreateQueryExecutionStatus",
                                        "StringEquals": "FAILED",
                                        "Next": "Create Table Failed",
                                    },
                                    {
                                        "Variable": "$.CreateQueryExecutionStatus",
                                        "StringEquals": "SUCCEEDED",
                                        "Next": "Create Table Succeeded",
                                    },
                                ],
                                "Default": "Wait Create Table",
                            },
                            "Create Table Failed": {"Type": "Fail"},
                            "Create Table Succeeded": {"Type": "Pass", "End": True},
                        },
                    },
                    "Next": "Job Succeeded",
                },
                "Job Succeeded": {"Type": "Succeed"},
            },
        },
        indent=4,
    )


definition = pulumi.Output.all(
    getQueryExecutionFunction.arn, startQueryExecutionFunction.arn
).apply(lambda o: create_definition(*o))

stateMachine = aws.sfn.StateMachine(
    resource_name="athena-query-execution",
    definition=definition,
    name="athena-query-execution",
    role_arn=stateMachineRole.arn,
)
