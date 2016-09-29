#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="ProbeAPI APNIC")
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement()
        apnic_countrycodes = Country.objects.get_apnic_countrycodes()
        results = msm.init(
            tps=SpeedtestTestPoint.objects.get_ipv4().
                filter(enabled=True).
                distinct('country').
                order_by('country').
                filter(country__in=apnic_countrycodes),

            ccs=apnic_countrycodes
        )
        return results
