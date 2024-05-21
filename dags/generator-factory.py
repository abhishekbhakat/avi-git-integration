import yaml
from airflow import DAG
from dag_template import generate_dag

# Load the YAML file
with open('dags/dag_metadata.yaml', 'r') as f:
    dag_config = yaml.safe_load(f)


# Iterate through each dag configuration in the YAML file
for dag_config in dag_config['dags']:
    dag_id = dag_config['dag_id']
    template_name = dag_config['dag_template']
    schedule = dag_config['schedule']
    print(f"Generating dag {dag_id} with template {template_name} and schedule {schedule}")

    dag = generate_dag(dag_config)

    globals()[dag_id] = dag