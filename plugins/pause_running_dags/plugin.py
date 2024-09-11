import os
from airflow.models import DagBag, DagModel
from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask import Blueprint, request, jsonify
from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from airflow.api.common.experimental import delete_dag, pause

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "templates")

bp = Blueprint(
    "pause_running_dags",
    __name__,
    template_folder=template_folder,
    static_folder="static",
    static_url_path="/static/pause_running_dags",
)

def get_running_dags():
    dag_bag = DagBag(read_dags_from_db=True)
    dag_bag.collect_dags_from_db()
    running_dags = []
    for dag_id, dag in dag_bag.dags.items():
        if dag.get_is_active():
            running_dags.append(dag_id)
    return running_dags

class PauseRunningDagsPlugin(AppBuilderBaseView):
    default_view = "pause_running_dags"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def pause_running_dags(self):
        content = {
            "running_dags": get_running_dags(),
        }
        return self.render_template("pause_running_dags.html", content=content)

    @expose("/pause", methods=['POST'])
    @csrf.exempt
    def pause_dag(self):
        dag_id = request.form.get('dag_id')
        if dag_id:
            try:
                pause.set_dag_paused(dag_id=dag_id, is_paused=True)
                return jsonify({"status": "success", "message": f"DAG {dag_id} paused successfully"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        return jsonify({"status": "error", "message": "No DAG ID provided"})

v_appbuilder_view = PauseRunningDagsPlugin()
v_appbuilder_package = {"name": "Pause Running DAGs", "category": "", "view": v_appbuilder_view}

class PauseRunningDagsPlugin(AirflowPlugin):
    name = "PauseRunningDagsPlugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]
