# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-22 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0017_auto_20211222_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probeapifetchfromftp',
            name='timestamp',
            field=models.BigIntegerField(null=True),
        ),
    ]