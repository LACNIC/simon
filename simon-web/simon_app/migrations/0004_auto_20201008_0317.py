# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-08 06:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0003_auto_20201007_1507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='majesticmilliontestpoint',
            name='speedtesttestpoint_ptr',
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 8, 3, 17, 21, 75523)),
        ),
        migrations.AlterField(
            model_name='httpscheck',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 8, 3, 17, 21, 66026)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 8, 3, 17, 21, 71390)),
        ),
        migrations.AlterField(
            model_name='results',
            name='date_test',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 8, 3, 17, 21, 59310), verbose_name=b'test date'),
        ),
        migrations.DeleteModel(
            name='MajesticMillionTestPoint',
        ),
    ]