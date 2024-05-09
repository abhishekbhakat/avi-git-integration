from airflow.decorators import dag, task
from datetime import datetime, timedelta
import pendulum
from airflow.utils.timezone import make_naive, make_aware
from airflow.sensors.external_task import ExternalTaskSensor

from airflow.models import DagRun
from airflow.utils.db import provide_session

# local_tz = pendulum.timezone("Pacific/Auckland")
def get_most_recent_dag_run_last_24_hours(execution_date, dag_id="your_external_dag_id"):
    # Calculate the time 24 hours ago from the current time
    twenty_four_hours_ago = execution_date - timedelta(hours=24)
    
    # Find the most recent DAG run for the specified DAG ID within the last 24 hours
    recent_dag_runs = DagRun.find(
        dag_id=dag_id,
        end_date=execution_date,
        start_date=twenty_four_hours_ago,
        state='success',  # Assuming you want to find successful DAG runs; remove if not needed
        no_backfills=True
    )
    
    # Sort the DAG runs by execution date in descending order and get the first one
    recent_dag_runs = sorted(recent_dag_runs, key=lambda dag_run: dag_run.execution_date, reverse=True)
    most_recent_dag_run = recent_dag_runs[0] if recent_dag_runs else None

    # Return the execution date of the most recent DAG run
    return most_recent_dag_run.execution_date if most_recent_dag_run else execution_date

# def handle_dst_transition(dt: datetime, local_tz) -> datetime:
#     print(f"utc_today is: {dt}")
#     local_time = pendulum.instance(dt).in_timezone(local_tz)
#     print(f"local_time is: {local_time}")
#     local_yesterday = make_aware(make_naive(local_time, local_tz) - timedelta(days=1), local_tz)
#     print(f"local_yesterday is: {local_yesterday}")
#     utc_yesterday = pendulum.instance(local_yesterday).in_timezone("UTC")
#     print(f"utc_yesterday is: {utc_yesterday}\n")
#     return utc_yesterday

@dag(
    'dummy_child_dag',
    start_date=datetime(2024,5,8),
    catchup=False,
    schedule="30 16 * * *"
)
def dummy_child_dag():
    task1 = ExternalTaskSensor(
        external_dag_id='dummy_parent_dag',
        external_task_id='task_1',
        task_id='task_1',
        # execution_date_fn=lambda dt: handle_dst_transition(dt, local_tz),
        execution_date_fn=get_most_recent_dag_run_last_24_hours,
        # execution_delta=timedelta(days=1),
    )

dag_obj = dummy_child_dag()