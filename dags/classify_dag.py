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
    'classify_dag',
    default_args=default_args,
    description='Classify news articles',
    schedule_interval=None,
)

classify_task = BashOperator(
    task_id='classify_articles',
    bash_command='/Users/phucnm/miniconda3/bin/python /Users/phucnm/git/misc/fimarin/s02_classify_article.py',
    dag=dag,
)

classify_task