from __future__ import division

"""
    Script than saves the Heatmap data into static/data/heatmap
"""
from django.core.management.base import BaseCommand
from simon_app.models import Country, Params
from django.db.models import Q
from simon_app.models import Results, AS
import json, sys
from simon_app.decorators import chatty_command


def heatmap(start, end):
    print "Generating heatmap for %s - %s" % (start.year, end.year)

    spinner = spinning_cursor()

    countries_iso = list(
        Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name').values_list(
            'iso', flat=True))
    # get those countries that have test results
    tmp = []
    for cc in countries_iso:
        if Results.objects.filter((Q(country_origin=cc)) & (Q(date_test__gt=start) & Q(date_test__lte=end))).count() > 0 \
                and Results.objects.filter((Q(country_destination=cc)) & (Q(date_test__gt=start) & Q(
                    date_test__lte=end))).count() > 0:  # Results.objects.filter((Q(country_origin = cc) | Q(country_destination = cc)) & (Q(date_test__gt = start) & Q(date_test__lte = end))).count() > 0:
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


def build_dict(results, ccs=Country.objects.get_lacnic_countrycodes()):
    from collections import defaultdict
    from sys import stdout

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
            rtts = rs.filter(country_destination=cc_d).values_list('min_rtt', flat=True)
            if len(rtts) > 0:
                rtt = sum(rtts) / len(rtts)
                # else:
                #     rtt = 0
                cc_dict[cc_d] = rtt
        region_dict[cc_o] = cc_dict
    return region_dict


def build_dict_as(matrix):
    from collections import defaultdict

    region_dict = defaultdict(None)
    for m in matrix:
        as_origin = str(m[0])
        as_destination = str(m[1])
        n = int(m[5])
        min_rtt = int(m[4])
        if n == 0 or min_rtt <= 0:
            continue

        as_dict = defaultdict(None)
        as_dict[as_destination] = min_rtt
        region_dict[as_origin] = as_dict
    return region_dict


class Command(BaseCommand):
    @chatty_command(command="Building the heatmap")
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


def build_heatmap(dictionary, filename, plot_text=True):
    import matplotlib
    from simon_project.settings import STATIC_ROOT, DEBUG
    if not DEBUG:
        matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    import numpy as np

    origins = []
    destinations = []
    n = 0
    for o in sorted(dictionary):
        if o not in origins:
            origins.append(o)
        for d in sorted(dictionary[o]):
            if d not in destinations:
                destinations.append(d)

            res = []

        n += 1
        sys.stdout.write("\r Preparing Data (1/3) %.1f%%" % (100 * float(n / len(dictionary))))
        sys.stdout.flush()
    print ""

    # def cluster_sort(key):
    #     d = {'DO': 0, 'GT': 1, 'CO': 0, 'VE': 1, 'CL': 2, 'BO': 2, 'EC': 0, 'AR': 3, 'HN': 0, 'BR': 3, 'CR': 0, 'CU': 0,
    #          'UY': 3, 'SR': 0, 'TT': 0, 'PY': 3, 'SV': 1, 'PA': 1, 'BZ': 0, 'PE': 2, 'MX': 1}
    #     return d[key]
    #
    # origins = sorted(origins, key=cluster_sort)
    # destinations = sorted(destinations, key=cluster_sort)

    n = 0
    N = len(origins) * len(destinations)
    for o in origins:
        for d in destinations:
            try:
                res.append(dictionary[o][d])
            except:
                res.append(0)
            finally:
                n += 1
                sys.stdout.write("\r Preparing Data (2/3) %.1f%%" % (100 * float(n / N)))
                sys.stdout.flush()
    print ""
    print "Painting matrix (3/3)"

    data = np.reshape(res, (len(origins), len(destinations)))
    fig, ax = plt.subplots()

    heatmap = ax.pcolor(data, cmap=plt.cm.Blues)

    if plot_text:
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                plt.text(x + 0.5, y + 0.5, "%.0f" % data[y, x],
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=8
                         )

    # put the major ticks at the middle of each cell
    plt.ylim(0, len(origins))
    plt.xlim(0, len(destinations))
    ax.set_xticks(np.arange(len(destinations)) + .5, minor=False)
    ax.set_yticks(np.arange(len(origins)) + .5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.set_xticklabels(destinations, minor=False)
    ax.set_yticklabels(origins, minor=False)

    # ax_ = plt.gca()
    # x, y, z = ax_.get_children()[2]
    # plt.colorbar(z, ax=ax_)
    plt.colorbar(heatmap)
    plt.show()

    # plt.savefig("%s/simon_app/imgs/%s" % (STATIC_ROOT, filename), transparent=True)


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor
