#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import TracerouteResult, TracerouteHop


class Command(BaseCommand):

    import signal

    def signal_term_handler(signal, frame):
        import sys
        sys.exit(1)
    signal.signal(signal.SIGTERM, signal_term_handler)


    def handle(self, *args, **options):
        from simon_app.models import ProbeApiPingResult, AS, SpeedtestTestPoint, Country
        from simon_app.reportes import GMTUY
        from django.template import Template, Context
        from simon_project import passwords
        import urllib2
        import json
        import datetime
        import numpy


        ccs = Country.objects.get_region_countries().values_list('iso', flat=True)
        origins = ""
        for c in ccs:
            origins += c + ','
        origins = origins[0:-1]  # remove trailing comma

        tps = SpeedtestTestPoint.objects.get_ipv4().distinct('country').order_by('country')  # one TP per country TODO get *really* random tests... toto get ipv6!!!
        for tp in tps:

            destination_ip = tp.ip_address
            cc_destination = tp.country  # country['CountryCode']

            count = 10
            max_hops = 20
            ping_time = 1000
            sleep_time = 1000
            tx_time = 5000
            timeout = count * max_hops * (ping_time + sleep_time) + tx_time  # seconds



            destination_ip = "216.58.221.164"
            # origins = "BR"

            t = Template(
                "https://probeapifree.p.mashape.com/Probes.svc/StartTracertTestByCountry?"
                "countrycode={{ cc }}&"
                "count={{ count }}&"
                "destination={{ destination }}&"
                "probeslimit={{ probeslimit }}"
                # "timeout={{ timeout }}"
            )

            ctx = Context({'cc': origins, 'count': count, 'destination': destination_ip, 'probeslimit': 2 * len(ccs), 'timeout': timeout})
            url = t.render(ctx)

            print destination_ip, url

            now = datetime.datetime.now(GMTUY())

            try:
                req = urllib2.Request(url)
                req.add_header("X-Mashape-Key", passwords.PROBEAPI)
                req.add_header("Accept", "application/json")
                response = urllib2.urlopen(req).read()
            except Exception as e:
                print e
                continue

            print datetime.datetime.now(GMTUY()) - now

            py_object = json.loads(response)

            N = len(py_object['StartTracertTestByCountryResult'])
            if N <= 0:
                continue

            # for each probe...
            for result in py_object['StartTracertTestByCountryResult']:

                # print json.dumps(result, indent=4, separators=(',', ': '))

                cc_origin = result['Country']['CountryCode']
                asn = result['ASN']['AsnID'][2:]  # strip 'AS'
                empty_ass = AS.objects.filter(network__isnull=True, asn=asn)  # get the asn with no network associated
                if len(empty_ass) <= 0:
                    as_origin = AS(asn=asn)  # create the empty-network AS
                    as_origin.save()
                elif len(empty_ass) > 1:
                    continue
                else:
                    as_origin = empty_ass[0]

                for traceroute in result["TRACERoute"]:

                    ip_origin = traceroute["IP"]

                    tr = TracerouteResult()
                    tr.save()

                    for hop in traceroute["Tracert"]:
                        ip_destination = hop['IP']
                        as_destination = AS.objects.get_as_by_ip(destination_ip)

                        status = hop["Status"]
                        if status != "OK" or ip_destination is None:

                            # print ip_destination, type(ip_destination)
                            if ip_destination is not None:
                                ip_version = 6 if ':' in ip_destination else 4
                            else:
                                ip_version = 0
                                as_destination = None

                            tr_hop = TracerouteHop(
                                date_test=now,
                                ip_origin=ip_origin,
                                ip_destination=ip_destination,
                                country_origin=cc_origin,
                                country_destination="XX",
                                ip_version=ip_version,
                                as_origin=as_origin.asn,
                                as_destination=as_destination.asn,
                                number_probes=0,

                                tester="probeapi",
                                tester_version="1",
                                traceroute_result=tr
                            )
                            tr.hop_count += 1
                            tr.save()
                            tr_hop.save()
                            continue

                        rtts = []
                        packet_loss = 0
                        for r in hop['PingTimeArray']:
                            try:
                                rtts.append(int(r))
                            except:
                                packet_loss += 1
                                continue

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
                            rtts = [0]

                        std_dev = numpy.std(rtts)
                        tr_hop = TracerouteHop(
                            date_test=now,
                            ip_origin=ip_origin,
                            ip_destination=ip_destination,
                            min_rtt=numpy.amin(rtts),
                            max_rtt=numpy.amax(rtts),
                            ave_rtt=numpy.mean(rtts),
                            dev_rtt=std_dev,
                            median_rtt=numpy.median(rtts),
                            packet_loss=packet_loss,
                            country_origin=cc_origin,
                            country_destination=cc_destination,
                            ip_version=6 if ':' in destination_ip else 4,
                            as_origin=as_origin.asn,
                            as_destination=as_destination.asn,
                            number_probes=len(rtts),

                            tester="probeapi",
                            tester_version="1",
                            traceroute_result=tr
                        )
                        tr.hop_count += 1
                        tr.save()
                        tr_hop.save()
                print tr.hop_count