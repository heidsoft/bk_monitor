# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial_user_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bkuser',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='\u90ae\u7bb1', blank=True),
        ),
    ]
