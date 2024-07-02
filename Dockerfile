FROM quay.io/astronomer/astro-runtime:11.6.0
RUN cd plugins/maintenance_mode_plugin && pip install .
