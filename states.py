import json

import pulumi_aws as aws

from iam import stateMachineRole
from lambda_ import function

definition = function.arn.apply(
    lambda arn: json.dumps(
        {
            "Comment": "An example state machine with a Lambda function",
            "StartAt": "Create Database If Not Exists",
            "States": {
                "Create Database If Not Exists": {
                    "Type": "Task",
                    "Resource": arn,
                    "InputPath": "$.DatabaseQueryString",
                    "ResultPath": "$.DatabaseQueryExecutionId",
                    "Next": "Wait Create Database If Not Exists",
                    "Retry": [
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
                    ],
                },
                "Wait Create Database If Not Exists": {
                    "Type": "Wait",
                    "Seconds": 10,
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
                                "Resource": arn,
                                "InputPath": "$.Drop",
                                "ResultPath": "$.DropQueryExecutionId",
                                "Next": "Wait Drop Table If Exists",
                            },
                            "Wait Drop Table If Exists": {
                                "Type": "Wait",
                                "Seconds": 10,
                                "Next": "Create Table",
                            },
                            "Create Table": {
                                "Type": "Task",
                                "Resource": arn,
                                "InputPath": "$.Create",
                                "ResultPath": "$.CreateQueryExecutionId",
                                "Next": "Wait Create Table",
                            },
                            "Wait Create Table": {
                                "Type": "Wait",
                                "Seconds": 10,
                                "End": True,
                            },
                        },
                    },
                    "End": True,
                },
            },
        },
        indent=4,
    )
)

stateMachine = aws.sfn.StateMachine(
    resource_name="athena-query-execution",
    definition=definition,
    name="athena-query-execution",
    role_arn=stateMachineRole.arn,
)
