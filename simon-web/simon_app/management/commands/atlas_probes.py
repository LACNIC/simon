from django.core.management.base import BaseCommand
from simon_app.models import RipeAtlasPingResult


class Command(BaseCommand):
    def handle(self, *args, **options):
        from simon_app.models import *
        import json
        import urllib2

        existent_probes = RipeAtlasProbe.objects.all().values_list('probe_id', flat=True)

        base_url = "https://atlas.ripe.net"
        ccs = Country.objects.get_region_countries().values_list('iso', flat=True)
        for cc in ccs:

            next = "/api/v1/probe/?country_code=%s" % (cc)
            while next != None:

                url = "%s%s" % (base_url, next)
                print url
                page_content = json.loads(urllib2.urlopen(url).read())
                next = page_content['meta']['next']

                for probe in page_content['objects']:

                    if probe['id'] in existent_probes:
                        continue

                    rap = RipeAtlasProbe(
                        probe_id = probe['id'],
                        country_code = probe['country_code'],
                        asn_v4 = probe['asn_v4'],
                        asn_v6 = probe['asn_v6'],
                        prefix_v4 = probe['prefix_v4'],
                        prefix_v6 = probe['prefix_v6']
                    )
                    rap.save()
                    print rap