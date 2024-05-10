FROM quay.io/astronomer/astro-runtime:11.3.0
RUN cd plugins/submodules/my_airflow_plugin && pip install .