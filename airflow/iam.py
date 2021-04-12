from pulumi_aws.iam import (
    Role,
    RolePolicyAttachment,
    get_policy_document,
    get_policy,
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementPrincipalArgs,
)
from pulumi import ResourceOptions
from dataengineeringutils3.pulumi import Tagger

tagger = Tagger(environment_name="dev")

execution_role_assume_role_policy = get_policy_document(
    statements=[
        GetPolicyDocumentStatementArgs(
            effect="Allow",
            actions=["sts:AssumeRole"],
            principals=[
                GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["airflow-env.amazonaws.com", "airflow.amazonaws.com"],
                )
            ],
        )
    ]
)

executionRole = Role(
    resource_name="airflow",
    assume_role_policy=execution_role_assume_role_policy.json,
    description="Execution role for Airflow",
    name="AmazonMWAAExecutionRole",
    tags=tagger.create_tags("AmazonMWAAExecutionRole"),
)

policy = get_policy(arn="arn:aws:iam::aws:policy/AdministratorAccess")

RolePolicyAttachment(
    resource_name="airflow",
    policy_arn=policy.arn,
    role=executionRole.name,
    opts=ResourceOptions(parent=executionRole),
)

