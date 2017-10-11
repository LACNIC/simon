#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "Latency Sets LACNIC"

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(
            max_job_queue_size=10
        )
        ccs = ["UY", "PE"]
        results = msm.init(
            tps=["uy-mvd-as28000.anchors.atlas.ripe.net", "191.240.3.46", "187.157.254.5"],
            ccs=ccs
        )

        return results
