from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from urllib2 import urlopen, HTTPError
from sys import stdout

__author__ = 'agustin'

class Command(BaseCommand):

    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.filter(enabled=True)
        N = len(tps)
        disabled = []
        for i, t in enumerate(tps):
            stdout.write("\r%.2f%%" % (100.0 * i / N))
            stdout.flush()

            try:
                urlopen("http://" + t.ip_address + "/", timeout=5).read()
            except HTTPError as e:
                httpCode = e.code
                if httpCode != 200:
                    t.enabled = False
                    t.save()
                    disabled.append(t)
                continue
            except Exception:
                continue
        print ""
        print "The following points have been disabled ", disabled