#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.core.management.base import BaseCommand
from simon_app.decorators import probeapi
from ._probeapi import ProbeApiMeasurement
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI - <source,destination> pairs"

    def add_arguments(self, parser):
        parser.add_argument('--src', type=str, nargs='+')
        parser.add_argument('--dst', type=str, nargs='+')
        parser.add_argument('--probes', type=int, default=10)
        parser.add_argument('--timeout', type=int, default=30000)

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        ccs = options['src']
        dst = options['dst']
        probes = options['probes']
        timeout = options.get('timeout')

        # accept ip addr, hostnmae, or plain txt as dst
        # plain txt will be formatted to hostname %s.exp.dev.lacnic.net
        dst = ["%s.exp.dev.lacnic.net" % d if '.' not in d and ':' not in d else d for d in dst]

        msm = ProbeApiMeasurement(
            max_job_queue_size=10,
            max_probes=probes
        )
        results = msm.init(
            tps=dst,
            ccs=ccs,
            timeout=timeout
        )

        return results
