from airflow.decorators import dag, task
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

# Define your DAG
@dag(
    'example_kubernetes_pod',
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['example'],
)
def example_kubernetes_pod():
    # Define the sidecar container
    sidecar_container = k8s.V1Container(
        name='sidecar-container',
        image='alpine:latest',
        # Define any additional configurations for your sidecar container here
    )   

    # Define the KPO with the sidecar container
    kpo_with_sidecar = KubernetesPodOperator(
        namespace='default',
        image='alpine:latest',
        name='kpo-with-sidecar',
        task_id='task-with-sidecar',
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(containers=[sidecar_container])
            )
        },
        cmds=['sleep', '300']
    )

dag_obj = example_kubernetes_pod()