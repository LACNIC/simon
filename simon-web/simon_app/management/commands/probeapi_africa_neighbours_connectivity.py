#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity [BANNED]")
    def handle(self, *args, **options):
        msm = ProbeApiMeasurement(max_job_queue_size=100, max_points=50)
        ccs = ['CF', 'SO', 'SN', 'SZ', 'TD', 'ZM', 'LR', 'NE', 'YT', 'RE', 'SC', 'SD', 'LS', 'GN', 'BF', 'CD', 'CM', 'SL', 'ST', 'ET', 'BI', 'MZ', 'NA', 'TG']
        results = msm.init(
            tps=['africa-connectivity.exp.dev.lacnic.net'],
            ccs=ccs
        )

        return results
