from airflow.decorators import dag, task
from pendulum import datetime


@dag(
    'dump_conn_var',
    start_date=datetime(2024, 4, 1),
    catchup=False,
    schedule=None,
    tags=["example"]
)
def dump_conn_var():

    @task
    def task_1():
        import json
        from airflow.settings import Session
        from airflow.models import Connection, Variable
        from airflow.providers.amazon.aws.fs.s3 import S3Hook
        session = Session()

        conns = session.query(Connection).all()
        vars = session.query(Variable).all()

        cons_json = [{"conn_id": conn.conn_id, "conn_type": conn.conn_type, "host": conn.host, "port": conn.port, "login": conn.login, "password": conn.password, "schema": conn.schema, "extra": json.loads(conn.extra) if not conn.extra == "" else {}} for conn in conns]
        vars_json = [{"key": var.key, "val": var.val, "description": var.description} for var in vars]
        print(json.dumps(cons_json, indent=4))
        print(json.dumps(vars_json, indent=4))
        hk = S3Hook(aws_conn_id="aws_default")
        hk.load_string(
            string_data = json.dumps(cons_json, indent=4), 
            key = "Airflow_connections",
            bucket_name = "some-bucket",
            replace=True
        )
        hk.load_string(
            string_data = json.dumps(vars_json, indent=4),
            key = "Airflow_variables",
            bucket_name = "some-bucket",
            replace=True
        )


    t1 = task_1()

dag_obj = dump_conn_var()