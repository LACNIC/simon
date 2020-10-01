#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from _probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI - <source,destination> pairs"

    def add_arguments(self, parser):
        parser.add_argument('--src', type=str, nargs='+')
        parser.add_argument('--dst', type=str, nargs='+')
        parser.add_argument('--probes', type=int)

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        ccs = options['src']
        dst = options['dst']
        probes = options['probes']

        # accept ip addr, hostnmae, or plain txt as dst
        # plain txt will be formatted to hostname %s.exp.dev.lacnic.net
        dst = map(
            lambda d: "%s.exp.dev.lacnic.net" % d if '.' not in d and ':' not in d else d,
            dst
        )

        msm = ProbeApiMeasurement(
            max_job_queue_size=10,
            max_probes=probes
        )
        results = msm.init(
            tps=dst,
            ccs=ccs
        )

        return results
