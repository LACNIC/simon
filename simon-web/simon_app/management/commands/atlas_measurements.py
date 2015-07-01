from django.core.management.base import BaseCommand
from simon_app.models import RipeAtlasPingResult


class Command(BaseCommand):
    def handle(self, *args, **options):
        from simon_app.models import *
        from simon_app.functions import inLACNICResources
        import json
        import urllib2
        from datetime import datetime
        from simon_app.api_views import getCountryFromIpAddress

        base_url = "https://atlas.ripe.net"
        probes = RipeAtlasProbe.objects.exclude(probe_id=None)
        stopped = 4
        for probe in probes:

            type = "ping"
            status = stopped
            previous = ("/api/v1/measurement/?"
                    "prb_id=%s&"
                    "type=%s&"
                    "is_public=1&"
                    "is_oneoff=1&"
                    "status=%s"
                   ) % (probe.probe_id, type, status)
            tester = "ripe-atlas"

            # calculate initial offset
            url = "%s%s" % (base_url, previous)
            initial = json.loads(urllib2.urlopen(url).read())
            meta = initial['meta']
            offset = meta['total_count'] - meta['limit'] # inital offset (so we page backwards)

            previous = ("/api/v1/measurement/?"
                    "prb_id=%s&"
                    "type=%s&"
                    "is_public=1&"
                    "is_oneoff=1&"
                    "status=%s&"
                    "offset=%s"
                   ) % (probe.probe_id, type, status, offset)

            while previous != None:
                url = "%s%s" % (base_url, previous)
                print url
                page_content = json.loads(urllib2.urlopen(url).read())
                previous = page_content['meta']['previous']

                for msm_pointer in page_content['objects']:
                    # fetch the actual results for every "pointer'

                    msm_id = msm_pointer['msm_id']
                    if msm_id in RipeAtlasMeasurement.objects.all().values_list('measurement_id', flat=True):
                        break # next probe

                    if not inLACNICResources(msm_pointer['dst_addr']):
                        continue

                    result_url = msm_pointer['result']
                    result_content = json.loads(urllib2.urlopen(result_url).read())

                    destination_ip = result_content['dst_addr']
                    origin_ip = result_content['src_addr']
                    min = result_content['min']
                    max = result_content['max']
                    avg = result_content['avg']

                    rar = RipeAtlasPingResult(

                        probe_id=probe.probe_id,
                        measurement_id=msm_id,
                        type=type,
                        oneoff=True,

                        date_test=datetime.fromtimestamp(result_content['timestamp']),
                        version='',
                        ip_origin=origin_ip,
                        ip_destination=destination_ip,
                        testype="icmp",
                        number_probes=result_content['sent'],
                        min_rtt=min,
                        max_rtt=max,
                        ave_rtt=avg,
                        dev_rtt=(max-avg + avg-min) / 2 / 2,  # asuming min avg - 2*std. dev. and max = avg + 2*std. dev.
                        median_rtt=avg,  # todo
                        packet_loss=int(result_content['sent']) - int(result_content['rcvd']),
                        country_origin=getCountryFromIpAddress(origin_ip),
                        country_destination=getCountryFromIpAddress(destination_ip),
                        ip_version=6 if ':' in destination_ip else 4,
                        tester=tester,
                        tester_version="1",
                        as_origin=AS.objects.get_as_by_ip(origin_ip),
                        as_destination=AS.objects.get_as_by_ip(destination_ip),
                        user_agent="",
                        url=""
                    )
                    rar.save()
                    print rar