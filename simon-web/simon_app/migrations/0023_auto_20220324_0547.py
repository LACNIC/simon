# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-24 08:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0022_auto_20220310_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProbeApiV3DataResult',
            fields=[
                ('results_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='simon_app.Results')),
            ],
            bases=('simon_app.results',),
        ),
        migrations.CreateModel(
            name='ProbeApiV3MetaDataResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probeapi_probe_id', models.CharField(default=b'', max_length=128)),
                ('hostname', models.CharField(default=b'', max_length=128, null=True)),
                ('ipv4only', models.BooleanField(default=False)),
                ('ipv6only', models.BooleanField(default=False)),
                ('error_msg', models.CharField(default=b'', max_length=128, null=True)),
                ('server_time', models.DateTimeField(default=datetime.datetime.now)),
                ('time_diff', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProbeApiV3PingResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('packet_loss_percentage', models.FloatField(null=True)),
            ],
            options={
                'verbose_name': 'Resultado ProbeAPI v3',
                'verbose_name_plural': 'Resultados ProbeAPI v3',
            },
        ),
        migrations.AddField(
            model_name='probeapiv3pingresult',
            name='data',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='simon_app.ProbeApiV3DataResult'),
        ),
        migrations.AddField(
            model_name='probeapiv3pingresult',
            name='metadata',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='metadata_obj', to='simon_app.ProbeApiV3MetaDataResult'),
        ),
        migrations.AddField(
            model_name='probeapiv3metadataresult',
            name='probeapifetchfromftp',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='simon_app.ProbeApiFetchFromFTP'),
        )
    ]
