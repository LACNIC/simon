# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-21 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0012_auto_20211221_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourlybatch',
            name='fecha_de_ejecucion',
            field=models.DateTimeField(),
        ),
    ]