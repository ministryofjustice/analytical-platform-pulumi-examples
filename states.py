import json

import pulumi_aws as aws

from iam import stateMachineRole
from lambda_ import function

definition = function.arn.apply(
    lambda arn: json.dumps(
        {
            "Comment": "An example state machine with a Lambda function",
            "StartAt": "Hello World",
            "States": {
                "Hello World": {"Type": "Task", "Resource": arn, "End": True},
            },
        }
    )
)

stateMachine = aws.sfn.StateMachine(
    resource_name="hello-world",
    definition=definition,
    name="Helloworld",
    role_arn=stateMachineRole.arn,
)
