#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


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

            destination_ip = tp.ip_address
            cc_destination = tp.country  # country['CountryCode']
            as_destination = AS.objects.get_as_by_ip(destination_ip)
            count = 15

            opener = urllib2.build_opener()
            opener.addheaders = [
                ("X-Mashape-Key", passwords.PROBEAPI),
                ("Accept", "application/json")
            ]

            t = Template("https://probeapifree.p.mashape.com/Probes.svc/StartPingTestByCountry?"
                         "countrycode={{ cc }}&"
                         "count={{ count }}&"
                         "destination={{ destination }}&"
                         "probeslimit={{ probeslimit }}&"
                         "timeout={{ timeout }}")

            ctx = Context({'cc': origins, 'count': count, 'destination': destination_ip, 'probeslimit': len(ccs), 'timeout': 30000})
            url = t.render(ctx)

            response = opener.open(url).read()
            py_object = json.loads(response, parse_int=int)

            if len(py_object['StartPingTestByCountryResult']) <= 0:
                continue

            for result in py_object['StartPingTestByCountryResult']:

                # print json.dumps(result, indent=4, separators=(',', ': '))

                cc_origin = result['Country']['CountryCode']
                asn = result['ASN']['AsnID'][2:]  # strip 'AS'

                rtts = []
                packet_loss = 0
                for ping_ in result['Ping']:
                    # for each testpoint
                    tp = SpeedtestTestPoint.objects.get(ip_address=ping_['IP'])

                    for r in ping_['PingTimeArray']:
                        try:
                            rtts.append(int(r))
                        except:
                            packet_loss += 1
                            continue

                    empty_ass = AS.objects.filter(network__isnull=True, asn=asn)  # get the asn with no network associated
                    if len(empty_ass) <= 0:
                        as_origin = AS(asn=asn)  # create the empty-network AS
                        as_origin.save()
                    elif len(empty_ass) > 1:
                        continue
                    else:
                        as_origin = empty_ass[0]

                    # IQR filtering...
                    _n = len(rtts)
                    rtts = sorted(rtts)
                    index = len(rtts) - 1
                    q1 = rtts[int(0.25 * index)]
                    q3 = rtts[int(0.75 * index)]
                    iqr = q3 - q1
                    max = q3 + 1.5 * iqr
                    min = q1 - 1.5 * iqr
                    rtts = [r for r in rtts if r > min and r < max]

                    if len(rtts) <= 0:
                        continue

                    std_dev = numpy.std(rtts)
                    ProbeApiPingResult(
                        date_test=now,
                        ip_origin='',
                        ip_destination=destination_ip,
                        min_rtt=numpy.amin(rtts),
                        max_rtt=numpy.amax(rtts),
                        ave_rtt=numpy.mean(rtts),
                        dev_rtt=std_dev,
                        median_rtt=numpy.median(rtts),
                        packet_loss=packet_loss,
                        country_origin=cc_origin,
                        country_destination=cc_destination,
                        ip_version=6 if ':' in destination_ip else 4,
                        as_origin=as_origin,
                        as_destination=as_destination,
                        url=tp.speedtest_url,
                        number_probes=len(rtts)
                    ).save()

                    print "ICMP ping from %s to %s is %.0f ms (%s samples, +- %.0f ms, %.0f samples stripped)" % (cc_origin, cc_destination, numpy.mean(rtts), len(rtts), 2*std_dev, _n-len(rtts))