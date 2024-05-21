from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from datetime import datetime


def generate_snowflake_to_gcs_dag(dag_config: dict) -> DAG:
    dag = DAG(
        dag_id=dag_config["dag_id"],
        schedule=dag_config["schedule"],
        catchup=False,
        start_date=datetime(2024, 5, 1),
        tags=dag_config["tags"],
    )

    # Start task
    start_task = EmptyOperator(
        task_id="start_task",
        dag=dag,
    )

    # Your Snowflake and GCS connections, and create tasks as needed
    snowflake_task = SnowflakeOperator(
        task_id="snowflake_task",
        dag=dag,
        sql="""SELECT * FROM some_table;""",
        snowflake_conn_id=dag_config["template_config"]["snowflake_conn_id"],
    )

    gcs_task = GCSCreateBucketOperator(
            task_id="CreateNewBucket",
            bucket_name="test-bucket",
            storage_class="MULTI_REGIONAL",
            location="EU",
            labels={"env": "dev", "team": "airflow"},
            gcp_conn_id="airflow-conn-id",
        )

    # End task
    end_task = EmptyOperator(
        task_id="end_task",
        dag=dag,
    )

    start_task >> snowflake_task >> gcs_task >> end_task

    return dag


def generate_postgresql_to_gcs_dag(dag_config: dict) -> DAG:
    dag = DAG(
        dag_id=dag_config["dag_id"],
        schedule=dag_config["schedule"],
        catchup=False,
        start_date=datetime(2024, 5, 1),
        tags=dag_config["tags"],
    )

    # Start task
    start_task = EmptyOperator(task_id="start_task")

    # Your PostgreSQL and GCS connections, and create tasks as needed
    postgresql_task = PostgresOperator(
        task_id="postgresql_task",
        dag=dag,
        sql="""SELECT * FROM some_table;""",
        postgres_conn_id=dag_config["template_config"]["postgres_conn_id"],
    )

    gcs_task = GCSCreateBucketOperator(
            task_id="CreateNewBucket",
            bucket_name="test-bucket",
            storage_class="MULTI_REGIONAL",
            location="EU",
            labels={"env": "dev", "team": "airflow"},
            gcp_conn_id="airflow-conn-id",
        )

    # End task
    end_task = EmptyOperator(task_id="end_task", dag=dag)

    start_task >> postgresql_task >> gcs_task >> end_task

    return dag


def generate_dag(dag_config: dict) -> DAG:
    template_name = dag_config["dag_template"]

    if template_name == "SnowflakeToGCS":
        return generate_snowflake_to_gcs_dag(dag_config)
    elif template_name == "PostgreSQLToGCS":
        return generate_postgresql_to_gcs_dag(dag_config)
    else:
        raise ValueError(f"Unsupported dag_template: {template_name}")
