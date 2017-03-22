from django.core.management.base import BaseCommand
from simon_app.models import Country, ProbeApiPingResult, ResultsManager
from collections import defaultdict
from datetime import datetime, timedelta
import datetime
import pytz
import json
from simon_project.settings import STATIC_ROOT
from django.db.models import Q


class Command(BaseCommand):
    """
    Command to export Africa Connectivity results to the world
    """

    def handle(self, *args, **options):
        comments = []

        now = datetime.datetime.now().replace(second=0, microsecond=0)
        uy = pytz.timezone('America/Montevideo')
        now = uy.localize(now)
        comments.append(["# Data exported at %s (%s)." % (now, now.tzinfo)])

        ccs = Country.objects.get_afrinic_countrycodes()
        start=datetime.datetime(year=2017, month=03, day=21)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )
        print len(sms)

        res = []
        for sm in sms:
            serializable_object = defaultdict(str)

            serializable_object['country_destination'] = sm.country_destination
            serializable_object['country_origin'] = sm.country_origin
            serializable_object['as_destination'] = sm.as_destination
            serializable_object['as_origin'] = sm.as_origin

            serializable_object['min_rtt'] = sm.min_rtt
            serializable_object['avg_rtt'] = sm.ave_rtt
            serializable_object['med_rtt'] = sm.median_rtt
            serializable_object['max_rtt'] = sm.max_rtt

            tz_probe = pytz.timezone(pytz.country_timezones[sm.country_origin][0])
            tz_target = pytz.timezone(pytz.country_timezones[sm.country_destination][0])
            uy = pytz.timezone(pytz.country_timezones['UY'][0])

            date = uy.localize(sm.date_test.replace(tzinfo=None))  # uy.localize(sm.date_test + timedelta(hours=03))
            date_utc = pytz.utc.normalize(date)
            date_probe = tz_probe.normalize(date)
            date_target = tz_target.normalize(date)
            serializable_object['date_probe'] = str(date_probe)
            serializable_object['date_target'] = str(date_target)
            serializable_object['date_utc'] = str(date_utc)

            if sm.ip_origin is not None:
                serializable_object['ip_origin'] = ResultsManager.show_address_to_the_world(sm.ip_origin)
            if sm.ip_destination is not None:
                serializable_object['ip_destination'] = ResultsManager.show_address_to_the_world(sm.ip_destination)

            res.append(serializable_object)

        with open(STATIC_ROOT + '/results-africa-connectivity.json', 'wb') as jsonfile:
            jsonfile.write(json.dumps(res))
            jsonfile.close()
