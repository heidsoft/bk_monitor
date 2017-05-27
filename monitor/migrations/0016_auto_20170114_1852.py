# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0015_auto_20161228_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmstrategy',
            name='alarm_solution_config',
            field=models.TextField(default=b'{}', verbose_name='\u81ea\u52a8\u5904\u7406\u914d\u7f6e'),
        ),
        migrations.AlterField(
            model_name='agentstatus',
            name='status',
            field=models.CharField(default=b'create', max_length=20, verbose_name='agent\u72b6\u6001', choices=[(b'create', '\u63a5\u5165\u4e2d'), (b'stop', '\u505c\u7528\u4e2d'), (b'normal', '\u6b63\u5e38'), (b'stopped', '\u505c\u7528'), (b'exception', '\u5f02\u5e38'), (b'delete', '\u5254\u9664\u4e2d')]),
        ),
    ]
