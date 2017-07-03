#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.template import Template, Context
from django.db import transaction
from simon_app.models import *
from simon_app.reportes import GMTUY
from simon_app.api_views import get_cc_from_ip_address
from probeapi_libs import get_countries, get_probeapi_response

from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
from random import shuffle
import json
import datetime
import numpy
import logging
import urlparse


class ProbeApiTraceroute():
    """
        Class that holds the logic to perform a ProbeAPI measurement
    """

    def __init__(self, threads=50, max_job_queue_size=200, max_points=0, ping_count=10):
        self.threads = threads
        self.max_job_queue_size = max_job_queue_size  # 0 for limitless
        self.max_points = max_points  # 0 for limitless
        self.ping_count = ping_count  # amount of ICMP pings performed per test

    logger = logging.getLogger(__name__)

    lock = Lock()

    results = []

    def init(self, tps=[], ccs=[]):
        EMPTY_RESULTS = []

        def do_work(url):
            try:

                response = get_probeapi_response(url)

                if response is not None:
                    self.process_response(response, requested_url=url)

            except Exception as e:
                print e
                pass

            finally:
                return

        ccs = get_countries(ccs=ccs)

        if ccs is None:
            return EMPTY_RESULTS

        ccs = ccs.keys()  # get countries with running probes...

        urls = []
        thread_pool = ThreadPool(self.threads)

        then = datetime.datetime.now(tz=GMTUY())

        if self.max_points > 1:
            tps = tps[:self.max_points]
        elif self.max_points == 1:
            tps = [tps[0]]

        tps = list(tps)
        shuffle(tps)  # shuffle in case the script gets aborted (do not run only the small alphanumeric tps only)

        for tp in tps:

            if isinstance(tp, SpeedtestTestPoint) or isinstance(tp, TestPoint):
                # normal flux... skip if targetting rotating domain

                # sanity check before building URLs
                online = tp.check_point(timeout=10, save=False, protocol="icmp")
                if not online:
                    print "Skipping %s" % (tp)
                    continue

                destination_ip = tp.ip_address
            else:
                destination_ip = tp  # the domain itself

            urls += self.build_url_for_tp(ccs, destination_ip, self.ping_count)

        self.logger.info("TPs %s x CCs %s" % (len(tps), len(ccs)))
        self.logger.info("Launching %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls)))
        for u in urls:
            print u

        thread_pool.map(do_work, urls)

        thread_pool.close()
        thread_pool.join()

        self.logger.info("Command ended with %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls)))
        self.logger.info("Command took %s" % (datetime.datetime.now(tz=GMTUY()) - then))

        return self.results

    def process_response(self, response, requested_url=''):
        """
        :param response:
        :param requested_url:
        :param persist:
        :return: Parsed list of TracerouteResult s
        """

        now = datetime.datetime.now(tz=GMTUY())

        py_object = json.loads(response, parse_int=int)['StartTracertTestByCountryResult']

        # py_object is a list
        if len(py_object) <= 0:
            return

        results = []  # results to be returned

        for probe_target_result in py_object:

            target = requested_url.split('&')[2].split('=')[1]

            cc_origin = probe_target_result['Country']['CountryCode']

            as_string = probe_target_result['ASN']['AsnID']
            if len(as_string) > 2:
                as_origin = as_string[2:]  # strip 'AS'
            else:
                as_origin = 0

            packet_loss = 0

            for traceroute in probe_target_result['TRACERoute']:

                destination_ip = traceroute['IP']

                cc_destination = TestPoint.objects.get_or_none(ip_address=destination_ip)
                if cc_destination is None:
                    cc_destination = 'XX'
                else:
                    cc_destination = cc_destination.country

                traceroute_result = TracerouteResult(
                    ip_origin='0.0.0.1',
                    ip_destination=destination_ip,
                    as_origin=as_origin,
                    as_destination=AS.objects.get_as_by_ip(destination_ip).asn,
                    country_origin=cc_origin,
                    country_destination=cc_destination
                )

                traceroute_result.save()

                for hop in traceroute['Tracert']:

                    hop_destination_ip = hop['IP']

                    voided = False

                    rtts = []
                    for r in hop['PingTimeArray']:
                        try:
                            rtts.append(int(r))
                        except Exception as e:
                            packet_loss += 1
                            continue

                    if len(rtts) == 0:
                        voided = True
                    else:

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

                        if len(rtts) == 0:
                            voided = True

                    hop_as_destination = AS.objects.get_as_by_ip(hop_destination_ip)
                    hop_cc_destination = get_cc_from_ip_address(hop_destination_ip)

                    if hop_cc_destination is None:
                        hop_cc_destination = 'XX'

                    std_dev = numpy.std(rtts)

                    if voided:
                        hop = TracerouteHop(
                            date_test=now,
                            # ip_origin='',
                            ip_destination=hop_destination_ip,
                            min_rtt=0,
                            max_rtt=0,
                            ave_rtt=0,
                            dev_rtt=0,
                            median_rtt=0,
                            packet_loss=packet_loss,
                            country_origin=cc_origin,
                            country_destination=hop_cc_destination,
                            ip_version=6 if ':' in hop_destination_ip else 4,
                            as_origin=as_origin,
                            as_destination=hop_as_destination.asn,
                            url=target,
                            number_probes=len(rtts)
                        )
                    else:
                        hop = TracerouteHop(
                            date_test=now,
                            # ip_origin='',
                            ip_destination=hop_destination_ip,
                            min_rtt=numpy.amin(rtts),
                            max_rtt=numpy.amax(rtts),
                            ave_rtt=numpy.mean(rtts),
                            dev_rtt=std_dev,
                            median_rtt=numpy.median(rtts),
                            packet_loss=packet_loss,
                            country_origin=cc_origin,
                            country_destination=hop_cc_destination,
                            ip_version=6 if ':' in hop_destination_ip else 4,
                            as_origin=as_origin,
                            as_destination=hop_as_destination.asn,
                            url=target,
                            number_probes=0
                        )

                    traceroute_result.traceroutehop_set.add(hop)  # save()

                # to be returned
                results.append(traceroute_result)
        return results

    def build_url_for_tp(self, ccs, destination_ip, ping_count):

        urls = []

        for cc in ccs:

            hops = 10
            round_trip = 2 * hops
            time_for_each_ping = 1000
            tx_time = 10000
            timeout = ping_count * round_trip * time_for_each_ping + tx_time

            t = Template(
                settings.PROBEAPI_ENDPOINT + "/StartTracertTestByCountry?"
                                             "countrycode={{ cc }}&"
                                             "count={{ count }}&"
                                             "destination={{ destination }}&"
                                             "probeslimit={{ probeslimit }}&"
                                             "timeout={{ timeout }}"
            )

            ctx = Context(
                {
                    'cc': cc,
                    'count': ping_count,
                    'destination': destination_ip,
                    'probeslimit': 10,  # 10 (probes per CC)
                    'timeout': timeout
                }
            )
            url_probeapi = t.render(ctx)
            if self.max_job_queue_size == 0 or len(urls) < self.max_job_queue_size:
                urls.append(url_probeapi)

        return urls
