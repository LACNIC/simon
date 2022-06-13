# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simon_app', '0029_auto_20220609_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probeapiv3resultmetadata',
            name='error_msg',
            field=models.CharField(default=b'', max_length=512, null=True),
        ),
    ]
