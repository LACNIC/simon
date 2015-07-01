from django.core.management.base import BaseCommand
from simon_app.models import RipeAtlasPingResult


class Command(BaseCommand):
    def handle(self, *args, **options):
        from simon_app.api_views import getCountryFromIpAddress
        import urllib2
        import json
        from simon_project.settings import v4resources
        from simon_app.models import *
    #
    #     test_types = {
    #         '1': 'ping',
    #         '2': 'traceroute',
    #         '3': 'ping6',
    #         '4': 'traceroute6'
    #     }
    #
    #     rams = []
    #     for ipBlock in v4resources:
    #         for type in test_types:
    #
    #             BASE = "https://atlas.ripe.net"
    #             next = "/api/v1/measurement/?" + \
    #                    ("dst_addr=%s&" % ipBlock) + \
    #                    "is_oneoff=false&" \
    #                    "is_public=true&" \
    #                    "status=2&" + \
    #                    ("type=%s&" % type) + \
    #                    "format=json"
    #
    #             while next is not None:
    #                 httpGet = urllib2.urlopen(BASE + next).read()
    #                 json_loads = json.loads(httpGet)
    #                 objects = json_loads['objects']
    #                 for o in objects:
    #                     # cc = getCountryFromIpAddress(o['dst_addr'])
    #                     msm_id = o['msm_id']
    #                     ram = RipeAtlasMeasurement(
    #                         measurement_id=msm_id,
    #                         running=True,
    #                         type=type
    #                     )
    #                     rams.append(ram)
    #
    #                 meta = json_loads['meta']
    #                 next = meta['next']
    #
    #     for ram in rams:
    #         try:
    #             old = RipeAtlasMeasurement.objects.filter(running=False, measurement_id=msm_id)
    #             old.running = True
    #             old.save()
    #         except:
    #             # it's new
    #             ram.save()


        from subprocess import Popen as background
        for m in RipeAtlasMeasurement.objects.filter(type='2'):
            command = ["python", "manage.py", "atlas", str(m.measurement_id)]
            background(command)