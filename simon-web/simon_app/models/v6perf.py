from django.db import models
from datetime import datetime
from models import Country


class V6PerfManager(models.Manager):


    def latest_measurements(self):
        reverse_ = V6Perf.objects.filter(
            country__in=Country.objects.get_lacnic_countrycodes()
        ).order_by(
            'country',
            '-date'
        ).distinct(
            'country'
        )
        return reverse_


class V6Perf(models.Model):
    """

    """
    date = models.DateTimeField(default=datetime.now)
    time_window = models.IntegerField(default=30)
    diff = models.FloatField(default=0.0)
    dualstack = models.FloatField(default=0.0)
    v6_rate = models.FloatField(default=0.0)
    country = models.CharField(max_length=2)

    objects = V6PerfManager()


class V6PerfMonthlyManager(models.Manager):
    def latest_measurements(self):
        reverse_ = V6PerfMonthly.objects.filter(country__in=Country.objects.get_lacnic_countrycodes()).order_by(
            'country',
            '-date').distinct(
            'country')
        return reverse_


class V6PerfMonthly(V6Perf):
    objects = V6PerfMonthlyManager()
