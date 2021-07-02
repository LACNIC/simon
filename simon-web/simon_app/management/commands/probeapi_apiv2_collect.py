#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from simon_app.models import ProbeApiRequest
from simon_app.decorators import probeapi
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI - Collect results from APIv2 results"

    def add_arguments(self, parser):
        parser.add_argument('--hours-ago', type=int)

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        hours_ago = options['hours_ago']

        then = datetime.now() - timedelta(hours=hours_ago)
        pars = ProbeApiRequest.objects.filter(
            stage_collected=False,
            date_1__gte=then
        )

        print("Requests to collect: ", pars.count())

        for par in pars:
            j = par.get()
            print(par, j)
