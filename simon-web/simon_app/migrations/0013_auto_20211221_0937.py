# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-21 12:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0012_auto_20211221_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourlybatch',
            name='probeapi_batch_fecha',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
