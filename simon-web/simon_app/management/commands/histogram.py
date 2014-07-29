from django.core.management.base import BaseCommand
import matplotlib.pyplot as pyplot
from numpy import math
from django.db.models import Q
from datetime import datetime, timedelta, date
from simon_app.reportes import GMTUY
from simon_app.models import Results, Country

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        DESDE = 10
        HASTA = 1000
        
        if len(args) == 0:
            print "Use: histogram <year>|historical country|region [CC] [CC]"
            return
        
        if "historical" in args:
            year = 2009
            start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
            end = datetime.now().replace(tzinfo=GMTUY())
        else:
            year = args[0]
            start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
            
            if int(datetime.now().year) == int(year):
                end = datetime.now().replace(tzinfo=GMTUY())
            else:
                end = datetime.strptime("Dec 31 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
        
        if "country" in args:
            self.histogram_countries(args[2], args[3], DESDE, HASTA, start, end, "Latency histogram between %s and %s, %s-%s" % (args[2], args[3], start.year, end.year))
        
        elif "region" in args:
            self.histogram_region(DESDE, HASTA, start, end, "Region latency histogram, %s-%s" % (start.year, end.year))
    
    def histogram(self, data, titulo):
        pyplot.hist(data, bins = math.sqrt(len(data)), normed = True, linewidth=0.0)
        pyplot.title(titulo)
        pyplot.show()
    
    def histogram_region(self, DESDE, HASTA, start, end, title):
        
        years = range(int(start.year), int(end.year) + 1)
        data_years = []
        legends = []
        for year in years:
            start = datetime.strptime("Jan 1 %s" % (year), '%b %d %Y').replace(tzinfo=GMTUY())
            end = start + timedelta(365)
            data = Results.objects.filter(Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))\
                                       ).values_list('ave_rtt', flat=True)
            legends.append("%s - %s samples" % (year, len(data)))
            data_years.append(data)
            pyplot.hist(data, bins = math.sqrt(len(data)), normed = True, linewidth=0.4, stacked=True, alpha=0.30)
        
        pyplot.legend(legends)
        pyplot.title(title)
        pyplot.savefig("/Users/agustin/Desktop/%s" % title, transparent=True)
#         pyplot.show()
        
    def histogram_countries(self, cc1, cc2, DESDE, HASTA, start, end, title):
        country_1 = Country.objects.get(iso = cc1)
        country_2 = Country.objects.get(iso = cc2)
        data = Results.objects.filter((Q(country_origin=country_1.iso) & Q(country_destination=country_2.iso)\
                                       | Q(country_origin=country_2.iso) & Q(country_destination=country_1.iso))\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        self.histogram(data, title)