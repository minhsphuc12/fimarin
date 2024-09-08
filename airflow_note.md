# Apache Airflow Notes

## Installation

# Install Airflow using pip
pip install apache-airflow

# Initialize the Airflow database
airflow db init

# Create an admin user
airflow users create \
    --username phucnguyen \
    --firstname phuc \
    --lastname nguyen \
    --role Admin \
    --password phucnguyen \
    --email phucnm2.ec@gmail.com


## Starting Airflow

# Start the web server on background
airflow webserver --port 8080 -D

export AIRFLOW__CORE__DAGS_FOLDER=/Users/phucnm/git/misc/fimarin/dags

# go to airflow home page: 
http://localhost:8080/

# Start the scheduler
airflow scheduler -D

## DAG and Task Commands

# List all DAGs
airflow dags list

# List tasks in a DAG
airflow tasks list <dag_id>

# Test a specific task
airflow tasks test <dag_id> <task_id> <execution_date>

# Trigger a DAG run
airflow dags trigger <dag_id>

# Pause a DAG
airflow dags pause <dag_id>

# Unpause a DAG
airflow dags unpause <dag_id>

## Airflow CLI

# View all CLI commands
airflow --help

# Get help for a specific command
airflow <command> --help

## Configuration

# View the current configuration
airflow config list

# Get the value of a specific configuration option
airflow config get-value <section> <key>

## Connections

# List all connections
airflow connections list

# Add a new connection
airflow connections add <conn_id> \
    --conn-type <conn_type> \
    --conn-host <host> \
    --conn-login <login> \
    --conn-password <password> \
    --conn-schema <schema>

# Delete a connection
airflow connections delete <conn_id>

## Variables

# Set a variable
airflow variables set <key> <value>

# Get a variable
airflow variables get <key>

# List all variables
airflow variables list

# Delete a variable
airflow variables delete <key>

## Debugging

# Print the list of active DAG runs
airflow dags state-of-dags

# Show DAG dependencies
airflow dags show <dag_id>

# Render a task's template
airflow tasks render <dag_id> <task_id> <execution_date>

## Cleanup

# delete all DAGs
airflow dags delete --all

# Clear task instances for a DAG
airflow tasks clear <dag_id>

# Clear task instances for a specific task
airflow tasks clear <dag_id> -t <task_id>

## Airflow Database

# Upgrade the metadata database to the latest version
airflow db upgrade

# Reset the metadata database
airflow db reset

## Plugins

# List all plugins
airflow plugins list

## Logs

# View logs for a specific task instance
airflow tasks logs <dag_id> <task_id> <execution_date>

## Best Practices

1. Use Airflow's built-in operators when possible
2. Implement proper error handling and retries
3. Use Jinja templating for dynamic configuration
4. Organize DAGs into meaningful groups
5. Use default_args for common configurations
6. Implement proper logging
7. Use Airflow variables and connections for sensitive information
8. Test DAGs thoroughly before deploying to production
9. Monitor Airflow performance and optimize as needed
10. Keep DAGs idempotent and atomic