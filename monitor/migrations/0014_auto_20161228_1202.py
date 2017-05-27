# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0013_auto_20161227_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataresulttable',
            name='generate_config_id',
            field=models.IntegerField(serialize=False, verbose_name='\u5173\u8054\u7684data etl config id', primary_key=True),
        ),
    ]
