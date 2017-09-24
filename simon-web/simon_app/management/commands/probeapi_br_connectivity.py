#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command


class Command(BaseCommand):

    command = "Brazil Connectivity"

    @timed_command(name=command)
    @probeapi(command=command)
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(
            max_job_queue_size=10
        )
        ccs = ['BR']
        results = msm.init(
            tps=["br.exp.dev.lacnic.net"],
            ccs=ccs
        )

        return results
