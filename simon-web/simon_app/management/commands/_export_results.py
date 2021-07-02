from builtins import str
import json
import pytz
from collections import defaultdict
from datetime import datetime
from simon_app.models import ResultsManager, ProbeApiPingResult
from simon_project.settings import STATIC_ROOT


def timezone_or_default(cc, default=None):
    try:
        cc_timezone = pytz.country_timezones[cc][0]
        return pytz.timezone(cc_timezone)
    except KeyError as e:
        return default


def export(sms, filename, pks=[]):
    """
        :param sms: Results to be exported
        :param filename: filename to be written with those results
        :return: void
    """

    if pks:
        sms = ProbeApiPingResult.objects.filter(pk__in=pks)

    comments = []

    now = datetime.now().replace(second=0, microsecond=0)
    uy = pytz.timezone('America/Montevideo')
    now = uy.localize(now)
    comments.append(["# Data exported at %s (%s)." % (now, now.tzinfo)])

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

        uy = pytz.timezone(pytz.country_timezones['UY'][0])
        tz_probe = timezone_or_default(sm.country_origin, default=uy)
        tz_target = timezone_or_default(sm.country_destination, default=uy)

        date = uy.localize(sm.date_test.replace(tzinfo=None))  # uy.localize(sm.date_test + timedelta(hours=03))
        date_utc = pytz.utc.normalize(date)
        date_probe = tz_probe.normalize(date)
        date_target = tz_target.normalize(date)
        serializable_object['date_probe'] = str(date_probe)
        serializable_object['date_target'] = str(date_target)
        serializable_object['date_utc'] = str(date_utc)

        serializable_object['target_url'] = sm.url

        if sm.ip_origin is not None:
            serializable_object['ip_origin'] = ResultsManager.show_address_to_the_world(sm.ip_origin)
        if sm.ip_destination is not None:
            serializable_object['ip_destination'] = ResultsManager.show_address_to_the_world(sm.ip_destination)

        res.append(serializable_object)
        del sm

    with open(STATIC_ROOT + "/%s.json" % filename, 'wb') as jsonfile:
        encoder = json.JSONEncoder()
        for chunk in encoder.iterencode(res):
            jsonfile.write(chunk)
