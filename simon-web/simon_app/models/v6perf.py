from django.db import models
from datetime import datetime


class V6Perf(models.Model):
    """

    """
    date = models.DateTimeField(default=datetime.now)
    diff = models.FloatField(default=0.0)
    dualstack = models.FloatField(default=0.0)
    v6_rate = models.FloatField(default=0.0)
    country = models.CharField(max_length=2)

    class Meta:
        managed = False
