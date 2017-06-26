#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="Brazil Connectivity")
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
