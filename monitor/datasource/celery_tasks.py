# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task, task

from monitor.datasource.models import Datasource


@periodic_task(run_every=crontab(minute='*/10'))
def update_ds_status_period():
    """
    每10分钟更新一次数据源状态
    :return:
    """
    # 获取处理中的数据源
    for ds in Datasource.get_processing_ds():
        update_ds_status.delay(ds)

    # 获取已经接入的数据源
    for ds in Datasource.get_normal_ds():
        update_ds_report_status.delay(ds)


@task()
def update_ds_status(ds):
    """
    轮询数据源的接入状态
    """
    ds.update_status()


@task()
def update_ds_report_status(ds):
    """
    轮询数据源的数据上报状态
    """
    ds.update_report_status()
