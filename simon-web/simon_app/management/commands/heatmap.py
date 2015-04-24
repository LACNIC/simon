from __future__ import division
"""
    Script than saves the Heatmap data into static/data/heatmap
"""
from django.core.management.base import BaseCommand
from simon_app.models import Country, Params
from django.db.models import Q
from simon_app.functions import meanLatency
from simon_app.models import Results, AS
from simon_app.reportes import GMTUY
from datetime import timedelta, datetime
import json
import sys

def asn_heatmap():
    rs = Results.objects.filter((Q(as_origin__gt=1) | Q(as_destination__gt=1)))# & Q(ip_version=4))
    ases = rs.order_by('as_origin').distinct('as_origin')
    ases_tmp = rs.order_by('as_destination').distinct('as_destination')
    ases = set(ases_tmp) - set(ases)
    
#     mean = []
#     for asn in ases:
#         if Results.objects.filter(Q(as_origin=asn.as_origin) & Q(as_destination=asn.as_origin)).count() > 0:
#             rs = Results.objects.filter(Q(as_origin=asn.as_origin) & Q(as_destination=asn.as_origin) & Q(ave_rtt__lte=800)).values_list('ave_rtt', flat=True)
#             print "AS %s\t%.1f ms (%s samples)" % (asn.as_origin.asn, sum(rs) / len(rs), len(rs))
#             mean.append(sum(rs) / len(rs))
#     print "------------------------\nRegion average : %s ms" % (sum(mean) / len(mean))
    
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

class Command(BaseCommand):

    def handle(self, *args, **options):
        # asn_heatmap()
        year = 2009#[2009, 2010, 2011, 2012, 2013]
        start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
        end = datetime.now(GMTUY())#start + timedelta(365)#
        heatmap(start, end)
        
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor
