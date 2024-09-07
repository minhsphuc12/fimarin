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
    'crawl_dag',
    default_args=default_args,
    description='Crawl news from multiple sources',
    schedule_interval=None,
)

crawl_thoibaonganhang_task = BashOperator(
    task_id='crawl_thoibaonganhang',
    bash_command='/Users/phucnm/miniconda3/bin/python /Users/phucnm/git/misc/fimarin/s01_crawl_thoibaonganhang.py',
    dag=dag,
)

crawl_thitruongtaichinhtiente_task = BashOperator(
    task_id='crawl_thitruongtaichinhtiente',
    bash_command='/Users/phucnm/miniconda3/bin/python /Users/phucnm/git/misc/fimarin/s01_crawl_thitruongtaichinhtiente.py',
    dag=dag,
)

[crawl_thoibaonganhang_task, crawl_thitruongtaichinhtiente_task]