# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-26 11:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0008_auto_20201123_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ripeatlasprobe',
            name='prefix_v4',
            field=models.CharField(max_length=18, null=True),
        ),
        migrations.AlterField(
            model_name='ripeatlasprobe',
            name='prefix_v6',
            field=models.CharField(max_length=48, null=True),
        ),
    ]