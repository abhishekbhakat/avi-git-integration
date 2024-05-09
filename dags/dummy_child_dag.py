from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.sensors.external_task import ExternalTaskSensor

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
        mode='reschedule',
        execution_delta=timedelta(days=1)
    )

dag_obj = dummy_child_dag()