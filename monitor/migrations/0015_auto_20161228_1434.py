# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0014_auto_20161228_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataresulttable',
            name='monitor_id',
            field=models.IntegerField(default=0, verbose_name='monitor id'),
        ),
        migrations.AddField(
            model_name='dataresulttablefield',
            name='generate_config_id',
            field=models.IntegerField(default=0, verbose_name='\u5173\u8054\u7684data etl config id'),
        ),
        migrations.AddField(
            model_name='dataresulttablefield',
            name='monitor_id',
            field=models.IntegerField(default=0, verbose_name='monitor id'),
        ),
    ]
