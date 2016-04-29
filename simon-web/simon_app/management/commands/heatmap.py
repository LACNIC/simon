from __future__ import division
"""
    Script than saves the Heatmap data into static/data/heatmap
"""
from django.core.management.base import BaseCommand
from simon_app.models import Country, Params
from django.db.models import Q
from simon_app.functions import meanLatency
from simon_app.models import Results, AS
import json, sys

def asn_heatmap():
    rs = Results.objects.filter((Q(as_origin__gt=1) | Q(as_destination__gt=1)))# & Q(ip_version=4))
    ases = rs.order_by('as_origin').distinct('as_origin')
    ases_tmp = rs.order_by('as_destination').distinct('as_destination')
    ases = set(ases_tmp) - set(ases)
    

    as_objects = []
    for r_asn in ases:
        if Results.objects.filter(Q(as_origin=r_asn.as_origin)).count() > 0\
        and Results.objects.filter(Q(as_destination=r_asn.as_origin)).count() > 0:
            as_objects.append(r_asn.as_origin)
    
    asns = []
    for as_object in as_objects:
        if str(as_object.asn) not in asns:
            asns.append(str(as_object.asn))
    
    print asns
    print "Generating heatmap for %s ASNs" % (len(asns))
#     sys.exit(0)
    
    try:
        param = Params.objects.get(config_name='heatmap_asns')
        param.config_value = str(asns)
    except Params.DoesNotExist:
        param = Params(config_name='heatmap_asns', config_value=str(asns).encode("utf-8"))
    param.save()
        
    N = len(as_objects) ** 2
    n = 0
    
    values = []
    i = j = 0
    for asn_origin in asns:
        for asn_destination in asns:
            n = n + 1
            sys.stdout.write("\r%.1f%s" % (100 * float(n / N), '%'))
            sys.stdout.flush()
            
            rs = Results.objects.filter(Q(as_origin__asn=asn_origin) & Q(as_destination__asn=asn_destination) & Q(ave_rtt__lte=800)).values_list('ave_rtt', flat=True)
            if len(rs) > 0:
                value = "%.2f" % (sum(rs) / len(rs))
                values.append([i, j, value])
            else:
                values.append([i, j, 0])
            
#             dt = datetime.now() - t0
#             sys.stdout.write("\r%s segundos" % ((N - n) * ( 1.0 * dt.seconds / n )))
#             sys.stdout.flush()
            
            j += 1
        i += 1
        j = 0
    sys.stdout.write("\n")
    try:
        param = Params.objects.get(config_name='heatmap_asns_values')
        param.config_value = json.dumps(values)
        param.save()
    except Params.DoesNotExist:
        param = Params(config_name='heatmap_asns_values', config_value=json.dumps(values))
        param.save()
    
    
def heatmap(start, end):
    
    print "Generating heatmap for %s - %s" % (start.year, end.year)
    
    spinner = spinning_cursor()
    
    countries_iso = list(Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name').values_list('iso', flat=True))
    # get those countries that have test results
    tmp = []
    for cc in countries_iso:
        if Results.objects.filter((Q(country_origin=cc)) & (Q(date_test__gt=start) & Q(date_test__lte=end))).count() > 0\
         and Results.objects.filter((Q(country_destination=cc)) & (Q(date_test__gt=start) & Q(date_test__lte=end))).count() > 0:  # Results.objects.filter((Q(country_origin = cc) | Q(country_destination = cc)) & (Q(date_test__gt = start) & Q(date_test__lte = end))).count() > 0:
            tmp.append(cc)
    countries_iso = tmp
    
    countries = []
    for country_iso in countries_iso:
        countries.append(str(Country.objects.get(iso=country_iso).printable_name))
    try:
        param = Params.objects.get(config_name='heatmap_countries')
        param.config_value = str(countries)
        param.save()
    except Params.DoesNotExist:
        param = Params(config_name='heatmap_countries', config_value=str(countries).encode("utf-8"))
        param.save()
    
    values = []
    i = j = 0
    
    N = len(countries_iso) ** 2
    n = 0
    latencies = []
    for country_iso_origin in countries_iso:
        latency = meanLatency(country_iso_origin, country_iso_origin, start, end)
        if latency > 0: latencies.append(latency)
        
        for country_iso_destination in countries_iso:
            n = n + 1
            sys.stdout.write("\r%.1f%s" % (100 * float(n / N), '%'))
            sys.stdout.flush()
#             sys.stdout.write(spinner.next())
#             sys.stdout.flush()
#             sys.stdout.write('\b')
            
            
            
            latency = meanLatency(country_iso_origin, country_iso_destination, start, end)
            values.append([i, j, latency])
            j = j + 1
        i = i + 1
        j = 0
    print "Region mean: %s" % (str(sum(latencies) * 1.0 / len(latencies)))
    try:
        param = Params.objects.get(config_name='heatmap_values')
        param.config_value = json.dumps(values)
        param.save()
    except Params.DoesNotExist:
        param = Params(config_name='heatmap_values', config_value=json.dumps(values))
        param.save()


def build_dict(results):
    from collections import defaultdict
    from sys import stdout

    ccs = ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'PE', 'PY', 'SR', 'UY', 'VE', 'BZ', 'CR', 'CU', 'DO', 'GT', 'HN', 'MX', 'PA', 'SV', 'TT'] # Country.objects.get_region_countrycodes()
    N = len(ccs)
    region_dict = defaultdict(None)
    for i, cc_o in enumerate(ccs):
        stdout.write("\r%.2f%%" % (100.0 * i / N))
        stdout.flush()
        rs = results.filter(country_origin=cc_o)

        if len(rs) == 0:
            continue

        cc_dict = defaultdict(None)
        for cc_d in ccs:
            rtts = rs.filter(country_destination=cc_d).values_list('ave_rtt', flat=True)
            if len(rtts) > 0:
                rtt = sum(rtts) / len(rtts)
            # else:
            #     rtt = 0
                cc_dict[cc_d] = rtt
        region_dict[cc_o] = cc_dict
    return region_dict

