#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from multiprocessing.dummy import Pool as ThreadPool
from simon_app.decorators import timed_command


class Command(BaseCommand):

    def run_msm(self, msm):
        return msm.init()

    command = "Africa Connectivity In-Country Measurements"

    @timed_command(name=command)
    @probeapi(command=command)
    def handle(self, *args, **options):
        ccs = Country.objects.get_afrinic_countrycodes()[0:5]

        # Script execution
        pool = ThreadPool(4)

        msms = []
        for cc in ccs:
            url = "%s.exp.dev.lacnic.net" % (cc.lower())

            msm = ProbeApiMeasurement(
                tps=[url],
                ccs=[cc]
            )
            msms.append(msm)

        lists = pool.map(self.run_msm, msms)
        res = []
        for l in lists:
            res += l
        return res
