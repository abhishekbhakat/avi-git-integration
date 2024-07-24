FROM quay.io/astronomer/astro-runtime:11.6.0
RUN cd plugins/maintenance_mode_plugin && pip install .
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-postgres && deactivate
# RUN mv /usr/local/airflow/dags/dbt/.dbt /home/astro