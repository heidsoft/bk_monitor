# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='data_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='\u540e\u53f0\u4fa7\u6570\u636e\u6e90id'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='result_table_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='\u540e\u53f0\u4fa7\u8868id'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='update_user',
            field=models.CharField(default=b'', max_length=50, verbose_name='\u6700\u65b0\u4fee\u6539\u4eba'),
        ),
    ]
