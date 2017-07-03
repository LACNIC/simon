#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from probeapi_traceroute import ProbeApiTraceroute
from probeapi_top28 import trace_top28


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity UTC+02:00 [traceroute]")
    def handle(self, *args, **options):
        msm = ProbeApiTraceroute(
            max_job_queue_size=50,
            max_points=20,
            ping_count=3
        )
        ccs = ['BW', 'BI', 'EG', 'LS', 'MW', 'MZ', 'RW', 'ZA', 'SZ', 'ZM', 'ZW']

        results = msm.init(
            tps=["africa-connectivity.exp.dev.lacnic.net"],
            ccs=ccs
        )

        results_top28 = trace_top28(ccs)

        return results + results_top28
