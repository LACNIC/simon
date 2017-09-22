#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from probeapi_top28 import ping_top28
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from simon_app.decorators import timed


class Command(BaseCommand):

    command = "Africa Connectivity UTC+03:00"

    @timed(name=command)
    @probeapi(command=command)
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)
        ccs = ['YT', 'KM', 'DJ', 'ER', 'ET', 'KE', 'MG', 'SO', 'SD', 'TZ', 'UG']

        results = msm.init(
            tps=['africa-connectivity.exp.dev.lacnic.net'],
            ccs=ccs
        )

        top28_results = ping_top28(ccs)

        return results + top28_results
