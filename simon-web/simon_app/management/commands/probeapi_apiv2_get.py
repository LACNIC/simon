#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand
from simon_app.models import ProbeApiRequest
from simon_app.decorators import probeapi
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):

    command = "ProbeAPI - Get s single result from APIv2 results"

    def add_arguments(self, parser):
        parser.add_argument('--id', type=str)

    @timed_command(name=command)
    @probeapi(command=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        id = options['id']

        par = ProbeApiRequest.objects.get(
            probeapi_id=id
        )

        j = par.get()

        print json.loads(j)
        return j
