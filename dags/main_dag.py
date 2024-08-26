from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
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
    'main_dag',
    default_args=default_args,
    description='Main DAG to orchestrate the workflow',
    schedule_interval='@daily',
)

trigger_s01 = TriggerDagRunOperator(
    task_id='trigger_s01_crawl',
    trigger_dag_id='s01_crawl_dag',
    dag=dag,
)

trigger_s02 = TriggerDagRunOperator(
    task_id='trigger_s02_classify_title',
    trigger_dag_id='s02_classify_title_dag',
    dag=dag,
)

trigger_s03 = TriggerDagRunOperator(
    task_id='trigger_s03_crawl_content',
    trigger_dag_id='s03_crawl_content_dag',
    dag=dag,
)

trigger_s04 = TriggerDagRunOperator(
    task_id='trigger_s04_summarize_content',
    trigger_dag_id='s04_summarize_content_dag',
    dag=dag,
)

trigger_s01 >> trigger_s02 >> trigger_s03 >> trigger_s04