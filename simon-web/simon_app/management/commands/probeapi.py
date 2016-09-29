#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.template import Template, Context

from simon_app.models import *
from simon_app.reportes import GMTUY
from probeapi_traceroute import get_countries, get_probeapi_response

from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
from random import shuffle
import json
import datetime
import numpy
import logging


class ProbeApiMeasurement():
    """
        Class that holds the logic to perform a ProbeAPI measurement
    """

    # import guppy
    # heapy = guppy.hpy()

    def __init__(self):
        pass

    logger = logging.getLogger(__name__)

    lock = Lock()

    threads = 50
    max_job_queue_size = 200  # 0 for limitless
    max_points = 0  # 0 for limitless
    ping_count = 10  # amount of ICMP pings performed per test

    results = []

    def init(self, tps=[], ccs=[]):
        def do_work(url):
            try:

                # print self.heapy.heap().get_rp(), self.heapy.setref()

                response = get_probeapi_response(url)
                if response is not None:
                    process_response(response, url)

            except Exception as e:
                print e
                pass

            finally:
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
                    result = ProbeApiPingResult(
                        date_test=datetime.datetime.now(tz=GMTUY()), \
                        ip_origin='', \
                        ip_destination=destination_ip, \
                        min_rtt=numpy.amin(rtts), \
                        max_rtt=numpy.amax(rtts), \
                        ave_rtt=numpy.mean(rtts), \
                        dev_rtt=std_dev, \
                        median_rtt=numpy.median(rtts), \
                        packet_loss=packet_loss, \
                        country_origin=cc_origin, \
                        country_destination=cc_destination, \
                        ip_version=6 if ':' in destination_ip else 4, \
                        as_origin=as_origin.asn, \
                        as_destination=as_destination.asn, \
                        url="", \
                        number_probes=len(rtts)
                    )
                    result.save()

                    self.lock.acquire()
                    self.results.append(result)
                    self.lock.release()

                    self.logger.info(
                        "ICMP ping from %s to %s is %.0f ms (%s samples, +- %.0f ms, %.0f samples stripped)" % (
                            cc_origin, cc_destination, numpy.mean(rtts), len(rtts), 2 * std_dev, _n - len(rtts)))

        ccs = get_countries(ccs=ccs).keys()  # get countries with running probes...

        urls = []
        thread_pool = ThreadPool(self.threads)

        then = datetime.datetime.now(tz=GMTUY())

        if self.max_points > 1:
            tps = tps[:self.max_points]
        elif self.max_points == 1:
            tps = [tps[0]]

        tps = list(tps)
        shuffle(tps)  # shuffle in case the script get aborted (do not run only the small alphanumeric tps only)

        for tp in tps:

            # sanity check before building URLs
            online = tp.check_point(timeout=10, save=False, protocol="icmp")
            if not online:
                print "Skipping %s" % (tp)
                continue

            destination_ip = tp.ip_address
            ping_count = self.ping_count

            for cc in ccs:

                round_trip = 2
                time_for_each_ping = 1000
                tx_time = 10000
                timeout = ping_count * round_trip * time_for_each_ping + tx_time

                t = Template(
                    settings.PROBEAPI_ENDPOINT + "/StartPingTestByCountry?"
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
                        'probeslimit': 3,  # 10 (probes per CC)
                        'timeout': timeout
                    }
                )
                url_probeapi = t.render(ctx)
                if self.max_job_queue_size == 0 or len(urls) < self.max_job_queue_size:
                    urls.append(url_probeapi)

        self.logger.info("TPs %s x CCs %s" % (len(tps), len(ccs)))
        self.logger.info("Launching %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls)))
        thread_pool.map(do_work, urls)

        thread_pool.close()
        thread_pool.join()

        self.logger.info("Command ended with %.0f worker threads on a %.0f jobs queue" % (self.threads, len(urls)))
        self.logger.info("Command took %s" % (datetime.datetime.now(tz=GMTUY()) - then))

        return self.results
