from django.core.management.base import BaseCommand
from simon_app.models import AS
from simon_app.functions import networkInLACNICResources
from simon_app import caching
import zlib, urllib2
import datetime
from sys import stdout
from simon_app.decorators import timed


class Command(BaseCommand):

    @timed(name="Downloading RIPE RIS")
    def handle(self, *args, **options):

        now = datetime.datetime.now()
        # caching.set("as-cached", AS.objects.all())
        # print caching.get("as-cached")
        #
        # print
        # exit(1)

        print "Downloading RIS..."
        file_v4=urllib2.urlopen('http://www.ris.ripe.net/dumps/riswhoisdump.IPv4.gz').read()
        file_v6=urllib2.urlopen('http://www.ris.ripe.net/dumps/riswhoisdump.IPv6.gz').read()

        print "Parsing RIS..."
        ris_v4 = zlib.decompress(file_v4, 16+zlib.MAX_WBITS)
        ris_v6 = zlib.decompress(file_v6, 16+zlib.MAX_WBITS)
        asn_list = [asn.split('\t') for asn in ris_v4.split('\n')] + [asn.split('\t') for asn in ris_v6.split('\n')]

        old = [a for a in AS.objects.all()] # Delete ALL AS-related info and make place for new information
        internet = AS(
            asn=0,
            network="0.0.0.0/0",
            pfx_length=0,
            date_updated=now,
            regional=False
        )
        internet.save()

        print "Inserting new records (%s)" % (now)
        N = len(asn_list)
        for i, line in enumerate(asn_list):
            try:
                stdout.write("\r%.2f%%" % (100.0 * i / N))
                stdout.flush()

                if len(line) != 3: continue

                ip = line[1]
                asn = line[0]
                pfx_length = ip.split('/')[1]

                # if not networkInLACNICResources(ip):
                #     continue

                as_object = AS(
                    asn=asn,
                    network=ip,
                    pfx_length=pfx_length,
                    date_updated=now,
                    regional=True
                )
                as_object.save()

            except KeyboardInterrupt:
                exit(1)
            except:
                continue

        print "Deleting old records..."
        for o in old:
            o.delete()