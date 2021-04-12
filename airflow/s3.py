from dataengineeringutils3.pulumi import Tagger
from pulumi_aws.s3 import Bucket, BucketPublicAccessBlock, BucketObject
from pulumi import ResourceOptions, FileAsset
from eks import cluster
import json

tagger = Tagger(environment_name="dev")

bucket = Bucket(
    resource_name="airflow",
    bucket="mojap-airflow-test",
    server_side_encryption_configuration={
        "rule": {"applyServerSideEncryptionByDefault": {"sseAlgorithm": "AES256"}}
    },
    versioning={"enabled": True},
)

BucketPublicAccessBlock(
    resource_name="airflow",
    block_public_acls=True,
    block_public_policy=True,
    bucket=bucket.id,
    ignore_public_acls=True,
    restrict_public_buckets=True,
    opts=ResourceOptions(parent=bucket),
)

content = "awscli\nkubernetes==12.0.1"

BucketObject(
    resource_name="airflow-requirements",
    opts=ResourceOptions(parent=bucket),
    bucket=bucket.id,
    content=content,
    key="requirements.txt",
    server_side_encryption="AES256",
)

BucketObject(
    resource_name="airflow-dag",
    opts=ResourceOptions(parent=bucket),
    bucket=bucket.id,
    key="dags/dag.py",
    server_side_encryption="AES256",
    source=FileAsset(path="./dag.py"),
)


def prepare_kube_config(kube_config: str) -> str:
    kube_config["users"][0]["user"]["exec"][
        "command"
    ] = "/usr/local/airflow/.local/bin/aws"
    return json.dumps(kube_config, indent=4)


BucketObject(
    resource_name="airflow-kube-config",
    opts=ResourceOptions(parent=bucket),
    bucket=bucket.id,
    content=cluster.kubeconfig.apply(prepare_kube_config),
    key="dags/.kube/config",
    server_side_encryption="AES256",
)
