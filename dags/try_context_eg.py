from airflow.decorators import task, dag
from datetime import datetime
import json

@dag(
    'try_context_eg',
    start_date=datetime(2024, 4, 1),
    catchup=False,
    schedule=None,
    default_args={
        "retries": 1,
    }
)
def try_context_eg():

    @task(
    )
    def task_1(**context):
        from pprint import pprint
        print(context['var']['value'].get('test_var'))
        pprint(context, indent=4)
        dag_run = context['dag_run']
        print(dag_run)
        conf = dag_run.conf if dag_run else {}
        # if isinstance(conf, str):
        #     conf = json.loads(conf)
        print(conf)
        # username = conf.get('triggered_by', 'Airflow Scheduler')
        # print(f"This task was triggered by: {username}")
    
    t1 = task_1()
    
dg_basic = try_context_eg()