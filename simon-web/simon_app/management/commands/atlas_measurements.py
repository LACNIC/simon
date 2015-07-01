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
        from simon_project.settings import asns

        base_url = "https://atlas.ripe.net"
        probes = RipeAtlasProbe.objects.exclude(probe_id=None)
        stopped = 4
        for asn in asns:

            type = "ping"
            status = stopped
            previous = ("/api/v1/measurement/?"
                    "dst_asn=%s&"
                    "type=%s&"
                    "is_public=1&"
                    "is_oneoff=1&"
                    "status=%s"
                   ) % (asn, type, status)
            tester = "ripe-atlas"

            # calculate initial offset
            url = "%s%s" % (base_url, previous)
            initial = json.loads(urllib2.urlopen(url).read())
            meta = initial['meta']
            offset = meta['total_count'] - meta['limit'] # inital offset (so we page backwards)

            previous = ("/api/v1/measurement/?"
                    "dst_asn=%s&"
                    "type=%s&"
                    "is_public=1&"
                    "is_oneoff=1&"
                    "status=%s&"
                    "offset=%s"
                   ) % (asn, type, status, offset)

            while previous != None:
                print url
                page_content = json.loads(urllib2.urlopen(url).read())
                previous = page_content['meta']['previous']

                for msm_pointer in page_content['objects']:
                    # fetch the actual results for every "pointer'

                    msm_id = msm_pointer['msm_id']
                    if msm_id in RipeAtlasMeasurement.objects.all().values_list('measurement_id', flat=True):
                        break # next probe

                    if not inLACNICResources(msm_pointer['dst_addr']):
                        print '.',
                        continue

                    result_url = msm_pointer['result']
                    result_content = json.loads(urllib2.urlopen(base_url + result_url).read())

                    for result in result_content:
                        destination_ip = result['dst_addr']
                        origin_ip = result['from']
                        min = result['min']
                        max = result['max']
                        avg = result['avg']

                        rar = RipeAtlasPingResult(

                            probe_id=result['prb_id'],
                            measurement_id=msm_id,
                            type=type,
                            oneoff=True,

                            date_test=datetime.fromtimestamp(result['timestamp']),
                            version=6 if ':' in destination_ip else 4,
                            ip_origin=origin_ip,
                            ip_destination=destination_ip,
                            testype="icmp",
                            number_probes=result['sent'],
                            min_rtt=min,
                            max_rtt=max,
                            ave_rtt=avg,
                            dev_rtt=(max-avg + avg-min) / 2 / 2,  # asuming min avg - 2*std. dev. and max = avg + 2*std. dev.
                            median_rtt=avg,  # todo
                            packet_loss=int(result['sent']) - int(result['rcvd']),
                            country_origin=getCountryFromIpAddress(origin_ip),
                            country_destination=getCountryFromIpAddress(destination_ip),
                            ip_version=6 if ':' in destination_ip else 4,
                            tester=tester,
                            tester_version="1",
                            as_origin=AS.objects.get_as_by_ip(origin_ip).asn,
                            as_destination=AS.objects.get_as_by_ip(destination_ip).asn,
                            user_agent="",
                            url=""
                        )
                        rar.save()
                        print "\t", rar