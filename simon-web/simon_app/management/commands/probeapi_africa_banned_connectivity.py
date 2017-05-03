#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity UTC+04:00")
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)
        ccs = ['RE', 'MU', 'SC']

        results = msm.init(
            tps=['africa-connectivity.exp.dev.lacnic.net']*10,
            ccs=ccs
        )

        return results
