from __future__ import print_function
from builtins import range
from django.core.management.base import BaseCommand
import matplotlib.pyplot as pyplot
from numpy import math
from django.db.models import Q, Count
from datetime import datetime, timedelta, date
from simon_project import *
from simon_app.functions import GMTUY
from simon_app.models import Results, Country

class Command(BaseCommand):
    
    def use(self):
        print("Use: histogram <year>|historical country|region [<CC>] [<CC>] | all")
        
#     def add_arguments(self, parser):
#         parser.add_argument('-H', '--historical')
#         parser.add_argument('region')
#         parser.add_argument('country', nargs=2, metavar='CC')
#         parser.add_argument('all')
    
    def handle(self, *args, **options):
        
        DESDE = 10
        HASTA = 800
        
        if len(args) == 0:
            self.use()
            return
        
        if "as" in args:
            self.histogram_as()
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
                        title = "Latency histogram between %s and %s, %s-%s" % (origin.iso, destination.iso, start.year, end.year)
                        filename = "countries/%s-%s %s-%s" % (origin.iso, destination.iso, start.year, end.year)
                        print("%s : %s" % (title, filename))
                        self.histogram_countries(origin.iso, destination.iso, DESDE, HASTA, start, end, title, filename)
                return
            
            else:
                origin = Country.objects.get(iso=args[2])
                destination = Country.objects.get(iso=args[3])
                title = "Latency histogram between %s and %s, %s-%s" % (origin.iso, destination.iso, start.year, end.year)
                filename = "countries/%s-%s %s-%s" % (origin.iso, destination.iso, start.year, end.year)
                self.histogram_countries(origin.iso, destination.iso, DESDE, HASTA, start, end, title, filename)
                return
        
        elif "region" in args:
            self.histogram_region(DESDE, HASTA, start, end, "Region latency histogram, %s-%s" % (start.year, end.year))
            return
            
        elif "ipv6" in args:
            self.histogram_ip(DESDE, HASTA, start, end, 6, "IPv6 stats")
            return
        
        elif "ipv4" in args:
            self.histogram_ip(DESDE, HASTA, start, end, 4, "IPv4 stats")
            return
        
        elif "ipvs" in args:
            self.histogram_ipvs(DESDE, HASTA, start, end, "IPv4 vs. IPv6 stats")
            return
    
    def histogram(self, data, titulo, filename, legend=""):
        if len(data) == 0:
            return
        
        pyplot.hist(data, bins = math.sqrt(len(data)), normed = True, linewidth=0.4)
        pyplot.title(titulo)
        pyplot.legend([legend])
        now = datetime.now().strftime("Last updated %d %b %Y")
        pyplot.text(1.0, -0.05, now, verticalalignment='top', horizontalalignment='right', transform=pyplot.axes().transAxes, color='gray', fontsize=9)
        pyplot.savefig("%s/histograms/%s" % (settings.STATIC_ROOT, filename), transparent=True)
        pyplot.clf()
        pyplot.show()
    
    def histogram_region(self, DESDE, HASTA, start, end, title):
        
        years = list(range(int(start.year), int(end.year) + 1))
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
        now = datetime.now().strftime("Last updated %d %b %Y")
        pyplot.text(1.0, -0.05, now, verticalalignment='top', horizontalalignment='right', transform=pyplot.axes().transAxes, color='gray', fontsize=9)
        pyplot.savefig("%s/histograms/region/%s" % (settings.STATIC_ROOT, title), transparent=True)
#         pyplot.show()
        
    def histogram_countries(self, cc1, cc2, DESDE, HASTA, start, end, title, filename):
        country_1 = Country.objects.get(iso = cc1)
        country_2 = Country.objects.get(iso = cc2)
        data = Results.objects.filter((Q(country_origin=country_1.iso) & Q(country_destination=country_2.iso)\
                                       | Q(country_origin=country_2.iso) & Q(country_destination=country_1.iso))\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        if len(data) > 0:
            legend = "%s samples" % (len(data))
            self.histogram(data, title, filename, legend)
        
    def histogram_ip(self, DESDE, HASTA, start, end, ipversion, title):
        data = Results.objects.filter(Q(ip_version=ipversion)\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        self.histogram(data, title, "ipv%s" % ipversion, "Estadisticas de IPv%s" % ipversion)
        
    def histogram_ipvs(self, DESDE, HASTA, start, end, title):
        data4 = Results.objects.filter(Q(ip_version=4)\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        data6 = Results.objects.filter(Q(ip_version=6)\
                                      & Q(ave_rtt__gt=DESDE) & Q(ave_rtt__lte=HASTA)\
                                       & (Q(date_test__gt=start) & Q(date_test__lte=end))).values_list('ave_rtt', flat=True)
        
        pyplot.hist([data4, data6], bins = math.sqrt(min(len(data4), len(data6))), normed = True, linewidth=0.4)
        pyplot.title(title)
        pyplot.legend(["IPv4 (%s samples)" % len(data4), "IPv6 (%s samples)" % len(data6)])
        now = datetime.now().strftime("Last updated %d %b %Y")
        pyplot.text(1.0, -0.05, now, verticalalignment='top', horizontalalignment='right', transform=pyplot.axes().transAxes, color='gray', fontsize=9)
        pyplot.savefig("%s/histograms/%s" % (settings.STATIC_ROOT, "ipv4v6"), transparent=True)                            
        
    def histogram_as(self):
        from simon_app.models import AS
        legends = []
        
        rs = Results.objects.filter((Q(country_origin='UY') & Q(country_destination='AR')) | (Q(country_origin='AR') & Q(country_destination='UY')))\
                                   .distinct('as_origin')
        rs_total = Results.objects.filter((Q(country_origin='UY') & Q(country_destination='AR')) | (Q(country_origin='AR') & Q(country_destination='UY'))\
                                          & Q(ave_rtt__lte=700)\
                                          ).values_list('ave_rtt', flat=True)
        N = len(rs_total)
        legends.append('Total')
        pyplot.hist(rs_total, normed = True)
        
        
        asns = []
        for r in rs: asns.append(r.as_origin)
        
        for asn in asns:#AS.objects.filter(asn=28000):
            data = Results.objects.filter(Q(as_origin=asn.id) & Q(as_destination__gt=4) & Q(ave_rtt__lte=700))
            
            asns_destination = []
            for r in data.distinct('as_destination'): asns_destination.append(r.as_destination)
            
            for asn_destination in asns_destination:
                data_dest = data.filter(Q(as_destination=asn_destination.id)).values_list('ave_rtt', flat=True)
                n = len(data_dest)
                if n < 100: continue#0.01 * N: continue
                pyplot.hist(data_dest, bins = math.sqrt(len(data_dest)), normed = True, linewidth=0.0, stacked=True, alpha=0.30)
                legends.append("ASN %s --> ASN %s (%.2f%s)" % (asn.asn, asn_destination.asn, 100.0 * n / N, '%'))
                
        pyplot.legend(legends)
        pyplot.show()
#         data = Results.objects.filter(Q(as_origin__gt=1))