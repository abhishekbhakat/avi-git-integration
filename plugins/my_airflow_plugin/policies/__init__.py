from typing import TYPE_CHECKING

from airflow.policies import hookimpl
from airflow.exceptions import AirflowClusterPolicyViolation

if TYPE_CHECKING:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.dag import DAG

@hookimpl
def task_policy(task):
    print("Hello from task_policy")
    doc_str = "This is a test doc string"
    task.doc = doc_str

@hookimpl
def dag_policy(dag):
    """Ensure that DAG has at least one tag and skip the DAG with `only_for_beta` tag."""
    print("Hello from DAG policy")
    if not dag.tags:
        raise AirflowClusterPolicyViolation(
            f"DAG {dag.dag_id} has no tags. At least one tag required. File path: {dag.fileloc}"
        )