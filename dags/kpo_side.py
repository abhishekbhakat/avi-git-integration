from airflow.decorators import dag, task
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from pendulum import datetime
from kubernetes.client import models as k8s

# Define your DAG
@dag(
    'example_kubernetes_pod',
    schedule=None,
    start_date=datetime(2024,5,1),
    tags=['example'],
)
def example_kubernetes_pod():
    # Define the sidecar container
    sidecar_container = k8s.V1Container(
        name='sidecar-container',
        image='python:alpine3.9',
        command=["python", "-c"],
    args=["""
import time
while True:
    print("Hello from the sidecar!")
    time.sleep(5)
"""],
    )

    main_container = k8s.V1Container(
        name="main-container",
        image="python:alpine3.9",
        command=['pip', 'list']
    )

    # Define the KPO with the sidecar container
    kpo_with_sidecar = KubernetesPodOperator(
        task_id='kpo_with_sidecar',
        image='python:alpine3.9',
        name='kpo-with-sidecar',
        full_pod_spec= k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[main_container, sidecar_container]
                    )
            )
    )

    kpo_without_sidecar = KubernetesPodOperator(
        task_id='kpo_without_sidecar',
        image='python:alpine3.9',
        name='kpo-without-sidecar',
        cmds=['pip', 'install', 'apache-airflow']
    )

dag_obj = example_kubernetes_pod()