from airflow.decorators import dag, task, task_group
from datetime import datetime

@dag(
    'ask_astro_dy_task_map',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['example']
)
def example_task_group_mapping_dag():

    @task
    def generate_string_list() -> list:
        # Generate a list of strings
        return ["string1", "string2", "string3"]

    @task_group(group_id='process_strings_group')
    def process_strings(string: str):
        @task
        def print_string(s: str):
            print(f"Processing: {s}")

        @task
        def modify_string(s: str) -> str:
            return f"Modified_{s}"

        # Define the task flow within the task group
        print_string(string)
        modified_string = modify_string(string)
        return modified_string

    # Generate the list of strings
    string_list = generate_string_list()

    # Map the task group over the list of strings
    process_strings.expand(string=string_list)

# Instantiate the DAG
dag = example_task_group_mapping_dag()