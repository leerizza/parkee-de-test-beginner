FROM apache/airflow:2.8.1-python3.10

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY pipeline/requirements.txt /opt/airflow/pipeline/requirements.txt
RUN pip install --no-cache-dir \
    -r /opt/airflow/pipeline/requirements.txt \
    dbt-clickhouse==1.9.8
