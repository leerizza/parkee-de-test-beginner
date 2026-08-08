"""Parkee POS ELT: extract+load Postgres -> ClickHouse raw, then dbt run + test."""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PIPELINE_DIR = "/opt/airflow/pipeline"
DBT_DIR = "/opt/airflow/dbt"


def run_extract_load():
    import sys

    sys.path.insert(0, PIPELINE_DIR)
    from main import main as run_pipeline

    run_pipeline()


with DAG(
    dag_id="parkee_elt_dag",
    description="Extract+load OLTP data into ClickHouse raw, then run dbt transformations.",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["parkee", "elt"],
) as dag:
    extract_load_python = PythonOperator(
        task_id="extract_load_python",
        python_callable=run_extract_load,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
    )

    extract_load_python >> dbt_run >> dbt_test
