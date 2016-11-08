#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="ProbeAPI AFRINIC")
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)
        afrinic_countrycodes = Country.objects.get_afrinic_countrycodes()

        results = msm.init(
            tps=SpeedtestTestPoint.objects.get_ipv4().
                filter(enabled=True).
                distinct('country').
                order_by('country').
                filter(country__in=afrinic_countrycodes),

            ccs=afrinic_countrycodes)
        return results
