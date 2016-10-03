from django.core.management.base import BaseCommand
from simon_app.models.models import Country
from simon_app.models.v6perf import *
import datetime
import StringIO
import requests
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):

        ccs = Country.objects.get_all_countrycodes()

        CC=1
        DIFF = 9
        PAIRSAMPLES = 10
        V6FAILURE = 11
        V6SAMPLES = 12
        DUALSTACK = 13
        DUALSTACK_ = 14
        V6USERRATE = 15

        APIKEY = "0857f45cdfd84d5089acbd8a50f39895655317f534d5aa3f51dabdf96894ea128aa9ef69c044086350c5c6448d807c3a02c198e8ab7b892393bf2a631018f5b1b60951f8838670f27c2bd69b6b81b6fc"
        daily = "6016e9a1-d86c-4490-bb63-f6f4909ff395/csv/latest?_apikey=%s" % APIKEY
        url = "https://data.import.io/extractor/%s" % daily
        data = requests.get(url).content
        csv_data = StringIO.StringIO(data)
        reader = csv.reader(csv_data)
        for row in reader:
            cc = row[CC]
            if cc not in ccs:
                continue

            diff = row[DIFF]
            v6_rate = row[V6USERRATE]
            now = datetime.datetime.now()
            dualstack = row[DUALSTACK]

            v6perf = V6Perf(
                country=cc,
                v6_rate=float(v6_rate.split("%")[0]),
                dualstack=float(dualstack.split("%")[0]),
                diff=float(diff),
                date=now
            )
            v6perf.save()



