from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint, request, render_template
from airflow.www.app import csrf
from datetime import datetime

bp = Blueprint(
    "maintenance_mode",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/maintenance_mode",
)

@bp.route("/maintenance", methods=["GET", "POST"])
@csrf.exempt
def maintenance_mode():
    if request.method == "POST":
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        task_handling = request.form.get("task_handling")
        # Process the form data here
    
    return render_template("maintenance_mode_form.html")

class MaintenanceModePlugin(AirflowPlugin):
    name = "maintenance_mode_plugin"
    flask_blueprints = [bp]
    appbuilder_menu_items = [
        {
            "name": "Maintenance Mode",
            "category": "Admin",
            "category_icon": "fa-wrench",
            "href": "/maintenance",
        }
    ]