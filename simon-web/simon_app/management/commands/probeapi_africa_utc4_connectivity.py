#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from probeapi_top28 import ping_top28
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity UTC+04:00")
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)
        ccs = ['RE', 'MU', 'SC']

        results = msm.init(
            tps=['africa-connectivity.exp.dev.lacnic.net'],
            ccs=ccs
        )

        top28_results = ping_top28(ccs)

        return results + top28_results
