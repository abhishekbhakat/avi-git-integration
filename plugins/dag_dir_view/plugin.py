import os
from collections import defaultdict

from airflow.models import DagBag
from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask import Blueprint
from flask_appbuilder import BaseView as AppBuilderBaseView, expose

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "templates")

bp = Blueprint(
    "dag_dir_view",
    __name__,
    template_folder=template_folder,
    static_folder="static",
    static_url_path="/static/dag_dir_view",
)

def nested_defaultdict():
    return defaultdict(nested_defaultdict)

def get_dag_structure():
    structure = nested_defaultdict()
    dag_bag = DagBag(read_dags_from_db=True)
    dag_bag.collect_dags_from_db()
    dags_folder = dag_bag.dag_folder
    dags = dag_bag.dags

    for dag_id, dag in dags.items():
        rel_path = os.path.relpath(dag.fileloc, dags_folder)
        path_parts = rel_path.split(os.sep)
        current = structure
        for part in path_parts[:-1]:  # Navigate through directories
            current = current[part]
        
        filename = path_parts[-1]
        if 'dags' not in current[filename]:
            current[filename]['dags'] = []
        current[filename]['dags'].append(dag_id)

    return dict(structure)  # Convert defaultdict to regular dict

class DagDirViewPlugin(AppBuilderBaseView):
    default_view = "dag_dir_view"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def dag_dir_view(self):
        content = {
            "structure": get_dag_structure(),
        }
        return self.render_template("dag_dir_view.html", content=content)

v_appbuilder_view = DagDirViewPlugin()
v_appbuilder_package = {"name": "Dag Dir", "category": "Dag Dir View", "view": v_appbuilder_view}

class DagDirViewPlugin(AirflowPlugin):
    name = "DagDirViewPlugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]