import json
import numpy
from datadog import statsd
from django.db import models
from datetime import datetime
from requests import get, post
from simon_app.models import AS, ProbeApiPingResult, TestPoint
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
    reply_1 = models.TextField(
        help_text="JSON payload as a text field. This should be JSONField in higher versions of PostgreSQL"
    )
    reply_2 = models.TextField(
        help_text="JSON payload as a text field. This should be JSONField in higher versions of PostgreSQL"
    )
    stage_requested = models.BooleanField(
        default=False,
        help_text="Determines is a test results has already been collected from the ProbePAI platform"
    )
    stage_collected = models.BooleanField(
        default=False,
        help_text="Determines is a test results has already been collected from the ProbePAI platform"
    )

    def request(self, ccs=None, destinations=None, ping_count=10, max_probes=10, timeout=1000):
        """
        :param ccs: list
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

        if ccs is None or destinations is None:
            return {}

        test_settings = {
            "PingType": "icmp",
            "BufferSize": 32,
            "Count": ping_count,
            "Fragment": 1,
            "Ipv4only": 0,
            "Ipv6only": 0,
            "Resolve": 0,
            "Sleep": 1000,
            "Ttl": 128,
            "Timeout": timeout,
            "TestCount": max_probes,
            "Sources": [{"CountryCode": cc} for cc in ccs],
            "Destinations": destinations,
            "ProbeInfoProperties": [
                "Latitude", "Longitude", "ProbeID", "CountryCode", "CityName", "ASN", "Network", "NetworkID"
            ]
        }

        return self.post(
            test_settings=test_settings
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

        if test_settings is None:
            return {}

        j = post(
            url=PROBEAPI_ENDPOINT_V2 + "/StartPingTest?apikey=" + KONG_API_KEY,
            json={
                "testSettings": test_settings
            },
            headers={
                "content-type": "application/json"
            }
        ).json()

        if j['StartPingTestResult']['Status']['StatusCode'] != "200":
            # something went wrong when invoking the api
            pass
        self.stage_requested = True
        self.date_1 = datetime.now()
        self.save()

        s = json.dumps(j)

        self.reply_1 = s
        self.probeapi_id = j["StartPingTestResult"]["TestID"].encode()

        self.save()

        print j
        return j

    def get(self, test_id=None, persist=True):

        if self.probeapi_id is None and test_id is None:
            return {}

        test_id = test_id if test_id else self.probeapi_id

        self.date_2 = datetime.now()
        j = get(
            PROBEAPI_ENDPOINT_V2 + "/GetPingResults?" + "testID=" + test_id + "&apikey=" + KONG_API_KEY,
            headers={
                "content-type": "application/json"
            }
        ).json()

        # 401 'Test failed or partially failed, not enough results'
        if j.get("ResponseStatus", {}).get("StatusCode", {}) not in ["200", "401"]:
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

                for r in j["PingTestResults"]:

                    if r["Status"] != "OK":
                        # something went wrong
                        continue

                    cc = r.get("CountryCode", "XX")
                    probe = r["ProbeInfo"]
                    probe_id = probe["ProbeID"]  # TODO store in DB
                    asn = probe["ASN"]

                    ip_destination = r["IP"]
                    country_destination = TestPoint.objects.get_or_none(ip_address=ip_destination, enabled=True)
                    if not country_destination:
                        country_destination = "XX"
                    as_destination = AS.objects.get_as_by_ip(ip_destination).asn

                    rtts = [int(rtt) for rtt in r["PingArray"]]

                    result = ProbeApiPingResult.objects.create(
                        version=2,
                        ip_destination=ip_destination,
                        number_probes=len(rtts),
                        min_rtt=min(rtts),
                        max_rtt=max(rtts),
                        ave_rtt=int(sum(rtts)/len(rtts)),
                        dev_rtt=numpy.std(rtts),
                        median_rtt=numpy.median(rtts),
                        packet_loss=0,  # TODO
                        country_origin=cc,
                        country_destination=country_destination,
                        ip_version=4 if '.' in ip_destination else 6,
                        as_origin=asn,
                        as_destination=as_destination,
                    #     probeApiRequestId=this one
                    )

                    statsd.increment(
                        'Result via Speedchecker',
                        tags=[
                                 'type:' + result.testype,
                                 'tester:' + result.tester,
                                 'url:' + result.url
                             ] + DATADOG_DEFAULT_TAGS
                    )

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
