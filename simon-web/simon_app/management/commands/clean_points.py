from __future__ import print_function
from collections import defaultdict
from django.db import DatabaseError, transaction
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from simon_app.decorators import chatty_command
from multiping import MultiPing, multi_ping
from tqdm import tqdm




class Command(BaseCommand):
    @chatty_command(command="Clean Test Points")
    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.all()

        responses, no_responses = multi_ping([tp.ip_address for tp in tps], timeout=10, retry=9)
        tps.filter(ip_address__in=list(responses.keys())).update(enabled=True)
        tps.exclude(ip_address__in=list(responses.keys())).update(enabled=False)

        print("Test points statuses (ICMP):")
        print("UP {up}".format(up=len(responses)), tps.filter(ip_address__in=list(responses.keys())))
        print("DOWN {down}".format(down=len(no_responses)), tps.exclude(ip_address__in=list(responses.keys())))
