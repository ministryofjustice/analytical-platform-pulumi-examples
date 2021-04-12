from airflow import DAG
from datetime import datetime
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

default_args = {
    "owner": "aws",
    "depends_on_past": False,
    "start_date": datetime(2019, 2, 20),
    "provide_context": True,
}

dag = DAG("kubernetes_pod_example", default_args=default_args, schedule_interval=None)

kube_config_path = "/usr/local/airflow/dags/.kube/config"

podRun = KubernetesPodOperator(
    namespace="airflow",
    image="amazon/aws-cli",
    cmds=["aws"],
    arguments=["sts", "get-caller-identity"],
    name="mwaa-pod-test",
    task_id="pod-task",
    get_logs=True,
    dag=dag,
    is_delete_operator_pod=False,
    config_file=kube_config_path,
    in_cluster=False,
    cluster_context="aws",
    service_account_name="mwaa-service-account",
)
