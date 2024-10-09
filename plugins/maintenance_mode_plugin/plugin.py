import os
from datetime import datetime, timezone

from airflow.models import Variable, DagModel
from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask import Blueprint, g, jsonify, request, url_for
from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from sqlalchemy.orm import Session
from airflow.utils.session import provide_session

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "templates")

bp = Blueprint(
    "maintenance_mode",
    __name__,
    template_folder=template_folder,
    static_folder="static",
    static_url_path="/static/maintenance_mode",
)

@provide_session
def get_unpaused_dags(session=None):
    unpaused_dags = session.query(DagModel.dag_id).filter(DagModel.is_paused == False).all()
    return [dag.dag_id for dag in unpaused_dags]

class MaintenanceModeView(AppBuilderBaseView):
    default_view = "maintenance"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def maintenance(self):
        maintenance_data = Variable.get("maintenance_mode_plugin_var", deserialize_json=True, default_var="")
        if maintenance_data:
            maintenance_data["start_time"] = maintenance_data["start_time"].split("+")[0]
            maintenance_data["end_time"] = maintenance_data["end_time"].split("+")[0]
        unpaused_dags = get_unpaused_dags()
        return self.render_template("maintenance_mode_form.html", maintenance_data=maintenance_data, unpaused_dags=unpaused_dags)

    @expose("/api/set_maintenance", methods=["POST"])
    @csrf.exempt
    def set_maintenance(self):
        data = request.json
        maintenance_data = {
            "start_time": datetime.fromisoformat(data.get("start_time")).astimezone(timezone.utc).isoformat(),
            "end_time": datetime.fromisoformat(data.get("end_time")).astimezone(timezone.utc).isoformat(),
            "task_handling": data.get("task_handling"),
        }

        Variable.set("maintenance_mode_plugin_var", maintenance_data, serialize_json=True)

        return jsonify({"status": "success", "message": "Maintenance window set successfully", "redirect": url_for("Airflow.index")})

    @expose("/api/shut_maintenance", methods=["POST"])
    @csrf.exempt
    def shut_maintenance(self):
        Variable.delete("maintenance_mode_plugin_var")

        return jsonify({"status": "success", "message": "Maintenance window shut successfully"})


v_appbuilder_view = MaintenanceModeView()
v_appbuilder_package = {"name": "Maintenance Mode", "category": "Custom Plugins", "view": v_appbuilder_view}


class MaintenanceModePlugin(AirflowPlugin):
    name = "maintenance_mode_plugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]

    @staticmethod
    def before_request():
        g.maintenance_mode = Variable.get("maintenance_mode_plugin_var", deserialize_json=True)
