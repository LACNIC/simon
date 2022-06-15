# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-09 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0010_auto_20211122_0540'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchCadaHora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probeapi_batch', models.CharField(max_length=10)),
                ('fecha_de_ejecucion', models.DateTimeField(auto_now_add=True)),
                ('fecha', models.DateTimeField()),
                ('status', models.CharField(choices=[(b'IP', b'In progress'), (b'ER', b'Error'), (b'FI', b'Finished')], max_length=2)),
            ],
        ),
        migrations.AddField(
            model_name='probeapifetchfromftp',
            name='batch',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to='simon_app.BatchCadaHora'),
            preserve_default=False,
        ),
    ]