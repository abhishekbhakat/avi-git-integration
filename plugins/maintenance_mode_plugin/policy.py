from airflow.policies import hookimpl
from airflow.models import Variable
from airflow.exceptions import AirflowSkipException, AirflowFailException
import json
from datetime import datetime

@hookimpl
def task_policy(task):
    maintenance_data = json.loads(Variable.get("maintenance_mode_plugin_var", "{}"))
    if maintenance_data:
        start_time = datetime.fromisoformat(maintenance_data['start_time'])
        end_time = datetime.fromisoformat(maintenance_data['end_time'])
        current_time = datetime.now()
        
        if start_time <= current_time <= end_time:
            if maintenance_data['task_handling'] == 'skipped':
                raise AirflowSkipException("Task skipped due to maintenance mode")
            elif maintenance_data['task_handling'] == 'failed':
                raise AirflowFailException("Task failed due to maintenance mode")
            elif maintenance_data['task_handling'] == 'success':
                task.on_success_callback = lambda context: None
                return