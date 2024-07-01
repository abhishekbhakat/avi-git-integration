from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import Blueprint, request, jsonify, url_for, g
from airflow.models import Variable
import os
import json
from datetime import datetime, timezone

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "templates")

bp = Blueprint(
    "maintenance_mode",
    __name__,
    template_folder=template_folder,
    static_folder="static",
    static_url_path="/static/maintenance_mode",
)

class MaintenanceModeView(AppBuilderBaseView):
    default_view = "maintenance"
    template_folder = template_folder

    @expose("/")
    @csrf.exempt
    def maintenance(self):
        maintenance_data = json.loads(Variable.get("maintenance_mode_plugin_var", "{}"))
        return self.render_template(
            "maintenance_mode_form.html",
            maintenance_data=maintenance_data
        )

    @expose("/api/set_maintenance", methods=["POST"])
    @csrf.exempt
    def set_maintenance(self):
        data = request.json
        maintenance_data = {
            "start_time": datetime.fromisoformat(data.get("start_time")).astimezone(timezone.utc).isoformat(),
            "end_time": datetime.fromisoformat(data.get("end_time")).astimezone(timezone.utc).isoformat(),
            "task_handling": data.get("task_handling")
        }
        
        Variable.set("maintenance_mode_plugin_var", json.dumps(maintenance_data))
        
        return jsonify({
            "status": "success", 
            "message": "Maintenance mode set successfully", 
            "redirect": url_for('Airflow.index')
        })

v_appbuilder_view = MaintenanceModeView()
v_appbuilder_package = {"name": "Maintenance Mode",
                        "category": "Admin",
                        "view": v_appbuilder_view}

class MaintenanceModePlugin(AirflowPlugin):
    name = "maintenance_mode_plugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]

    @staticmethod
    def before_request():
        maintenance_data = json.loads(Variable.get("maintenance_mode_plugin_var", "{}"))
        g.maintenance_mode = maintenance_data if maintenance_data else None