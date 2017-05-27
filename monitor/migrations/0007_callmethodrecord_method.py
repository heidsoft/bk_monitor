# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0006_alarmstrategy'),
    ]

    operations = [
        migrations.AddField(
            model_name='callmethodrecord',
            name='method',
            field=models.CharField(default=b'', max_length=10, verbose_name='http\u65b9\u6cd5'),
        ),
    ]
