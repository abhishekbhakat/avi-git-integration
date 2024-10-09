from airflow.policies import hookimpl
from airflow.models import Log
from airflow import settings
from airflow.models.taskinstance import TaskInstance

@hookimpl
def task_instance_mutation_hook(task_instance: TaskInstance):
    def get_user():
        session = settings.Session()
        dag_log_entry = session.query(Log).filter(
            Log.dag_id == task_instance.dag_id,
            Log.event.in_(['trigger'])
        ).order_by(Log.dttm.desc()).first()
        
        task_log_entry = session.query(Log).filter(
            Log.dag_id == task_instance.dag_id,
            Log.task_id == task_instance.task_id,
            Log.event.in_(['clear', 'retry', 'cli_task_run'])
        ).order_by(Log.dttm.desc()).first()
        
        if task_log_entry and (not dag_log_entry or task_log_entry.dttm > dag_log_entry.dttm):
            return task_log_entry.owner if task_log_entry.owner else None
        elif dag_log_entry and dag_log_entry.owner:
            return dag_log_entry.owner if dag_log_entry.owner else None
        else:
            return None
        

    user = get_user()
    user_list = ['user1', 'user2']
    # instead of user_list implement any method to get the authorized users.
    if user not in user_list:
        print(f"User {user} is not allowed to run this task")
        task_instance.state = 'skipped'