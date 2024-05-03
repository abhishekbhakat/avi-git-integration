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
        image='python:alpine3.9',
        command=["python", "-c"],
    args=["""
import subprocess
import time

def tally_active_processes():
    try:
        output = subprocess.check_output(['ps', '-auxfh'])
        output_str = output.decode('utf-8')
        lines = output_str.strip().split('\\n')
        active_processes = len(lines) - 1
        print(f"Number of active processes: {active_processes}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'ps' command: {e}")

while True:
    tally_active_processes()
    time.sleep(5)
"""],
    )

    main_container = k8s.V1Container(
        name="main-container",
        image="python:alpine3.9",
        command=['pip', 'install', 'apache-airflow']
    )

    # Define the KPO with the sidecar container
    kpo_with_sidecar = KubernetesPodOperator(
        task_id='kpo_with_sidecar',
        image='python:alpine3.9',
        name='kpo-with-sidecar',
        full_pod_spec= k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[sidecar_container, main_container]
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