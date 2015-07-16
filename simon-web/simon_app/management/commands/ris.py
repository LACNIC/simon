from django.core.management.base import BaseCommand
from simon_app.models import AS
from simon_app.functions import networkInLACNICResources
from simon_project import settings
import zlib, urllib2
import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):

        now = datetime.datetime.now()

        print "Downloading RIS..."
        file = urllib2.urlopen('http://www.ris.ripe.net/dumps/riswhoisdump.IPv4.gz').read()

        print "Parsing RIS..."
        ris = zlib.decompress(file, 16 + zlib.MAX_WBITS)
        asn_list = [asn.split('\t') for asn in ris.split('\n')]

        AS.objects.all().delete()  # Delete ALL AS-related info and make place for new information

        internet = AS(
            asn=0,
            network="0.0.0.0/0",
            pfx_length=0,
            date_updated=now,
            regional=False
        )
        internet.save()

        N = len(asn_list)
        i = 0
        for line in asn_list:
            try:
                print "%.2f%%" % (100.0 * i / N)
                i += 1

                if len(line) != 3: continue

                ip = line[1]
                asn = line[0]
                pfx_length = ip.split('/')[1]

                if not networkInLACNICResources(ip):
                    continue

                as_object = AS(
                    asn=asn,
                    network=ip,
                    pfx_length=pfx_length,
                    date_updated=now,
                    regional=True
                )
                as_object.save()

            except:
                continue