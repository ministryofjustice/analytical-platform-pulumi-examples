import json

import pulumi_aws as aws

lambdaAssumeRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    identifiers=[f"lambda.{aws.config.region}.amazonaws.com"],
                    type="Service",
                )
            ],
        )
    ]
)

lambdaRole = aws.iam.Role(
    resource_name="lambda",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": f"lambda.{aws.config.region}.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

lambdaRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["athena:*", "logs:*"], resources=["*"]
        )
    ]
)

lambdaRolePolicy = aws.iam.RolePolicy(
    resource_name="lambda", role=lambdaRole.id, policy=lambdaRolePolicyDocument.json
)

stateMachineAssumeRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    identifiers=[f"states.{aws.config.region}.amazonaws.com"],
                    type="Service",
                )
            ],
        )
    ]
)

stateMachineRole = aws.iam.Role(
    resource_name="state-machine",
    assume_role_policy=stateMachineAssumeRolePolicyDocument.json,
)

stateMachineRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["lambda:InvokeFunction"], resources=["*"]
        )
    ]
)

stateMachineRolePolicy = aws.iam.RolePolicy(
    resource_name="state-machine",
    role=stateMachineRole.id,
    policy=stateMachineRolePolicyDocument.json,
)

eventRuleAssumeRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    identifiers=["events.amazonaws.com"],
                    type="Service",
                )
            ],
        )
    ]
)

eventRuleRole = aws.iam.Role(
    resource_name="event-rule",
    assume_role_policy=eventRuleAssumeRolePolicyDocument.json,
)

eventRuleRolePolicyDocument = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(actions=["states:*"], resources=["*"])
    ]
)

eventRuleRolePolicy = aws.iam.RolePolicy(
    resource_name="event-rule",
    role=eventRuleRole.id,
    policy=eventRuleRolePolicyDocument.json,
)