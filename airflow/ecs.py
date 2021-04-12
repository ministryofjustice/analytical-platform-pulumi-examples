import json
from pulumi_aws.ecs import (
    Cluster,
    ClusterDefaultCapacityProviderStrategyArgs,
    TaskDefinition,
)
from dataengineeringutils3.pulumi import Tagger

tagger = Tagger(environment_name="dev")

cluster = Cluster(
    resource_name="airflow",
    capacity_providers=["FARGATE"],
    default_capacity_provider_strategies=[
        ClusterDefaultCapacityProviderStrategyArgs(capacity_provider="FARGATE")
    ],
    name="airflow",
    tags=tagger.create_tags("airflow"),
)

TaskDefinition(
    resource_name="base",
    container_definitions=json.dumps(
        [
            {
                "name": "base",
                "image": "ubuntu:20.04",
                "memory": 1024,
                "essential": True,
            }
        ]
    ),
    family="airflow-base",
    cpu=1024,
    execution_role_arn=None,
    inference_accelerators=None,
    ipc_mode=None,
    memory=2048,
    network_mode="awsvpc",
    pid_mode=None,
    placement_constraints=None,
    proxy_configuration=None,
    requires_compatibilities=["FARGATE"],
    tags=tagger.create_tags("base"),
    task_role_arn=None,
    volumes=None,
)
