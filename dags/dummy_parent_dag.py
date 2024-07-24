from airflow.decorators import dag, task
from datetime import datetime

@dag(
    'dummy_parent_dag',
    start_date=datetime(2024,5,8),
    catchup=False,
    schedule="30 16 * * *"
)
def dummy_parent_dag():
    @task
    def task_1():
        print('task_1')

    @task
    def task_2():
        print('task_2')

    task_1() >> task_2()

dag_obj = dummy_parent_dag()
