import json
from django.db import models
from datetime import datetime
from requests import get, post
from simon_project.settings import PROBEAPI_ENDPOINT_V2, KONG_API_KEY


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

    def post(self, probe_test_settings=None):
        # {
        #     "StartPingTestResult": {
        #         "Status": {
        #             "StatusCode": "200",
        #             "StatusText": "OK"
        #         },
        #         "TestID": "a3d2d418-4f24-43f9-a546-c51551f00a6c"
        #     }
        # }

        if probe_test_settings is None:
            return {}

        j = post(
            PROBEAPI_ENDPOINT_V2 + "/StartPingTest?apikey=" + KONG_API_KEY,
            headers={
                "content-type: application/json"
            }
        ).json()
        self.stage_requested = True
        self.date_1 = datetime.now()
        self.save()

        s = json.dumps(j)

        self.reply_1 = s
        self.probeapi_id = j["StartPingTestResult"]["TestID"]

        self.save()

        return j

    def get(self, test_id=None, persist=True):

        if test_id is None:
            return {}

        self.date_2 = datetime.now()
        j = get(
            PROBEAPI_ENDPOINT_V2 + "/GetPingResults?" + "testID=" + test_id + "&apikey=" + KONG_API_KEY,
            headers={
                "content-type: application/json"
            }
        ).json()

        s = json.dumps(j)

        self.reply_2 = s
        self.stage_collected = True

        if persist:
            self.save()

        return j
