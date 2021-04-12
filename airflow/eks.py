from dataengineeringutils3.pulumi import Tagger
from pulumi import Output, ResourceOptions, export
import pulumi_aws.iam as iam
from pulumi_eks import Cluster, RoleMappingArgs
from pulumi_kubernetes.core.v1 import Namespace, ServiceAccount
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs
from pulumi_kubernetes.rbac.v1 import (
    PolicyRuleArgs,
    Role,
    RoleBinding,
    RoleRefArgs,
    SubjectArgs,
)

from iam import executionRole
from vpc import privateSubnet1, privateSubnet2, publicSubnet1, publicSubnet2, vpc

tagger = Tagger(environment_name="dev")

cluster = Cluster(
    resource_name="airflow",
    create_oidc_provider=True,
    desired_capacity=1,
    instance_type="t3a.nano",
    name="airflow",
    min_size=1,
    max_size=4,
    private_subnet_ids=[privateSubnet1.id, privateSubnet2.id],
    public_subnet_ids=[publicSubnet1.id, publicSubnet2.id],
    role_mappings=[
        RoleMappingArgs(
            groups=["system:masters"],
            role_arn=executionRole.arn,
            username="mwaa-service",
        )
    ],
    version="1.19",
    vpc_id=vpc.id,
)

export("kubeconfig", cluster.kubeconfig)

namespace = Namespace(
    resource_name="airflow",
    metadata=ObjectMetaArgs(name="airflow"),
    opts=ResourceOptions(provider=cluster.provider),
)

role = Role(
    resource_name="airflow",
    metadata=ObjectMetaArgs(name="mwaa-role", namespace=namespace.metadata.name),
    rules=[
        PolicyRuleArgs(
            api_groups=["", "apps", "batch", "extensions"],
            resources=[
                "jobs",
                "pods",
                "pods/attach",
                "pods/exec",
                "pods/log",
                "pods/portforward",
                "secrets",
                "services",
            ],
            verbs=["create", "describe", "delete", "get", "list", "patch", "update"],
        )
    ],
)

roleBinding = RoleBinding(
    resource_name="airflow",
    metadata=ObjectMetaArgs(
        name="mwaa-role-binding", namespace=namespace.metadata.name
    ),
    subjects=[SubjectArgs(kind="User", name="mwaa-service")],
    role_ref=RoleRefArgs(
        api_group="rbac.authorization.k8s.io", kind="Role", name="mwaa-role"
    ),
)

service_account_name = "mwaa-service-account"


def get_assume_role_policy(args):
    url, arn, namespace = args
    return iam.get_policy_document(
        statements=[
            iam.GetPolicyDocumentStatementArgs(
                effect="Allow",
                actions=["sts:AssumeRoleWithWebIdentity"],
                principals=[
                    iam.GetPolicyDocumentStatementPrincipalArgs(
                        type="Federated",
                        identifiers=[arn],
                    )
                ],
                conditions=[
                    iam.GetPolicyDocumentStatementConditionArgs(
                        test="StringEquals",
                        values=[
                            f"system:serviceaccount:{namespace}"
                            f":{service_account_name}"
                        ],
                        variable=f"{url}:sub",
                    )
                ],
            )
        ]
    ).json


oidc_provider = cluster.core.oidc_provider

baseContainerRole = iam.Role(
    resource_name="base-container-role",
    assume_role_policy=Output.all(
        oidc_provider.url, oidc_provider.arn, namespace.metadata.name
    ).apply(get_assume_role_policy),
    description="Base role for Airflow container tasks",
    name="AmazonMWAABaseContainerRole",
    tags=tagger.create_tags("AmazonMWAABaseContainerRole"),
)

serviceAccount = ServiceAccount(
    resource_name="airflow",
    metadata=ObjectMetaArgs(
        name=service_account_name,
        namespace=namespace.metadata.name,
        annotations={"eks.amazonaws.com/role-arn": baseContainerRole.arn},
    ),
    opts=ResourceOptions(provider=cluster.provider),
)

containerRole = iam.Role(
    resource_name="container-role",
    assume_role_policy=Output.all(
        oidc_provider.url, oidc_provider.arn, namespace.metadata.name
    ).apply(get_assume_role_policy),
    description="Role for Airflow container tasks",
    name="AmazonMWAAContainerRole",
    tags=tagger.create_tags("AmazonMWAAContainerRole"),
)