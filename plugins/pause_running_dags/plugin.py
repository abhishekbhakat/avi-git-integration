import os
from airflow.models import DagBag, DagModel, Variable
from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from airflow.utils.session import provide_session
from flask import Blueprint, jsonify
from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from sqlalchemy.orm import Session
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "templates")

bp = Blueprint(
    "pause_running_dags",
    __name__,
    template_folder=template_folder,
    static_folder="static",
    static_url_path="/static/pause_running_dags",
)

PAUSE_RUNNING_DAGS_VAR_KEY = 'pause_running_dags_plugin_var'

@provide_session
def get_unpaused_dags(session=None):
    unpaused_dags = session.query(DagModel.dag_id).filter(DagModel.is_paused == False).all()
    return [dag.dag_id for dag in unpaused_dags]

def get_dag_structure(dag_ids):
    structure = {}
    dag_bag = DagBag(read_dags_from_db=True)
    dag_bag.collect_dags_from_db()
    dags_folder = dag_bag.dag_folder

    for dag_id in dag_ids:
        dag = dag_bag.get_dag(dag_id)
        if dag:
            rel_path = os.path.relpath(dag.fileloc, dags_folder)
            path_parts = rel_path.split(os.sep)
            current = structure
            for part in path_parts[:-1]:  # Navigate through directories
                if part not in current:
                    current[part] = {}
                current = current[part]

            filename = path_parts[-1]
            if filename not in current:
                current[filename] = {'dags': []}
            current[filename]['dags'].append(dag_id)

    return structure

class PauseRunningDagsPlugin(AppBuilderBaseView):
    default_view = "pause_running_dags"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def pause_running_dags(self):
        paused_dags = Variable.get(PAUSE_RUNNING_DAGS_VAR_KEY, deserialize_json=True, default_var=None)
        unpaused_dags = get_unpaused_dags()
        content = {
            "paused_dags": paused_dags,
            "unpaused_dags": unpaused_dags,
            "dag_structure": get_dag_structure(unpaused_dags),
        }
        return self.render_template("pause_running_dags.html", content=content)

    @expose("/pause", methods=['POST'])
    @csrf.exempt
    @provide_session
    def pause_dags(self, session=None):
        try:
            unpaused_dags = get_unpaused_dags(session=session)
            for dag_id in unpaused_dags:
                dag = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag:
                    dag.is_paused = True
            session.commit()
            Variable.set(PAUSE_RUNNING_DAGS_VAR_KEY, json.dumps(unpaused_dags))
            return jsonify({"status": "success", "message": "All unpaused DAGs have been paused and preserved"})
        except Exception as e:
            session.rollback()
            return jsonify({"status": "error", "message": str(e)})

    @expose("/unpause", methods=['POST'])
    @csrf.exempt
    @provide_session
    def unpause_dags(self, session=None):
        try:
            paused_dags = Variable.get(PAUSE_RUNNING_DAGS_VAR_KEY, deserialize_json=True, default_var=[])
            for dag_id in paused_dags:
                dag = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag:
                    dag.is_paused = False
            session.commit()
            Variable.delete(PAUSE_RUNNING_DAGS_VAR_KEY)
            return jsonify({"status": "success", "message": "All preserved DAGs have been unpaused"})
        except Exception as e:
            session.rollback()
            return jsonify({"status": "error", "message": str(e)})

v_appbuilder_view = PauseRunningDagsPlugin()
v_appbuilder_package = {"name": "Pause Running DAGs", "category": "", "view": v_appbuilder_view}

class PauseRunningDagsPlugin(AirflowPlugin):
    name = "PauseRunningDagsPlugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]
