from airflow.decorators import task, dag
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.models import Variable
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

    @task(
    )
    def t2():
        var = Variable.get('test_var_qwerty', deserialize_json=True)
        print(var)
    
    t2_obj = t2()
    
    
dg_basic = expose_env()