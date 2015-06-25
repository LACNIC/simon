#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import TracerouteResult, TracerouteHop


class Command(BaseCommand):
    def handle(self, *args, **options):
        from simon_app.models import ProbeApiPingResult, AS, SpeedtestTestPoint, Country
        from simon_app.reportes import GMTUY
        from django.template import Template, Context
        from simon_project import passwords
        import urllib2
        import json
        import datetime
        import numpy

        now = datetime.datetime.now(GMTUY())

        ccs = Country.objects.get_region_countries().values_list('iso', flat=True)

        origins = ""
        for c in ccs:
            origins += c + ','
        origins = origins[0:-1]  # remove trailing comma

        tps = SpeedtestTestPoint.objects.all().distinct('country').order_by('country')  # one TP per country TODO get *really* random tests...
        for tp in tps:
            try:
                # tp = random.choice(tps)
                # with random.choice(SpeedtestTestPoint.objects.all()) as tp:
                # for tp in SpeedtestTestPoint.objects.all():

                destination_ip = tp.ip_address
                cc_destination = tp.country  # country['CountryCode']
                as_destination = AS.objects.get_as_by_ip(destination_ip)
                count = 10

                opener = urllib2.build_opener()
                opener.addheaders = [
                    ("X-Mashape-Key", passwords.PROBEAPI),
                    ("Accept", "application/json")
                ]

                t = Template("https://probeapifree.p.mashape.com/Probes.svc/StartTracertTestByCountry?"
                             "countrycode={{ cc }}&"
                             "count={{ count }}&"
                             "destination={{ destination }}&"
                             "probeslimit={{ probeslimit }}&"
                             "timeout={{ timeout }}")

                print destination_ip

                ctx = Context({'cc': origins, 'count': count, 'destination': destination_ip, 'probeslimit': len(ccs), 'timeout': 20000})
                url = t.render(ctx)

                response = opener.open(url).read()
                py_object = json.loads(response)

                N = len(py_object['StartTracertTestByCountryResult'])
                if N <= 0:
                    continue

                # for each probe...
                for result in py_object['StartTracertTestByCountryResult']:

                    cc_origin = result['Country']['CountryCode']
                       asn = result['ASN']['AsnID'][2:]  # strip 'AS'


                    result_traceroute = result['TRACERoute'][0]['Tracert']
                    if result_traceroute is None or len(result_traceroute) <= 0:
                        continue

                    # for each hop...

                    rtts = result_traceroute[0]['PingTimeArray']
                    hop_ip_destination = result_traceroute[0]['IP']

                    # print json.dumps(result_traceroute, indent=4, separators=(',', ': '))

                    empty_ass = AS.objects.filter(network__isnull=True, asn=asn)  # get the asn with no network associated
                    if len(empty_ass) <= 0:
                        as_origin = AS(asn=asn)  # create the empty-network AS
                        as_origin.save()
                    elif len(empty_ass) > 1:
                        continue
                    else:
                        as_origin = empty_ass[0]

                    print rtts, hop_ip_destination, as_origin

                    # print rtts
                    # # IQR filtering...
                    # _n = len(rtts)
                    # rtts = sorted(rtts)
                    # index = len(rtts) - 1
                    # q1 = rtts[int(0.25 * index)]
                    # q3 = rtts[int(0.75 * index)]
                    # iqr = q3 - q1
                    # max = q3 + 1.5 * iqr
                    # min = q1 - 1.5 * iqr
                    # rtts = [r for r in rtts if r > min and r < max]

                    hop = TracerouteHop()

                    # std_dev = numpy.std(rtts)
                    # ProbeApiPingResult(
                    #     date_test=now,
                    #     ip_origin='',
                    #     ip_destination=destination_ip,
                    #     min_rtt=rtt,#numpy.amin(rtts),
                    #     max_rtt=rtt,#numpy.amax(rtts),
                    #     ave_rtt=rtt,#numpy.mean(rtts),
                    #     dev_rtt=0,#std_dev,
                    #     median_rtt=rtt,#numpy.median(rtts),
                    #     packet_loss=0,
                    #     country_origin=cc_origin,
                    #     country_destination=cc_destination,
                    #     ip_version=6 if ':' in destination_ip else 4,
                    #     as_origin=as_origin,
                    #     as_destination=as_destination,
                    #     url=tp.speedtest_url,
                    #     number_probes=count, #len(rtts)
                    # ).save()

                    # print "ICMP ping from %s to %s is %s ms (%s samples)" % (cc_origin, cc_destination, rtt, N)
            except Exception:
                continue