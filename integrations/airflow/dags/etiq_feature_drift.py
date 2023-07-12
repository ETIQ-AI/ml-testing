from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

# Etiq Library
import etiq
import pandas as pd
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
# Operators
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import \
    SlackWebhookOperator
from airflow.sensors.filesystem import FileSensor
from etiq import SimpleDatasetBuilder

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG


def slack_webhook_defined() -> bool:
    # Get the slack webhook from the environment
    SLACK_WEBHOOK = Variable.get('ETIQ_SLACK_WEBHOOK', default_var="")
    return SLACK_WEBHOOK != ""

def slack_feature_drift_alert(issue: Tuple,
                              webhook_conn_id: str = "etiq_slack",
                              **context) -> None:
    '''
         Sends slack alert using the provided connection id
    '''
    slack_webhook_token = (BaseHook.get_connection(webhook_conn_id)
                                    .password)
    slack_msg = f"""
        :x: Feature Drift Issue.
        *Feature*: {issue["feature"]}
        *Task*: {context.get('task_instance').task_id}
        *Dag*: {context.get('task_instance').dag_id}
        *Execution Time*: {context.get('execution_date')}
        <{context.get('task_instance').log_url}|*Logs*>
    """
    slack_alert = SlackWebhookOperator(
        task_id='slack_issue',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow',
        slack_webhook_conn_id="etiq_slack"
    )
    return slack_alert.execute(context=context)

def get_datasets_latest(etiq_data, **kwargs):
    apath = Path(etiq_data) / 'latest'
    files_list = []
    for alatest in list(apath.glob('**/*.csv')):
        afile = Path(alatest)
        if afile.is_file():
            _ = afile.rename(afile.with_suffix('.csv.processing'))
            files_list.append(str(afile) + '.processing')
    kwargs['ti'].xcom_push(key='latest_dataset', value=files_list)
    # Log list of files
    print(f"Latest Datasets = {files_list}")
    return files_list

def get_dataset_base(etiq_data, **kwargs):
    apath = Path(etiq_data) / 'base'
    files = list(apath.glob('**/*.csv'))
    kwargs['ti'].xcom_push(key='base_dataset', value=str(files[0]))
    # Log base dataset
    print(f"Base Dataset = '{files[0]}'")
    return str(files[0])

def get_dataset(dataset_filename, target_feature):
    dataset_df = pd.read_csv(dataset_filename)
    dataset = SimpleDatasetBuilder.dataset(features=dataset_df,
                                           label=target_feature)
    return dataset

def calculate_drift(etiq_project, etiq_dashboard, etiq_token, config_file, **kwargs):
    def run_drift_calculations():
        project = etiq.projects.open(name=etiq_project)
        base_dataset = get_dataset(base_dataset_filename, target_feature)
        i = 1
        for alatest in latest_dataset_filenames:
            alatest_name = '.'.join(alatest.split('.')[:-1])
            latest_dataset = get_dataset(alatest, target_feature)
            #Create snapshot
            snapshot = project.snapshots.create(name=f'Snapshot Base {i}',
                                                dataset=base_dataset,
                                                comparison_dataset=latest_dataset,
                                                model=None,
                                                stage=etiq.SnapshotStage.PRODUCTION)
            # Scan for feature drift at a global level
            (_, issues, _) = snapshot.scan_drift_metrics()
            issues.to_csv(alatest_name + '.feature_drift_issues.txt', index=False)
            if slack_webhook_defined():
                for _,aissue in issues.iterrows():
                    slack_feature_drift_alert(issue=aissue,
                                              webhook_conn_id="etiq_slack",
                                              **kwargs)
            # Scan for target drift at a global level
            (_, issues_target, _) = snapshot.scan_target_drift_metrics()
            issues_target.to_csv(alatest_name + '.target_drift_issues.txt', index=False)

    ti = kwargs['ti']
    config = etiq.load_config(config_file)
    target_feature = config['dataset']['label']
    base_dataset_filename = ti.xcom_pull(key='base_dataset',
                                         task_ids='get_base_dataset')
    latest_dataset_filenames = ti.xcom_pull(key='latest_dataset',
                                            task_ids='get_latest_datasets')
    if etiq_dashboard != '':
        with etiq.login_using_token(etiq_dashboard, etiq_token):
            run_drift_calculations()
    else:
        run_drift_calculations()

def archive_latest_files(**kwargs):
    latest_dataset_filenames = kwargs['ti'].xcom_pull(key='latest_dataset',
                                                      task_ids='get_latest_datasets')
    for alatest in latest_dataset_filenames:
        afile = Path(alatest)
        if afile.is_file():
            _ = afile.rename(afile.with_suffix('.processed'))


with DAG(dag_id="etiq_drift_example", # Dag id
    description='An example feature drift detection DAG using Etiq',
    schedule_interval="@hourly",
    default_args={
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "start_date": datetime(2022, 7, 4),
    },
    catchup=False,
    tags=['etiq'],
) as dag:
    # Get environment variables
    etiq_configfile = Variable.get('ETIQ_CONFIG')
    etiq_data = Variable.get('ETIQ_DATA')
    etiq_project = Variable.get('ETIQ_PROJECT')
    etiq_dashboard = Variable.get('ETIQ_DASHBOARD', default_var = '')
    etiq_token = Variable.get('ETIQ_TOKEN', default_var='')

    # We set up the sensor to scan every 30 seconds for new files
    latest_datafiles_sensor_task = (
        FileSensor(task_id= "latest_datafiles_sensor_task",
                   poke_interval= 30,
                   filepath=str(Path(etiq_data) / 'latest/*csv'),
                   mode='reschedule',
                   timeout = 30 * 60,
                   fs_conn_id="etiq_fs")
    )
    base_datafile_sensor_task = (
        FileSensor(task_id= "base_datafile_sensor_task",
                   poke_interval= 30,
                   filepath=str(Path(etiq_data) / 'base/*csv'),
                   mode='reschedule',
                   timeout = 30 * 60,
                   fs_conn_id="etiq_fs")
    )
    base_and_latest_present = EmptyOperator(
            task_id="base_and_latest_present"
        )

    get_base_dataset = PythonOperator(task_id="get_base_dataset",
                                      python_callable=get_dataset_base,
                                      provide_context=True,
                                      op_kwargs={"etiq_data": etiq_data})
    get_latest_datasets = PythonOperator(task_id="get_latest_datasets",
                                          python_callable=get_datasets_latest,
                                          provide_context=True,
                                          op_kwargs={"etiq_data": etiq_data})
    calculate_drift_task = PythonOperator(task_id="calculate_drift",
                                          python_callable=calculate_drift,
                                          provide_context=True,
                                          op_kwargs={"etiq_project": etiq_project,
                                                     "etiq_dashboard": etiq_dashboard,
                                                     "etiq_token": etiq_token,
                                                     "config_file": etiq_configfile})
    archive_latest_files_task = PythonOperator(task_id="archive_latest_files",
                                          python_callable=archive_latest_files,
                                          provide_context=True)

[latest_datafiles_sensor_task, base_datafile_sensor_task] >> base_and_latest_present
(base_and_latest_present >> [get_base_dataset, get_latest_datasets] >>
 calculate_drift_task >> archive_latest_files_task)
