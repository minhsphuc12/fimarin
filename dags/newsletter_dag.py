from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'newsletter_dag',
    default_args=default_args,
    description='Generate weekly newsletter',
    schedule_interval=None,  # Remove schedule_interval
)

newsletter_task = BashOperator(
    task_id='generate_newsletter',
    bash_command='/Users/phucnm/miniconda3/bin/python /Users/phucnm/git/misc/fimarin/s03_generate_weekly_newsletter.py',
    dag=dag,
)

newsletter_task