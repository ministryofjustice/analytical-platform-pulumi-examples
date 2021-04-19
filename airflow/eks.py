import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
from data_engineering_pulumi_components.utils import Tagger
from pulumi import Output, ResourceOptions, export

from iam import executionRole
from vpc import privateSubnet1, privateSubnet2, publicSubnet1, publicSubnet2, vpc

tagger = Tagger(environment_name="dev")

cluster = eks.Cluster(
    resource_name="airflow",
    create_oidc_provider=True,
    fargate=True,
    name="airflow",
    private_subnet_ids=[privateSubnet1.id, privateSubnet2.id],
    public_subnet_ids=[publicSubnet1.id, publicSubnet2.id],
    role_mappings=[
        eks.RoleMappingArgs(
            groups=["system:masters"],
            role_arn=executionRole.arn,
            username="mwaa-service",
        )
    ],
    version="1.19",
    vpc_id=vpc.id,
    tags=tagger.create_tags(name="airflow"),
)

export("kubeconfig", cluster.kubeconfig)

airflowNamespace = k8s.core.v1.Namespace(
    resource_name="airflow",
    metadata=k8s.meta.v1.ObjectMetaArgs(name="airflow"),
    opts=ResourceOptions(provider=cluster.provider),
)

role = k8s.rbac.v1.Role(
    resource_name="airflow",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="mwaa-role", namespace=airflowNamespace.metadata.name
    ),
    rules=[
        k8s.rbac.v1.PolicyRuleArgs(
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

roleBinding = k8s.rbac.v1.RoleBinding(
    resource_name="airflow",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="mwaa-role-binding", namespace=airflowNamespace.metadata.name
    ),
    subjects=[k8s.rbac.v1.SubjectArgs(kind="User", name="mwaa-service")],
    role_ref=k8s.rbac.v1.RoleRefArgs(
        api_group="rbac.authorization.k8s.io", kind="Role", name="mwaa-role"
    ),
)

service_account_name = "mwaa-service-account"


def get_assume_role_policy(args):
    url, arn, namespace = args
    return aws.iam.get_policy_document(
        statements=[
            aws.iam.GetPolicyDocumentStatementArgs(
                effect="Allow",
                actions=["sts:AssumeRoleWithWebIdentity"],
                principals=[
                    aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                        type="Federated",
                        identifiers=[arn],
                    )
                ],
                conditions=[
                    aws.iam.GetPolicyDocumentStatementConditionArgs(
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

baseContainerRole = aws.iam.Role(
    resource_name="base-container-role",
    assume_role_policy=Output.all(
        oidc_provider.url, oidc_provider.arn, airflowNamespace.metadata.name
    ).apply(get_assume_role_policy),
    description="Base role for Airflow container tasks",
    name="AmazonMWAABaseContainerRole",
    tags=tagger.create_tags("AmazonMWAABaseContainerRole"),
)

serviceAccount = k8s.core.v1.ServiceAccount(
    resource_name="airflow",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name=service_account_name,
        namespace=airflowNamespace.metadata.name,
        annotations={"eks.amazonaws.com/role-arn": baseContainerRole.arn},
    ),
    opts=ResourceOptions(provider=cluster.provider),
)

containerRole = aws.iam.Role(
    resource_name="container-role",
    assume_role_policy=Output.all(
        oidc_provider.url, oidc_provider.arn, airflowNamespace.metadata.name
    ).apply(get_assume_role_policy),
    description="Role for Airflow container tasks",
    name="AmazonMWAAContainerRole",
    tags=tagger.create_tags("AmazonMWAAContainerRole"),
)

fargateProfile = aws.eks.FargateProfile(
    resource_name="airflow",
    cluster_name=cluster.name,
    fargate_profile_name="airflow",
    pod_execution_role_arn=cluster.core.fargate_profile.pod_execution_role_arn,
    selectors=[
        aws.eks.FargateProfileSelectorArgs(namespace=airflowNamespace.metadata.name)
    ],
    subnet_ids=cluster.private_subnet_ids,
    tags=tagger.create_tags("airflow"),
    opts=ResourceOptions(parent=cluster),
)
