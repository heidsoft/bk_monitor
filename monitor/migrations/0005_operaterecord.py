# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_callmethodrecord_datagenerateconfig_dataresulttable_dataresulttablefield_monitorhoststicky'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperateRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('biz_id', models.IntegerField(default=0, verbose_name='\u4e1a\u52a1cc_id')),
                ('config_type', models.CharField(max_length=32, verbose_name='\u914d\u7f6e\u7c7b\u578b')),
                ('config_id', models.IntegerField(verbose_name='\u64cd\u4f5cconfig_id')),
                ('config_title', models.CharField(default=b'', max_length=512, verbose_name='\u914d\u7f6e\u6807\u9898')),
                ('operator', models.CharField(max_length=32, verbose_name='\u64cd\u4f5c\u4eba')),
                ('operator_name', models.CharField(default=b'', max_length=32, verbose_name='\u64cd\u4f5c\u4eba\u6635\u79f0')),
                ('operate', models.CharField(max_length=32, verbose_name='\u5177\u4f53\u64cd\u4f5c')),
                ('operate_time', models.DateTimeField(auto_now_add=True, verbose_name='\u64cd\u4f5c\u65f6\u95f4')),
                ('data', models.TextField(verbose_name='\u6570\u636e(JSON)')),
                ('data_ori', models.TextField(default=b'{}', verbose_name='\u4fee\u6539\u524d\u6570\u636e(JSON)')),
                ('operate_desc', models.TextField(default=b'', verbose_name='\u64cd\u4f5c\u8bf4\u660e')),
            ],
            options={
                'verbose_name': '\u64cd\u4f5c\u8bb0\u5f55',
                'verbose_name_plural': '\u64cd\u4f5c\u8bb0\u5f55',
            },
        ),
    ]
