# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core import serializers
from django.conf import settings
from account.models import BkUser


def initial_user_data(apps, schema_editor):
    try:
        admin_username_list = settings.ADMIN_USERNAME_LIST
        for username in admin_username_list:
            BkUser.objects.create_superuser(username)
    except Exception, e:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_user_data),
    ]
