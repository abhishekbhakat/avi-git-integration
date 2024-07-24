from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from pendulum import datetime

months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MONTHLY_CONSUMER_DATASETS = [Dataset(f"file:///datasets/monthly_consumer_{month}") for month in months]

md = """This DAG demonstrates the production of multiple datasets based on certain condition."""

@dag(
    'datasets_producer_dag',
    start_date=datetime(2024, 7, 24),
    schedule=None,
    catchup=False,
    tags=['multi_dataset_handling'],
    doc_md=md,
)
def datasets_producer_dag():

    @task
    def throw_list_of_months():
        # Apply any logic to select the months
        return ["jan", "feb", "mar"]

    def dataset_producer_task():

        return

    def check_month(month, months):
        if month in months:
            return month

    t1 = throw_list_of_months()

    for i in months:

        branch_task = BranchPythonOperator(
            task_id=f"branch_task_{i}",
            python_callable=check_month,
            op_args=[i, "{{ task_instance.xcom_pull(task_ids='throw_list_of_months') }}"],
        )

        python_task = EmptyOperator(
            task_id=i,
            outlets = [Dataset(f"file:///datasets/monthly_consumer_{i}")],
        )

        t1 >> branch_task >> python_task

datasets_producer_dag()
