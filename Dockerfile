FROM quay.io/astronomer/astro-runtime:11.5.0
RUN cd plugins/my_airflow_plugin && pip install .