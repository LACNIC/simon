#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "Africa Connectivity [BANNED]"

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=100, max_points=50)
        ccs = ['CF', 'SO', 'SN', 'SZ', 'TD', 'ZM', 'LR', 'NE', 'YT', 'RE', 'SC', 'SD', 'LS', 'GN', 'BF', 'CD', 'CM', 'SL', 'ST', 'ET', 'BI', 'MZ', 'NA', 'TG']
        results = msm.init(
            tps=['africa-connectivity.exp.dev.lacnic.net'],
            ccs=ccs
        )

        return results
