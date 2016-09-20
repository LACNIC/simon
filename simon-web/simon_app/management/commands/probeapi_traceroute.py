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
from multiprocessing.dummy import Pool as ThreadPool
from simon_app.api_views import get_cc_from_ip_address


def get_countries(ccs=[]):
    url = settings.PROBEAPI_ENDPOINT + "/GetCountries"

    try:
        print "Getting countries..."
        response = get_probeapi_response(url)
        py_object = json.loads(response)
        res = {}
        for p in py_object["GetCountriesResult"]:
            cc = p["CountryCode"]
            if cc in ccs:
                res[cc] = p["ProbesCount"]
        return res
    except Exception as e:
        pass


def get_probeapi_response(url):
    req = urllib2.Request(url)
    req.add_header("apikey", settings.KONG_API_KEY)
    req.add_header("Accept", "application/json")
    response = urllib2.urlopen(req).read()
    return response


class Command(BaseCommand):
    threads = 50
    max_job_queue_size = 0  # 0 for limitless
    max_points = 0  # 0 for limitless
    ping_count = 3  # amount of ICMP pings performed per test

    def handle(self, *args, **options):
        def do_work(url_probeapi):
            print url_probeapi

            try:
                response = get_probeapi_response(url_probeapi)
                print response
                if response is not None:
                    print response
                    process_response(response)
            except Exception as e:
                print e
                pass

            finally:
                return

        def process_response(response):

            now = datetime.datetime.now()
            py_object = json.loads(str(response))

            N = len(py_object['StartTracertTestByCountryResult'])
            if N <= 0:
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

                    tr = TracerouteResult(
                        # ip_origin=ip_origin,
                        # country_origin=cc_origin
                    )
                    tr.save()

                    for hop in traceroute["Tracert"]:
                        ip_destination = hop['IP']
                        as_destination = AS.objects.get_as_by_ip(destination_ip)
                        cc_destination = get_cc_from_ip_address(ip_destination)
                        status = hop["Status"]

                        if status != "OK" or ip_destination is None:
                        # Timed out hops
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
                                country_destination=cc_destination,
                                ip_version=ip_version,
                                as_origin=as_origin.asn,
                                as_destination=as_destination.asn,
                                number_probes=0,

                                tester="probeapi",
                                tester_version="1",
                                traceroute_result=tr
                            )
                            tr.traceroutehop_set.add(tr_hop)
                            tr.hop_count += 1
                            tr.save()
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
                        tr.traceroutehop_set.add(tr_hop)
                        tr.hop_count += 1
                        tr.save()
                    tr.country_destination = tr.traceroutehop_set.last().country_destination
                    tr.country_origin = tr.traceroutehop_set.last().country_origin
                    tr.as_destination = tr.traceroutehop_set.last().as_destination
                    tr.as_origin = tr.traceroutehop_set.last().as_origin
                    tr.save()

                return

        ccs = get_countries().keys()

        tps = SpeedtestTestPoint.objects.get_ipv4().filter(enabled=True).distinct('country').order_by(
            'country')  # one TP per country TODO get *really* random tests... TODO get ipv6!!!

        urls = []
        thread_pool = ThreadPool(self.threads)

        then = datetime.datetime.now(tz=GMTUY())

        if self.max_points > 1:
            tps = tps[:self.max_points]
        elif self.max_points == 1:
            tps = [tps[0]]

        print "TPs %s x CCs %s" % (len(tps), len(ccs))
        then = datetime.datetime.now(tz=GMTUY())
        for i, tp in enumerate(tps):

            # sanity check
            online = tp.check_point(protocol="icmp")
            if not online:
                continue

            for cc in ccs:
                destination_ip = tp.ip_address
                ping_count = self.ping_count

                max_hops = 50
                ping_time = 1000
                sleep_time = 1000
                tx_time = 10000
                timeout = ping_count * max_hops * (ping_time + sleep_time) + tx_time  # seconds

                t = Template(
                    "https://probeapifree.p.mashape.com/Probes.svc/StartTracertTestByCountry?"
                    "countrycode={{ cc }}&"
                    # "count={{ count }}&"
                    "destination={{ destination }}&"
                    "probeslimit={{ probeslimit }}"
                    # "timeout={{ timeout }}"
                )

                ctx = Context(
                    {
                        'cc': cc,
                        # 'count': ping_count,
                        'destination': destination_ip,
                        'probeslimit': 2 * len(ccs)
                        # 'timeout': timeout
                    }
                )
                url_probeapi = t.render(ctx)
                if self.max_job_queue_size == 0 or len(urls) <= self.max_job_queue_size:
                    urls.append(url_probeapi)

        print "TPs %s x CCs %s" % (len(tps), len(ccs))
        print "Launching %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls))
        thread_pool.map(do_work, urls)

        thread_pool.close()
        thread_pool.join()

        print "Command ended with %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls))
        print "Command took %s" % (datetime.datetime.now(tz=GMTUY()) - then)