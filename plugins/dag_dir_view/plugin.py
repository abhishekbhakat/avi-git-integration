import os
from datetime import datetime, timezone

from airflow.models import DagBag
from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask import Blueprint, g, jsonify, request, url_for
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


class DagDirViewPlugin(AppBuilderBaseView):
    default_view = "dag_dir_view"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def dag_dir_view(self):
        dagbag = DagBag(read_dags_from_db=True)
        dag_folder = dagbag.dag_folder
        content = {
            "dags": [],
            "dags_folder": dag_folder,
        }
        return self.render_template("dag_dir_view.html", content=content)


v_appbuilder_view = DagDirViewPlugin()
v_appbuilder_package = {"name": "Dag Dir", "category": "Dag Dir View", "view": v_appbuilder_view}


class DagDirViewPlugin(AirflowPlugin):
    name = "DagDirViewPlugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]
