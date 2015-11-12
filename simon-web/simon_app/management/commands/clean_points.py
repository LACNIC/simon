from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from urllib2 import urlopen, HTTPError
from sys import stdout
from simon_app.decorators import *

__author__ = 'agustin'


class Command(BaseCommand):
    def handle(self, *args, **options):
        command = "Clean Test Points"

        tps = SpeedtestTestPoint.objects.filter(enabled=True)
        N = len(tps)
        disabled = []
        for i, tp in enumerate(tps):
            stdout.write("\r%.2f%%" % (100.0 * i / N))
            stdout.flush()

            tp.check()

        print ""
        print "The following points have been disabled ", disabled