from pulumi_aws.mwaa import Environment, EnvironmentNetworkConfigurationArgs
from pulumi import ResourceOptions
from iam import executionRole
from s3 import bucket
from vpc import privateSubnet1, privateSubnet2, securityGroup
from data_engineering_pulumi_components.utils import Tagger

tagger = Tagger(environment_name="dev")

Environment(
    resource_name="airflow",
    airflow_version="1.10.12",
    dag_s3_path="dags",
    environment_class="mw1.small",
    execution_role_arn=executionRole.arn,
    max_workers=1,
    min_workers=1,
    name="TestEnvironment",
    source_bucket_arn=bucket.arn,
    network_configuration=EnvironmentNetworkConfigurationArgs(
        security_group_ids=[securityGroup.id],
        subnet_ids=[privateSubnet1.id, privateSubnet2.id],
    ),
    requirements_s3_path="requirements.txt",
    tags=tagger.create_tags("TestEnvironment"),
    webserver_access_mode="PUBLIC_ONLY",
    opts=ResourceOptions(import_="TestEnvironment"),
)
