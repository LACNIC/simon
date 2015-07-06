from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from urllib2 import urlopen, HTTPError

__author__ = 'agustin'

class Command(BaseCommand):

    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.filter(enabled=True)
        N = len(tps)
        i=0
        for t in tps:
            i+=1
            try:
                urlopen("http://" + t.ip_address + "/", timeout=5).read()
            except HTTPError as e:
                httpCode = e.code
                if httpCode != 200:
                    t.enabled = False
                    print t
                    t.save()
                    print t
                continue
            except Exception:
                continue
            print "%.2f%%" % (100.0*i / N)