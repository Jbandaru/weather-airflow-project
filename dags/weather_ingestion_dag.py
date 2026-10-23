from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="weather_ingestion",
    description="Fetch San Francisco weather and store it in PostgreSQL",
    start_date=datetime(2026, 10, 23),
    schedule="*/30 * * * *",
    catchup=False,
    tags=["weather", "postgres"],
) as dag:

    fetch_and_store_weather = BashOperator(
        task_id="fetch_and_store_weather",
        bash_command="python /opt/airflow/dags/weather_pipeline.py",
        retries=2,
        retry_delay=timedelta(minutes=2),
    )
