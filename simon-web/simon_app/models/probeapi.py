import json
import numpy
from datadog import statsd
from django.db import models
from datetime import datetime
from netaddr import IPAddress
from requests import get, post
from simon_app.models import AS, ProbeApiPingResult, SpeedtestTestPoint, ProbeapiTracerouteResult, ProbeapiTracerouteHop
from simon_project.settings import PROBEAPI_ENDPOINT_V2, KONG_API_KEY, DATADOG_DEFAULT_TAGS


class ProbeApiTestSettings(object):

    def __init__(self):

        self.pingtype = 'icmp'
        self.buffersize = 32
        self.count = 3
        self.fragment = 1
        self.ipv4only = 0
        self.ipv6only = 0
        self.resolve = 0
        self.sleep = 1000
        self.ttl = 128
        self.timeout = 1000
        self.testcount = 10
        self.sources = dict()
        self.sources = list()
        self.probeinfoproperties = list()


class ProbeApiRequest(models.Model):

    date_1 = models.DateTimeField(
        default=datetime.now,
        help_text="Datetime this test was requested to the platform"
    )
    date_2 = models.DateTimeField(
        default=datetime.now,
        help_text="Last datetime this results was requested from the platform"
    )
    probeapi_id = models.CharField(
        max_length=1024
    )
    test_settings = models.TextField(
        help_text="JSON request as a text field. This should be JSONField in higher versions of PostgreSQL",
        default='{}'
    )
    reply_1 = models.TextField(
        help_text="JSON payload as a text field. This should be JSONField in higher versions of PostgreSQL"
    )
    reply_2 = models.TextField(
        help_text="JSON payload as a text field. This should be JSONField in higher versions of PostgreSQL"
    )
    stage_requested = models.BooleanField(
        default=False,
        help_text="Determines is a test results has already been collected from the ProbeAPI platform"
    )
    stage_collected = models.BooleanField(
        default=False,
        help_text="Determines is a test results has already been collected from the ProbeAPI platform"
    )
    test_type = models.CharField(
        default='ping',
        max_length=16
    )

    def request(self, sources=None, destinations=None, ping_count=10, max_probes=10, timeout=1000):
        """
        :param sources: list
        :param destinations: list
        :param max_probes:
        :param ping_count:
        :return:
        """

        # {"testSettings":
        # {"PingType": "icmp", "BufferSize": 32, "Count": 3, "Fragment": 1, "Ipv4only": 0, "Ipv6only": 0,
        #                   "Resolve": 0, "Sleep": 1000, "Ttl": 128, "Timeout": 1000, "TestCount": 10,
        #                   "Sources": [{"CountryCode": "US"}], "Destinations": ["www.google.com"],
        #                   "ProbeInfoProperties": ["Latitude", "Longitude", "ProbeID", "CountryCode", "CityName"]}}

        if sources is None or destinations is None:
            return {}

        sources_settings = []
        for source in sources:
            try:
                source = int(source)
                key = "ASN"
            except ValueError as ve:
                key = "CountryCode"
            sources_settings.append(
                {key: source}
            )

        test_settings = {}
        if self.test_type == 'ping':
            test_settings["PingType"] = "icmp"

        elif self.test_type == 'traceroute':
            test_settings["Timeout"] = 60000
            test_settings["HopTimeout"] = 2000
            test_settings["MaxFailedHops"] = 64  # allow failed hops

        base_settings = {
            "Platform": "PC",
            "BufferSize": 32,
            "Count": ping_count,
            "Fragment": 1,
            "Ipv4only": 0,
            "Ipv6only": 0,
            "Resolve": 1,
            "Sleep": 1000,
            "Ttl": 128,
            "Timeout": timeout,
            "TestCount": max_probes,
            "Sources": sources_settings,
            "Destinations": destinations,
            "ProbeInfoProperties": [
                "Latitude", "Longitude", "ProbeID", "CountryCode", "CityName", "ASN", "Network", "NetworkID",
                "IPAddress"
            ]
        }

        z = test_settings.copy()
        z.update(base_settings)
        self.test_settings = json.dumps(z)
        self.save()

        return self.post(
            test_settings=z
        )

    def post(self, test_settings=None):
        # {
        #     "StartPingTestResult": {
        #         "Status": {
        #             "StatusCode": "200",
        #             "StatusText": "OK"
        #         },
        #         "TestID": "a3d2d418-4f24-43f9-a546-c51551f00a6c"
        #     }
        # }

        if self.test_type == "ping":
            endpoint = "/StartPingTest"
            key = "StartPingTestResult"
        elif self.test_type == "traceroute":
            endpoint = "/StartTracertTest"
            key = "StartTracertTestResult"
        else:
            return None

        if test_settings is None:
            return {}

        j = post(
            url=PROBEAPI_ENDPOINT_V2 + endpoint + "?apikey=" + KONG_API_KEY,
            json={
                "testSettings": test_settings
            },
            headers={
                "content-type": "application/json"
            }
        ).json()

        s = json.dumps(j)
        self.reply_1 = s

        r = j.get(key, {}).get("Status", {}).get("StatusCode", {})
        if r != "200":
            # something went wrong when invoking the api
            self.save()
            pass

        self.stage_requested = True
        self.date_1 = datetime.now()
        self.save()

        self.probeapi_id = j[key]["TestID"].encode()

        self.save()

        print j
        return j

    def parse_response(self, j):

        if "PingTestResults" in j:
            for r in j["PingTestResults"]:

                if r["Status"] != "OK":
                    # something went wrong
                    continue

                probe = r["ProbeInfo"]
                cc = probe.get("CountryCode", "XX")
                probe_id = probe["ProbeID"]  # TODO store in DB
                probe_ip = probe["IPAddress"].replace("X", str(0))
                asn = probe.get("ASN", 0)

                pings = r["PingArray"]
                if not pings:
                    continue
                ip_destination = r["IP"]
                tp = SpeedtestTestPoint.objects.filter(
                    ip_address=ip_destination,
                    enabled=True
                ).order_by(
                    '-date_created'
                ).first()
                if tp:
                    country_destination = tp.country
                else:
                    country_destination = "XX"
                if not country_destination:
                    country_destination = "XX"
                as_destination = AS.objects.get_as_by_ip(ip_destination).asn

                rtts = [int(rtt) for rtt in pings if rtt]
                if len(rtts) == 0: continue

                result = ProbeApiPingResult.objects.create(
                    version=2,
                    ip_destination=ip_destination,
                    ip_origin=probe_ip,
                    number_probes=len(rtts),
                    min_rtt=min(rtts),
                    max_rtt=max(rtts),
                    ave_rtt=int(sum(rtts) / len(rtts)),
                    dev_rtt=numpy.std(rtts),
                    median_rtt=numpy.median(rtts),
                    packet_loss=0,  # TODO
                    country_origin=cc,
                    country_destination=country_destination,
                    ip_version=4 if '.' in ip_destination else 6,
                    as_origin=asn,
                    as_destination=as_destination,

                    probeapi_probe_id=probe_id
                )

                statsd.increment(
                    'Result via Speedchecker',
                    tags=[
                             'type:' + result.testype,
                             'tester:' + result.tester,
                             'url:' + result.url
                         ] + DATADOG_DEFAULT_TAGS
                )
        elif "TracerouteTestResults" in j:
            for r in j["TracerouteTestResults"]:

                if r["TestStatus"]["StatusText"] != "OK":
                    # something went wrong
                    continue

                probe = r["ProbeInfo"]
                cc = probe.get("CountryCode", "XX")
                probe_id = probe["ProbeID"]  # TODO store in DB
                probe_ip = probe["IPAddress"].replace("X", str(0))

                asn = probe.get("ASN", 0)

                hops_objects = []
                hops = r.get("Tracert")
                result = ProbeapiTracerouteResult.objects.create(
                    ip_origin=probe_ip,
                    as_origin=asn,
                    country_origin=cc
                )

                for hop_number, hop in enumerate(hops):
                    hop_number += 1  # 1-based index for hop number

                    pings = hop["PingTimeArray"]
                    if not pings:
                        continue
                    ip_destination = hop["IP"]
                    try:
                        IPAddress(ip_destination)
                    except Exception as e:
                        ip_destination = '0.0.0.0'

                    country_destination = "XX"
                    as_destination = AS.objects.get_as_by_ip(ip_destination).asn

                    rtts = [int(rtt) for rtt in pings if rtt]
                    if len(rtts) == 0: continue  # TODO allow * * * ?

                    h = ProbeapiTracerouteHop.objects.create(
                        traceroute_result=result,
                        testype='traceroute',
                        hop_number=hop_number,

                        version=2,
                        ip_destination=ip_destination,
                        ip_origin=probe_ip,
                        number_probes=len(rtts),
                        min_rtt=min(rtts),
                        max_rtt=max(rtts),
                        ave_rtt=int(sum(rtts) / len(rtts)),
                        dev_rtt=numpy.std(rtts),
                        median_rtt=numpy.median(rtts),
                        packet_loss=0,  # TODO
                        country_origin=cc,
                        country_destination=country_destination,
                        ip_version=4 if '.' in ip_destination else 6,
                        as_origin=asn,
                        as_destination=as_destination,

                        probeapi_probe_id=probe_id
                    )
                    hops_objects.append(h)

                # 1 traceroute --> 1 result through the platform
                # get general info from last valid hop h, as TracerouteResult is a simple abstraction
                last_hop = result.probeapitraceroutehop_set.order_by('-hop_number').first()
                result.as_destination = last_hop.as_destination
                result.ip_destination = last_hop.ip_destination
                result.country_destination = last_hop.country_destination
                result.save()

                statsd.increment(
                    'Result via Speedchecker',
                    tags=[
                             'type:' + h.testype,
                             'tester:' + h.tester,
                             'url:' + h.url
                         ] + DATADOG_DEFAULT_TAGS
                )

    def get(self, test_id=None, persist=True):

        if self.probeapi_id is None and test_id is None:
            return {}

        test_id = test_id if test_id else self.probeapi_id

        self.date_2 = datetime.now()
        if self.test_type == "ping":
            endpoint = "/GetPingResults"
        elif self.test_type == "traceroute":
            endpoint = "/GetTracertResults"
        else:
            return
        j = get(
            PROBEAPI_ENDPOINT_V2 + endpoint + "?" + "testID=" + test_id + "&apikey=" + KONG_API_KEY,
            headers={
                "content-type": "application/json"
            }
        ).json()

        # 401 'Test failed or partially failed, not enough results'
        # 502 'Test failed, not enough probes'
        if j.get("ResponseStatus", {}).get("StatusCode", {}) not in ["200", "401", "502"]:
            # 202 == not ready
            # 504 == no probes
            self.reply_2 = json.dumps(j)
            self.save()  # store anything the api might give us back
            return j

        try:
            if self.stage_collected:
                return self.reply_2

            else:
                # first time it's being fetched
                self.parse_response(j)
        except Exception as e:
            print e
            pass

        s = json.dumps(j)
        self.reply_2 = s
        self.stage_collected = True

        if persist:
            self.save()

        print s
        return j
