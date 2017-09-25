from django.core.management.base import BaseCommand
from simon_app.models.v6perf import *
from datetime import datetime
import requests, json


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = 'https://stats.labs.apnic.net/v6perf'
        # url = 'http://localhost:8000/static/simon_app/v6perf.json'
        domstring = requests.get(url).text

        diff_list = domstring.split('[\'Country\', \'Mean RTT Diff\'],')[1].split(']);')[0].replace('\'', '"')
        s_diff_list = "[%s]" % diff_list
        for item in json.loads(s_diff_list):
            cc = item[0]
            diff = item[1]
            #         v6_rate = row[V6USERRATE]
            #         now = datetime.datetime.now()
            #         dualstack = row[DUALSTACK]
            #
            v6perf = V6Perf(
                country=cc,
                diff=float(diff),
                date=datetime.now()
            )
            v6perf.save()
