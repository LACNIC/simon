# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-21 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0013_auto_20211221_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourlybatch',
            name='status',
            field=models.CharField(choices=[(b'IP', b'In progress'), (b'ER', b'Error'), (b'FI', b'Finished')], default=b'IP', max_length=2),
        ),
    ]
