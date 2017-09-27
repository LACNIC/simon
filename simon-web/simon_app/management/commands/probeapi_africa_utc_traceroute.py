#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from probeapi_traceroute import ProbeApiTraceroute
from probeapi_top28 import trace_top28
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "Africa Connectivity UTC [traceroute]"

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):
        msm = ProbeApiTraceroute(
            max_job_queue_size=50,
            max_points=20,
            ping_count=3
        )
        ccs = ['EH', 'GM', 'SH', 'BF', 'GH', 'GN', 'GW', 'CI', 'LR', 'ML', 'MR', 'MA', 'ST', 'SN',
               'SL', 'TG']

        results = msm.init(
            tps=["africa-connectivity.exp.dev.lacnic.net"],
            ccs=ccs
        )

        results_top28 = trace_top28(ccs)

        return results + results_top28
