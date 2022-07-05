from datetime import datetime, timedelta
from pathlib import Path
import contextlib

import pandas as pd
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.models import Variable


# Etiq Library
import etiq

@contextlib.contextmanager
def login_using_token(host, token):
    try:
        login_result = etiq.login(host, token)
        if login_result.connected:
            yield
        else:
            raise Exception(login_result.message)
    finally:
        if login_result.connected:
            etiq.logout()

def get_datasets_latest(etiq_data, **kwargs):
    apath = Path(etiq_data) / 'latest'
    files_list = []
    for alatest in list(apath.glob('**/*.csv')):
        afile = Path(alatest)
        if afile.is_file():
            _ = afile.rename(afile.with_suffix('.csv.processing'))
            files_list.append(str(afile) + '.processing')
    kwargs['ti'].xcom_push(key='latest_dataset', value=files_list)
    print(files_list)
    return files_list

def get_dataset_base(etiq_data, **kwargs):
    apath = Path(etiq_data) / 'base'
    files = list(apath.glob('**/*.csv'))
    kwargs['ti'].xcom_push(key='base_dataset', value=str(files[0]))
    return str(files[0])

def get_dataset(dataset_filename, target_feature, sep=','):
    dataset_df = pd.read_csv(dataset_filename, header=0, sep=sep)
    dataset = etiq.SimpleDatasetBuilder.from_dataframe(dataset_df, target_feature=target_feature).build()
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
            # Scan for target drift at a global level
            (_, issues_target, _) = snapshot.scan_target_drift_metrics()
            issues_target.to_csv(alatest_name + '.target_drift_issues.txt', index=False)

    ti = kwargs['ti']
    config = etiq.load_config(config_file)
    target_feature = config['dataset']['label']
    base_dataset_filename = ti.xcom_pull(key='base_dataset', task_ids='get_base_dataset')
    latest_dataset_filenames = ti.xcom_pull(key='latest_dataset', task_ids='get_latest_datasets')
    if etiq_dashboard != '':
        with login_using_token(etiq_dashboard, etiq_token):
            run_drift_calculations()
    else:
        run_drift_calculations()

def archive_latest_files(**kwargs):
    latest_dataset_filenames = kwargs['ti'].xcom_pull(key='latest_dataset', task_ids='get_latest_datasets')
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
    etiq_dashboard = Variable.get('ETIQ_DASHBOARD')
    etiq_token = Variable.get('ETIQ_TOKEN')

    # We set up the sensor to scan every 30 seconds for new files
    latest_datafiles_sensor_task = FileSensor(task_id= "latest_datafiles_sensor_task",
                                              poke_interval= 30,
                                              filepath=str(Path(etiq_data) / 'latest/*csv'),
                                              mode='reschedule',
                                              timeout = 30 * 60,
                                              fs_conn_id="docker_fs")
    base_datafile_sensor_task = FileSensor(task_id= "base_datafile_sensor_task",
                                           poke_interval= 30,
                                           filepath=str(Path(etiq_data) / 'base/*csv'),
                                           mode='reschedule',
                                           timeout = 30 * 60,
                                           fs_conn_id="docker_fs")
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
base_and_latest_present >> [get_base_dataset, get_latest_datasets] >> calculate_drift_task >> archive_latest_files_task
