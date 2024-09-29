from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 7),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

PYTHON_PATH = '/Users/phucnm/miniconda3/bin/python'
HOME_PATH = '/Users/phucnm/git/misc'

# Main DAG
dag = DAG(
    'news_workflow_dag',
    default_args=default_args,
    description='DAG to orchestrate the entire news workflow',
    schedule_interval='@daily',
)

# Crawl tasks
crawl_thoibaonganhang_task = BashOperator(
    task_id='crawl_thoibaonganhang',
    bash_command=f'{PYTHON_PATH} {HOME_PATH}/fimarin/s01_crawl_thoibaonganhang.py',
    dag=dag,
)

crawl_thitruongtaichinhtiente_task = BashOperator(
    task_id='crawl_thitruongtaichinhtiente',
    bash_command=f'{PYTHON_PATH} {HOME_PATH}/fimarin/s01_crawl_thitruongtaichinhtiente.py',
    dag=dag,
)

# Classify task
classify_task = BashOperator(
    task_id='classify_articles',
    bash_command=f'{PYTHON_PATH} {HOME_PATH}/fimarin/s02_classify_article.py',
    dag=dag,
)

def check_if_sunday(**context):
    execution_date = context['execution_date']
    if execution_date.weekday() == 6:  # 6 represents Sunday
        return 'generate_newsletter'
    return 'skip_newsletter'

branch_task = BranchPythonOperator(
    task_id='check_if_sunday',
    python_callable=check_if_sunday,
    provide_context=True,
    dag=dag,
)

# Newsletter task
newsletter_task = BashOperator(
    task_id='generate_newsletter',
    bash_command=f'{PYTHON_PATH} {HOME_PATH}/fimarin/s03_generate_weekly_newsletter.py',
    dag=dag,
)

skip_newsletter = EmptyOperator(
    task_id='skip_newsletter',
    dag=dag,
)

# Set up task dependencies
[crawl_thoibaonganhang_task, crawl_thitruongtaichinhtiente_task] >> classify_task >> branch_task >> [newsletter_task, skip_newsletter]