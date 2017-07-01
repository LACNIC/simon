import pytz
import json
from collections import defaultdict
from datetime import datetime
from simon_app.models import ResultsManager
from simon_project.settings import STATIC_ROOT


def export_traces(trs, filename):
    comments = []

    now = datetime.now().replace(second=0, microsecond=0)
    uy = pytz.timezone('America/Montevideo')
    now = uy.localize(now)
    comments.append(["# Data exported at %s (%s)." % (now, now.tzinfo)])

    traces = []
    for tr in trs:
        serializable_trace = defaultdict(str)

        serializable_trace['country_destination'] = tr.country_destination
        serializable_trace['country_origin'] = tr.country_origin
        serializable_trace['as_destination'] = tr.as_destination
        serializable_trace['as_origin'] = tr.as_origin
        serializable_trace['hop_count'] = tr.hop_count

        hops = tr.traceroutehop_set.all()
        serializable_trace['hops'] = []
        for i, hop in enumerate(hops):
            serializable_hop = defaultdict(str)

            serializable_hop['index'] = i + 1

            serializable_hop['country_destination'] = hop.country_destination
            serializable_hop['country_origin'] = hop.country_origin
            serializable_hop['as_destination'] = hop.as_destination
            serializable_hop['as_origin'] = hop.as_origin

            serializable_hop['min_rtt'] = hop.min_rtt
            serializable_hop['avg_rtt'] = hop.ave_rtt
            serializable_hop['med_rtt'] = hop.median_rtt
            serializable_hop['max_rtt'] = hop.max_rtt

            if hop.ip_origin is not None:
                serializable_hop['ip_origin'] = ResultsManager.show_address_to_the_world(hop.ip_origin)
            if hop.ip_destination is not None:
                serializable_hop['ip_destination'] = ResultsManager.show_address_to_the_world(hop.ip_destination)

            uy = pytz.timezone(pytz.country_timezones['UY'][0])
            try:
                tz_probe = pytz.timezone(pytz.country_timezones[hop.country_origin][0])
            except KeyError as e:
                tz_probe = uy
            try:
                tz_target = pytz.timezone(pytz.country_timezones[hop.country_destination][0])
            except KeyError as e:
                tz_target = uy

            date = uy.localize(
                hop.date_test.replace(tzinfo=None))  # uy.localize(sm.date_test + timedelta(hours=03))
            date_utc = pytz.utc.normalize(date)
            date_probe = tz_probe.normalize(date)
            date_target = tz_target.normalize(date)
            serializable_hop['date_probe'] = str(date_probe)
            serializable_hop['date_target'] = str(date_target)
            serializable_hop['date_utc'] = str(date_utc)

            serializable_trace['hops'].append(serializable_hop)

        traces.append(serializable_trace)

    with open(STATIC_ROOT + "%s.json" % filename, 'wb') as jsonfile:
        jsonfile.write(json.dumps(traces))
        jsonfile.close()
