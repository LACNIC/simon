#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import *
from simon_app.reportes import GMTUY
from django.template import Template, Context
from simon_project import passwords
import urllib2
import json
import datetime
import numpy
from random import sample


def get_countries():
    url = "https://probeapifree.p.mashape.com/Probes.svc/GetCountries"

    try:
        print "Getting countries..."
        req = urllib2.Request(url)
        req.add_header("X-Mashape-Key", passwords.PROBEAPI)
        req.add_header("Accept", "application/json")
        response = urllib2.urlopen(req).read()
        py_object = json.loads(response)

        res = {}
        ccs = Country.objects.get_region_countrycodes()
        for p in py_object["GetCountriesResult"]:
            cc = p["CountryCode"]
            if cc in ccs:
                res[cc] = p["ProbesCount"]
        return res
    except Exception as e:
        pass


def get_probeapi_response(url):
    req = urllib2.Request(url)
    req.add_header("X-Mashape-Key", passwords.PROBEAPI)
    req.add_header("Accept", "application/json")
    response = urllib2.urlopen(req).read()
    return response


class Command(BaseCommand):
    def handle(self, *args, **options):
        from threading import Thread

        from Queue import Queue

        def do_work(tp, url_probeapi):
            try:
                q.put((tp, url_probeapi))

                response = get_probeapi_response(url_probeapi)
                if response is not None:
                    process_response(response, tp)

            except Exception as e:
                print e
                pass

            finally:
                dt = datetime.datetime.now() - then
                # print "%s\t%s" % (q.unfinished_tasks, dt)
                q.task_done()
                return

        def process_response(response, tp):

            now = datetime.datetime.now()
            py_object = json.loads(str(response))

            N = len(py_object['StartTracertTestByCountryResult'])
            if N <= 0:
                print py_object
                return

            # for each probe...
            for result in py_object['StartTracertTestByCountryResult']:

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
                                country_destination=tp.country,
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
                            country_destination=tp.country,
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
                return

        ccs = get_countries().keys()
        # ccs = sample(ccs, 1)  # delete this (experimental)

        tps = SpeedtestTestPoint.objects.get_ipv4().filter(enabled=True).distinct('country').order_by(
            'country')  # one TP per country TODO get *really* random tests... TODO get ipv6!!!

        print "tps %s x ccs %s" % (len(tps), len(ccs))
        q = Queue()
        then = datetime.datetime.now()
        for i, tp in enumerate(tps):

            # print "%.1f%%" % (100.0 * i / len(tps))

            # sanity check
            online = tp.check_point()
            if not online:
                continue

            for cc in ccs:
                destination_ip = tp.ip_address

                count = 3
                max_hops = 20
                ping_time = 1000
                sleep_time = 1000
                tx_time = 5000
                timeout = count * max_hops * (ping_time + sleep_time) + tx_time  # seconds

                t = Template(
                    "https://probeapifree.p.mashape.com/Probes.svc/StartTracertTestByCountry?"
                    "countrycode={{ cc }}&"
                    "count={{ count }}&"
                    "destination={{ destination }}&"
                    "probeslimit={{ probeslimit }}"
                    # "timeout={{ timeout }}"
                )

                ctx = Context(
                    {
                        'cc': cc,
                        'count': count,
                        'destination': destination_ip,
                        'probeslimit': 2 * len(ccs),
                        'timeout': timeout
                    }
                )
                url_probeapi = t.render(ctx)

                t = Thread(
                    target=do_work,
                    args=(tp, url_probeapi)
                )
                t.daemon = False
                t.start()

        q.join()