def build_dict_as(results):
    from collections import defaultdict
    from sys import stdout

    ccs = AS.objects.all().values_list("asn", flat=True).distinct("asn")
    N = len(ccs)
    region_dict = defaultdict(None)
    for i, cc_o in enumerate(ccs):
        stdout.write("\r%.2f%%" % (100.0 * i / N))
        stdout.flush()
        rs = results.filter(as_origin=cc_o)
        print "-",

        if len(rs) == 0:
            continue

        print "/",

        cc_dict = defaultdict(None)
        print "\\",
        for cc_d in ccs:
            print ".",
            rtts = rs.filter(as_destination=cc_d).values_list('ave_rtt', flat=True)
            if len(rtts) > 0:
                rtt = sum(rtts) / len(rtts)
                print rtt
            # else:
            #     rtt = 0
                cc_dict[cc_d] = rtt
        region_dict[cc_o] = cc_dict
    return region_dict


class Command(BaseCommand):

    def handle(self, *args, **options):
        # asn_heatmap()
        # year = 2009#[2009, 2010, 2011, 2012, 2013]
        # start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
        # end = datetime.now(GMTUY())#start + timedelta(365)#
        # heatmap(start, end)

        results = Results.objects.javascript()
        dictionary = build_dict(results)
        filename = "heatmap-javascript.png"
        build_heatmap(dictionary, filename)

        results = Results.objects.applet()
        dictionary = build_dict(results)
        filename = "heatmap-applet.png"
        build_heatmap(dictionary, filename)

        results = Results.objects.probeapi()
        dictionary = build_dict(results)
        filename = "heatmap-icmp.png"
        build_heatmap(dictionary, filename)


def build_heatmap(dictionary, filename):
    import matplotlib
    from simon_project.settings import STATIC_ROOT, DEBUG
    if not DEBUG:
        matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    import numpy as np



    origins = []
    destinations = []
    for o in sorted(dictionary):
        if o not in origins: origins.append(o)
        for d in sorted(dictionary[o]):
            if d not in destinations: destinations.append(d)

            res = []
    for o in origins:
        for d in destinations:
            try:
                res.append(dictionary[o][d])
            except:
                res.append(0)

    data = np.reshape(res, (len(origins), len(destinations)))
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(data, cmap=plt.cm.Blues)


    # put the major ticks at the middle of each cell
    plt.ylim(0, len(origins))
    plt.xlim(0, len(destinations))
    ax.set_xticks(np.arange(len(destinations))+.5, minor=False)
    ax.set_yticks(np.arange(len(origins))+.5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.set_xticklabels(destinations, minor=False)
    ax.set_yticklabels(origins, minor=False)

    # plt.title("LAC region country-level latency matrix\nGenerated %s\n" % (datetime.now().strftime('%d %b %Y')))
    plt.savefig("%s/simon_app/imgs/%s" % (STATIC_ROOT, filename), transparent=True)

        
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor
