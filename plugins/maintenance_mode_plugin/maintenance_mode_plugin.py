from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import Blueprint
import os

# Get the directory of the current file
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

v_appbuilder_view = MaintenanceModeView()
v_appbuilder_package = {"name": "Maintenance Mode",
                        "category": "Admin",
                        "view": v_appbuilder_view}

class MaintenanceModePlugin(AirflowPlugin):
    name = "maintenance_mode_plugin"
    flask_blueprints = [bp]
    appbuilder_views = [v_appbuilder_package]