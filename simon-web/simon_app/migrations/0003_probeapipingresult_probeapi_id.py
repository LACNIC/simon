# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-22 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0002_probeapirequest_test_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='probeapipingresult',
            name='probeapi_id',
            field=models.CharField(default=b'', max_length=128),
        ),
    ]
