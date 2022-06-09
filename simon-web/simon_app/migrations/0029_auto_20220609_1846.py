# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0028_probeapiv3traceroutehop_error_msg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probeapiv3resultmetadata',
            name='time_diff',
            field=models.FloatField(max_length=255, null=True),
        ),
    ]
