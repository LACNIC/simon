#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from probeapi_traceroute import ProbeApiTraceroute


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity UTC+01:00 [traceroute]")
    def handle(self, *args, **options):
        msm = ProbeApiTraceroute(
            max_job_queue_size=50,
            max_points=20,
            ping_count=3
        )
        ccs = ['DZ', 'AO', 'BJ', 'CM', 'CF', 'TD', 'CG', 'CD', 'GQ', 'GA', 'LY', 'NA', 'NE', 'NG',
               'TN']

        results = msm.init(
            tps=["africa-connectivity.exp.dev.lacnic.net"],
            ccs=ccs
        )

        return results