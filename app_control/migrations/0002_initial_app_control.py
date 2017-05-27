# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core import serializers


def initial_app_control_data(apps, schema_editor):
    try:
        # 初始化功能开关数据
        func_data = [
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'func_test', 'func_name': u"示例功能"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'create_task', 'func_name': u"创建任务"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'execute_task', 'func_name': u"执行任务"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'tasks', 'func_name': u"任务列表"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'task', 'func_name': u"任务详情"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'pause_task', 'func_name': u"任务暂停"}},
            {'model': 'app_control.Function_controller', 'fields': {'func_code': 'terminate_task', 'func_name': u"任务终止"}},
        ]
        func_obj = serializers.deserialize('python', func_data, ignorenonexistent=True)
        for obj in func_obj:
            obj.save()
    except Exception, e:
        print e
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_control', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_app_control_data),
    ]
