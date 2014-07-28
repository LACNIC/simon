"""
    Script than saves the Heatmap data into static/data/heatmap
"""
from django.core.management.base import BaseCommand
from simon_app.models import Country, Params
from django.db.models import Q
from simon_app.functions import meanLatency
from simon_app.models import Results
from simon_app.reportes import GMTUY
from datetime import timedelta

def heatmap(start, end):
    
    print "Generating heatmap for %s - %s" % (start.year, end.year)
    
    import sys
    spinner = spinning_cursor()
    
    countries_iso = list(Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name').values_list('iso', flat=True))
    # get those countries that have test results
    tmp = []
    for cc in countries_iso:
        if Results.objects.filter((Q(country_origin=cc)) & (Q(date_test__gt=start) & Q(date_test__lte=end))).count() > 0\
         and Results.objects.filter((Q(country_destination=cc)) & (Q(date_test__gt=start) & Q(date_test__lte=end))).count() > 0:  # Results.objects.filter((Q(country_origin = cc) | Q(country_destination = cc)) & (Q(date_test__gt = start) & Q(date_test__lte = end))).count() > 0:
            tmp.append(cc)
    countries_iso = tmp
    
    import json
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
    
    latencies = []
    for country_iso_origin in countries_iso:
        latency = meanLatency(country_iso_origin, country_iso_origin, start, end)
        if latency > 0: latencies.append(latency)
        
        for country_iso_destination in countries_iso:
            sys.stdout.write(spinner.next())
            sys.stdout.flush()
            sys.stdout.write('\b')
            
            
            
            latency = meanLatency(country_iso_origin, country_iso_destination, start, end)
            values.append([i, j, latency])
            j = j + 1
        i = i + 1
        j = 0
    print latencies
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
        year = [2009, 2010, 2011, 2012, 2013]
        from datetime import datetime
        start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
        end = datetime.now(GMTUY())#start + timedelta(365) # # 
        heatmap(start, end)
        
def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor
