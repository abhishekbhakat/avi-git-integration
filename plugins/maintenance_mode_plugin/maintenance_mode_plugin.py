from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import Blueprint, request, jsonify, redirect, url_for
from airflow.models import Variable
from flask import g
import os
import json

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
        return self.render_template("maintenance_mode_form.html")

    @expose("/api/set_maintenance", methods=["POST"])
    @csrf.exempt
    def set_maintenance(self):
        data = request.json
        maintenance_data = {
            "start_time": data.get("start_time"),
            "end_time": data.get("end_time"),
            "task_handling": data.get("task_handling")
        }
        
        Variable.set("maintenance_mode_plugin_var", json.dumps(maintenance_data))
        
        return jsonify({"status": "success", "message": "Maintenance mode set successfully", "redirect": url_for('/')})

v_appbuilder_view = MaintenanceModeView()
v_appbuilder_package = {"name": "Maintenance Mode",
                        "category": "Admin",
                        "view": v_appbuilder_view}

class MaintenanceModePlugin(AirflowPlugin):
    name = "maintenance_mode_plugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]

    # Add this method to inject maintenance mode data into all templates
    @staticmethod
    def before_request():
        maintenance_data = json.loads(Variable.get("maintenance_mode_plugin_var", "{}"))
        g.maintenance_mode = maintenance_data if maintenance_data else None