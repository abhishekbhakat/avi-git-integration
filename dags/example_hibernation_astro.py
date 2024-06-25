from datetime import datetime, timedelta, timezone
from requests import request

from airflow.models import DagRun
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from airflow.configuration import conf
from urllib.parse import urlparse
import os, json

DEPLOYMENT_ID = conf.get("astronomer", "casbin_deployment")
ORGANIZATION_ID = urlparse(conf.get("webserver", "base_url")).netloc.split(".")[0]
ASTRO_API_TOKEN = os.getenv("ASTRO_API_TOKEN")

default_args = {
    "owner": "Avi",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}


@dag(
    "Auto_Hibernation_Dag",
    default_args=default_args,
    schedule_interval="*/15 * * * *",
    catchup=False,
    max_active_runs=1,
    doc_md="""
DAG to hibernate deployment based on the threshold interval and deployment mode.
Requires the following environment variables to be set:
- API_TOKEN: API Token
- THRESHOLD_TIME_IN_MINS: Threshold time in minutes (default: 15)

This DAG will check if any DAGs ran in previous THRESHOLD_TIME_IN_MINS minutes. 
If no DAGs ran, it will hibernate the deployment, else will poll every 15 minutes.
""",
    tags=["example"],
)
def example_hibernation_dag():
    @task.branch(task_display_name="Check Deployment Mode 🧑🏻‍💻")
    def check_deployment_type(**context):
        url = f"https://api.astronomer.io/platform/v1beta1/organizations/{ORGANIZATION_ID}/deployments/{DEPLOYMENT_ID}"
        response = request(
            url=url,
            method="GET",
            headers={
                "Authorization": f"Bearer {ASTRO_API_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=300,
        )
        if not response.ok:
            raise Exception("Failed to fetch deployment details")
        print("Response: ", response.text)
        is_development = response.json().get("isDevelopmentMode")
        print(f"Development_mode: {is_development}")
        if is_development:
            return "check_hibernation_condition"
        else:
            return "end"

    @task.branch(task_display_name="Check Hibernation Condition ❄")
    def check_hibernation_condition():
        threshold_time_in_mins = int(os.getenv("THRESHOLD_TIME_IN_MINS", "15"))

        dag_runs = DagRun.find(
            execution_start_date=datetime.now(timezone.utc)
            - timedelta(minutes=int(threshold_time_in_mins)),
        )
        dag_runs = list(set(dag_runs).union(set(DagRun.find(state="running"))).union(set(DagRun.find(state="queued"))))
        dag_runs = [dag_run for dag_run in dag_runs if dag_run.dag_id != "hibernation_dag"]
        print(f"DAGs ran below threshold limit {threshold_time_in_mins}: {len(dag_runs)}")
        if len(dag_runs) == 0:
            return "hibernate_deployment"
        else:
            return "end"

    @task(task_id="hibernate_deployment", task_display_name="Hibernate Deployment 🛌")
    def hibernate():
        url = f"https://api.astronomer.io/platform/v1beta1/organizations/{ORGANIZATION_ID}/deployments/{DEPLOYMENT_ID}/hibernation-override"
        response = request(
            url=url,
            method="POST",
            headers={
                "Authorization": f"Bearer {ASTRO_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "isHibernating": True,
            },
            timeout=300,
        )
        print(response.status_code)
        if response.ok:
            return response.json()
        else:
            raise Exception("Failed to hibernate deployment")

    end = EmptyOperator(
        task_id="end", trigger_rule="none_failed", task_display_name="End 🏁"
    )

    check_deployment_type() >> check_hibernation_condition() >> hibernate() >> end


dag_obj = example_hibernation_dag()
