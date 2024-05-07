from airflow.decorators import task, dag
from datetime import datetime

@dag(
    'try_context_eg',
    start_date=datetime(2024, 4, 1),
    catchup=False,
    schedule=None
)
def try_context_eg():

    @task(
    )
    def task_1(**context):
        print(context['var']['value'].get('test_var'))
        # print(context['var']['json'].get('test_var'))
    
    t1 = task_1()
    
dg_basic = try_context_eg()