#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from ._probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI LACNIC"

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(
            max_job_queue_size=10,
            max_probes=50
        )
        ccs = Country.objects.get_lacnic_countrycodes()
        results = msm.init(
            tps=["lac-connectivity.exp.dev.lacnic.net"],
            ccs=ccs
        )

        return results
