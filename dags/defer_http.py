from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
}

with DAG(
    dag_id='deferrable_http_operator_dag',
    default_args=default_args,
    schedule=None,
    start_date=datetime(2024, 10, 1),
    catchup=False,
) as dag:

    fetch_data = HttpOperator(
        task_id='fetch_data',
        method='GET',
        http_conn_id='my_http_conn',
        endpoint='api/v1/data',
        headers={"Content-Type": "application/json"},
        log_response=True,
        deferrable=True,  # Enable deferrable
        response_check=lambda response: response.status_code == 200,
    )

    fetch_sensor = HttpSensor(
        task_id='fetch_sensor',
        http_conn_id='my_http_conn',
        endpoint='api/v1/data',
        poke_interval=5,
        response_check=lambda response: response.status_code == 200,
        deferrable= True,  # Enable deferrable
    )

fetch_data