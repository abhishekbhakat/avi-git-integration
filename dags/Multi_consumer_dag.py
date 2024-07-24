from airflow.datasets import Dataset
from airflow.decorators import dag, task
from pendulum import datetime

months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MONTHLY_CONSUMER_DATASETS = [Dataset(f"file:///datasets/monthly_consumer_{month}") for month in months]

# creating bitwise OR of all datasets
schedule_datasets = MONTHLY_CONSUMER_DATASETS[0]
for dataset in MONTHLY_CONSUMER_DATASETS[1:]:
    schedule_datasets |= dataset

@dag(
    dag_id="datasets_consumer_dag",
    start_date=datetime(2024, 7, 24),
    schedule=schedule_datasets,
    catchup=False,
    tags=['multi_dataset_handling'],
)
def datasets_consumer_dag():
    @task
    def read_dataset_events_map(triggering_dataset_events):
        print("Reading about cocktails")
        print("Length of triggering_dataset_events", len(triggering_dataset_events))
        months = []
        for dataset, dataset_list in triggering_dataset_events.items():
            print(dataset, dataset_list)
            source_task_id = dataset_list[0].source_task_id
            months.append(source_task_id)
        return months



    @task
    def single_consumer_action(month):
        print("Single consumer action for month", month)

    single_consumer_action.expand(month=read_dataset_events_map())


dg_obj = datasets_consumer_dag()
