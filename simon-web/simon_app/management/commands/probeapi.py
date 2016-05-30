#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from newrelic.core import thread_utilization

from simon_app.models import *
from simon_app.models_management import CommandAudit
from simon_app.reportes import GMTUY
from django.template import Template, Context
from simon_project import passwords
import urllib2
import json
import datetime
import numpy
from probeapi_traceroute import get_countries, get_probeapi_response
from multiprocessing.dummy import Pool as ThreadPool


class Command(BaseCommand):
    def handle(self, *args, **options):
        command = "ProbeAPI Measurements"

        def do_work(url):
            try:
                response = get_probeapi_response(url)
                if response is not None:
                    process_response(response, url)

            except Exception as e:
                print e, response
                pass

            finally:
                dt = datetime.datetime.now() - then
                # q.task_done()
                # print "%s\t%s" % (q.unfinished_tasks, dt)
                return

        def process_response(response, url_probeapi):
            py_object = json.loads(response, parse_int=int)

            if len(py_object['StartPingTestByCountryResult']) <= 0:
                return

            for result in py_object['StartPingTestByCountryResult']:

                cc_origin = result['Country']['CountryCode']
                asn = result['ASN']['AsnID'][2:]  # strip 'AS'

                packet_loss = 0

                for ping_ in result['Ping']:
                    rtts = []
                    for r in ping_['PingTimeArray']:
                        try:
                            rtts.append(int(r))
                        except Exception as e:
                            packet_loss += 1
                            continue
                    destination_ip = ping_["IP"]

                    try:
                        empty_ass = AS.objects.filter(network__isnull=True,
                                                      asn=asn)  # get the asn with no network associated
                        if len(empty_ass) <= 0:
                            as_origin = AS(asn=asn)  # create the empty-network AS
                            as_origin.save()
                        elif len(empty_ass) > 1:
                            continue
                        else:
                            as_origin = empty_ass[0]

                    except Exception as e:
                        as_origin = AS(asn=asn)  # create the empty-network AS
                        as_origin.save()

                    if len(rtts) <= 0:
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
                        continue

                    as_destination = AS.objects.get_as_by_ip(destination_ip)
                    cc_destination = TestPoint.objects.get(ip_address=destination_ip).country

                    std_dev = numpy.std(rtts)
                    ProbeApiPingResult(
                        date_test=datetime.datetime.now(),
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
                        as_origin=as_origin.asn,
                        as_destination=as_destination.asn,
                        url="",
                        number_probes=len(rtts)
                    ).save()

                    print "ICMP ping from %s to %s is %.0f ms (%s samples, +- %.0f ms, %.0f samples stripped)" % (
                        cc_origin, cc_destination, numpy.mean(rtts), len(rtts), 2 * std_dev, _n - len(rtts))

        ccs = get_countries().keys()

        tps = SpeedtestTestPoint.objects.get_ipv4().filter(enabled=True).distinct('country').order_by(
            'country')

        urls = []
        thread_pool = ThreadPool(50)

        then = datetime.datetime.now()

        print "tps %s x ccs %s" % (len(tps), len(ccs))

        for tp in tps:

            # sanity check before building URLs
            online = tp.check_point(timeout=10, save=False)
            if not online:
                print "Skipping %s" % (tp)
                continue

            for cc in ccs:

                destination_ip = tp.ip_address
                count = 10

                t = Template("https://probeapifree.p.mashape.com/Probes.svc/StartPingTestByCountry?"
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
                        'probeslimit': 10,
                        'timeout': 10000
                    }
                )
                url_probeapi = t.render(ctx)
                urls.append(url_probeapi)

        thread_pool.map(do_work, urls)

        thread_pool.close()
        thread_pool.join()