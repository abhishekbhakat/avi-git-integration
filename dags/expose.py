from airflow.decorators import task, dag
from airflow.operators.bash import BashOperator
from datetime import datetime
import json

@dag(
    'expose_env',
    start_date=datetime(2024, 4, 1),
    catchup=False,
    schedule=None
)
def expose_env():
    t1 = BashOperator(
        task_id='print_env',
        bash_command='env',
    )
    
    
dg_basic = expose_env()