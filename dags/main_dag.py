from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

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
    'main_news_dag',
    default_args=default_args,
    description='Main DAG to orchestrate the news workflow',
    schedule_interval='@daily',
)

trigger_crawl = TriggerDagRunOperator(
    task_id='trigger_crawl',
    trigger_dag_id='crawl_dag',
    dag=dag,
)

trigger_classify = TriggerDagRunOperator(
    task_id='trigger_classify',
    trigger_dag_id='classify_dag',
    dag=dag,
)

def check_if_sunday():
    if datetime.now().weekday() == 6:  # 6 represents Sunday
        return 'trigger_newsletter'
    return 'skip_newsletter'

branch_task = BranchPythonOperator(
    task_id='check_if_sunday',
    python_callable=check_if_sunday,
    dag=dag,
)

trigger_newsletter = TriggerDagRunOperator(
    task_id='trigger_newsletter',
    trigger_dag_id='newsletter_dag',
    dag=dag,
)

skip_newsletter = DummyOperator(
    task_id='skip_newsletter',
    dag=dag,
)

trigger_crawl >> trigger_classify >> branch_task >> [trigger_newsletter, skip_newsletter]