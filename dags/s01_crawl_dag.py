from airflow import DAG
from airflow.operators.python import PythonOperator
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
    's01_crawl_dag',
    default_args=default_args,
    description='Crawl from multiple sources in parallel',
    schedule_interval='@daily',
)

def crawl_thitruongtaichinhtiente():
    # Import and run the main function from s01_crawl_thitruongtaichinhtiente.py
    from s01_crawl_thitruongtaichinhtiente import main
    main()

# Add more functions for other sources

crawl_thitruongtaichinhtiente_task = PythonOperator(
    task_id='crawl_thitruongtaichinhtiente',
    python_callable=crawl_thitruongtaichinhtiente,
    dag=dag,
)

# Add more tasks for other sources

# Set task dependencies if needed