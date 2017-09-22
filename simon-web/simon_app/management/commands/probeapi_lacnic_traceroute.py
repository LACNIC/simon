#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from simon_app.models import Country
from probeapi_traceroute import ProbeApiTraceroute
from simon_app.decorators import timed


class Command(BaseCommand):

    command = "LAC Connectivity [traceroute]"

    @timed(name=command)
    @probeapi(command=command)
    def handle(self, *args, **options):
        msm = ProbeApiTraceroute(
            max_job_queue_size=50,
            max_points=20,
            ping_count=3
        )
        ccs = Country.objects.get_lacnic_countrycodes()
        results = msm.init(
            tps=["lac-connectivity.exp.dev.lacnic.net"],
            ccs=ccs
        )

        return results
