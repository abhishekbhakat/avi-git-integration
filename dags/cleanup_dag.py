from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.utils.db_cleanup import run_cleanup

@dag(
    "cleanup",
    schedule="@daily",
    start_date=datetime(2023, 2, 18),
    catchup=False,
    tags=["Maintenance",'IMP']
)
def cleanup_dag():
    @task()
    def cleanup():
        print("Starting cleanup")
        # cleanup past 7 days
        run_cleanup(
            clean_before_timestamp = datetime.now() - timedelta(days=7),
            confirm=False,
            verbose=True,
        )
        print("Cleanup completed")
    cleanup()

dag = cleanup_dag()