from django.core.management.base import BaseCommand
from simon_app.models.models import Country
from simon_app.models.v6perf import *
from simon_project import passwords
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

        APIKEY = passwords.IMPORTIO_API_KEY

        importio_endpoint = "https://data.import.io/extractor"

        daily = "4beced29-001e-4320-8c03-351d560ba2b8"
        url_daily = "%s/%s/csv/latest?_apikey=%s" % (importio_endpoint, daily, APIKEY)

        monthly = "39b6c0fc-3927-4ee7-9a60-75ac918a2386"
        url_monthly = "%s/%s/csv/latest?_apikey=%s" % (importio_endpoint, monthly, APIKEY)

        data = requests.get(url_daily).content
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

        data = requests.get(url_monthly).content
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

            v6perf_monthly = V6PerfMonthly(
                country=cc,
                v6_rate=float(v6_rate.split("%")[0]),
                dualstack=float(dualstack.split("%")[0]),
                diff=float(diff),
                date=now
            )
            v6perf_monthly.save()



