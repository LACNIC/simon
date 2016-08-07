#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from simon_app.models import SpeedtestTestPoint, Country
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement()
        apnic_countrycodes = Country.objects.get_apnic_countrycodes()
        msm.init(tps=SpeedtestTestPoint.objects.get_ipv4().
                 filter(enabled=True).
                 distinct('country').
                 order_by('country').
                 filter(country__in=apnic_countrycodes),

                 ccs=apnic_countrycodes)