FROM quay.io/astronomer/astro-runtime:12.1.0
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-postgres && deactivate
# RUN mv /usr/local/airflow/dags/dbt/.dbt /home/astro