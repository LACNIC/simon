from django.core.management.base import BaseCommand
import matplotlib.pyplot as pyplot
from numpy import math
from django.db.models import Q
from datetime import datetime, timedelta, date
from simon_project import *
from simon_app.reportes import GMTUY
from simon_app.models import Results, Country

class Command(BaseCommand):
    
    def use(self):
        print "Use: histogram <year>|historical country|region [<CC>] [<CC>]"
    
    def handle(self, *args, **options):
        
        DESDE = 10
        HASTA = 1000
        
        if len(args) == 0:
            self.use()
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
            if "all" in args:
                countries = Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3))
                i = 0
                for country in countries:
                    i = i + 1
                    origin = country
                    destinations = countries[i:]
                    for destination in destinations:
                        self.histogram_countries(origin.iso, destination.iso, DESDE, HASTA, start, end, "Latency histogram between %s and %s, %s-%s" % (origin.iso, destination.iso, start.year, end.year), "countries/%s-%s %s-%s" % (origin.iso, destination.iso, start.year, end.year))
                return
                    
            self.histogram_countries(args[2], args[3], DESDE, HASTA, start, end, "Latency histogram between %s and %s, %s-%s" % (args[2], args[3], start.year, end.year), "%s-%s %s-%s" % (args[2], args[3], start.year, end.year))
        
        elif "region" in args:
            self.histogram_region(DESDE, HASTA, start, end, "Region latency histogram, %s-%s" % (start.year, end.year))
    
    def histogram(self, data, titulo, filename, legend=''):
        if len(data) == 0:
            return
        pyplot.hist(data, bins = math.sqrt(len(data)), normed = True, linewidth=0.4)
        pyplot.title(titulo)
        pyplot.savefig("%s/histograms/%s" % (settings.STATIC_ROOT, filename), transparent=True)
        pyplot.clf()
#         pyplot.show()
    
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
            pyplot.hist(data, bins = math.sqrt(len(data)), normed = True, linewidth=0.4, stacked=True, alpha=0.70)
        
        pyplot.legend(legends)
        pyplot.title(title)
        pyplot.savefig("%s/histograms/region/%s" % (settings.STATIC_ROOT, title), transparent=True)
#         pyplot.show()
        
    def histogram_countries(self, cc1, cc2, DESDE, HASTA, start, end, title, filename):
        country_1 = Country.objects.get(iso = cc1)
        country_2 = Country.objects.get(iso = cc2)
        data = Results.objects.filter((Q(country_origin=country_1.iso) & Q(country_destination=country_2.iso)\
                                       | Q(country_origin=country_2.iso) & Q(country_destination=country_1.iso))\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        legend = "%s - %s, %s samples" % (cc1, cc2, len(data))
        self.histogram(data, title, filename, legend)