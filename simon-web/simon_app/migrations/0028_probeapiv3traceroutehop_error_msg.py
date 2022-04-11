# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0027_probeapiv3traceroutehop_hop_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='probeapiv3traceroutehop',
            name='error_msg',
            field=models.CharField(default=b'', max_length=128, null=True),
        ),
    ]
