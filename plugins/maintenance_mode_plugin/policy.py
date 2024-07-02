from airflow.policies import hookimpl
from airflow.models import Variable
from airflow.operators.python import PythonOperator
import json
from datetime import datetime, timezone
from airflow.exceptions import AirflowSkipException

def maintenance_task_failed(**context):
    raise Exception("Task failed due to maintenance window")

def maintenance_task_skipped(**context):
    raise AirflowSkipException("Task skipped due to maintenance window")

def maintenance_task_success(**context):
    print("Task marked as success due to maintenance window")

@hookimpl
def dag_policy(dag):
    maintenance_data = json.loads(Variable.get("maintenance_mode_plugin_var", "{}"))
    if maintenance_data:
        start_time = datetime.fromisoformat(maintenance_data['start_time']).replace(tzinfo=timezone.utc)
        end_time = datetime.fromisoformat(maintenance_data['end_time']).replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        
        if start_time <= current_time <= end_time:
            for task_id, task in dag.task_dict.copy().items():
                if maintenance_data['task_handling'] == 'skipped':
                    new_task = PythonOperator(
                        task_id=task_id,
                        python_callable=maintenance_task_skipped,
                    )
                elif maintenance_data['task_handling'] == 'failed':
                    new_task = PythonOperator(
                        task_id=task_id,
                        python_callable=maintenance_task_failed,
                    )
                elif maintenance_data['task_handling'] == 'success':
                    new_task = PythonOperator(
                        task_id=task_id,
                        python_callable=maintenance_task_success,
                    )
                
                if hasattr(task, 'doc') and isinstance(task.doc, property):
                    new_task.doc_md = "Task Overridden due to Maintenance Window"
                else:
                    new_task.doc = "Task Overridden due to Maintenance Window"
                
                if hasattr(task, '_upstream_task_ids'):
                    new_task._upstream_task_ids = task._upstream_task_ids.copy()
                if hasattr(task, '_downstream_task_ids'):
                    new_task._downstream_task_ids = task._downstream_task_ids.copy()

                dag.task_dict[task_id] = new_task
                dag.task_dict[task_id].dag = dag