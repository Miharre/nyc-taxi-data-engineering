from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

# Optional deployment example. Airflow is intentionally not required for the
# laptop quick-start; this DAG schedules the same tested end-to-end entry point.
with DAG(
    "nyc_taxi_monthly_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 5 * *",
    catchup=False,
    tags=["portfolio", "data-engineering"],
) as dag:
    run_pipeline = BashOperator(
        task_id="run_end_to_end_pipeline",
        bash_command=(
            "cd /opt/project && python -m src.pipeline "
            "--year {{ data_interval_start.year }} "
            "--month {{ data_interval_start.month }}"
        ),
    )
