# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_auto_20161123_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='status',
            field=models.CharField(default=b'normal', max_length=20, verbose_name='\u6570\u636e\u6e90\u72b6\u6001', choices=[(b'normal', '\u6b63\u5e38'), (b'stopped', '\u505c\u7528'), (b'process', '\u63a5\u5165\u4e2d'), (b'failed', '\u63a5\u5165\u5931\u8d25')]),
        ),
    ]
