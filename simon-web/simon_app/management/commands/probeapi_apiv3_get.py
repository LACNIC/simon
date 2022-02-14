#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from simon_app.models import HourlyBatch
from simon_app.decorators import probeapi
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI - Collect results from APIv3 results"

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=str)

    # @timed_command(name=command)
    # @probeapi(command=command)
    # @mem_comsumption(name=command)
    def handle(self, *args, **options):

        batch = options['batch']
        hb = HourlyBatch.objects.get_or_create(
             probeapi_batch=batch
         )[0]
        #
        j = hb.get()
        # #
        # # print(json.loads(j))
        # return par
        print(j)