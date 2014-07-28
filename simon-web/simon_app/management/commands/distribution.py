from django.core.management.base import BaseCommand
from simon_app.models import Results
import simon_project.settings as settings
from django.db.models import Q

"""
    Command that generates the Region Distribution Chart
"""

class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open('%s/data/region.tsv' % settings.STATIC_ROOT, 'w')
        f.write("date\tIP v4\tIP v6\n")
        results = Results.objects.all()
        maximum = 500  # results[n-1]
        categories = 20
        for i in range(1, categories):
            category_max = i * maximum / float(categories)
            category_min = (i - 1) * maximum / float(categories)
            categroy_results = results.filter(Q(ave_rtt__gte=category_min) & Q(ave_rtt__lt=category_max))
            f.write(str((category_min + category_max) / 2.0))
             
            for v in [4, 6]:
                n = len(results.filter(ip_version=v))
                m = len(categroy_results.filter(ip_version=v).values_list('ave_rtt', flat=True).order_by('ave_rtt'))
                if n != 0:
                    valor = (100 * (m / float(n)))
                else:
                    valor = 0
                f.write("\t" + str(float("%0.2f" % valor)))
             
            f.write("\n")
        f.close()
        
#         from scipy import stats
#         from datetime import datetime, timedelta
#         from simon_app.reportes import GMTUY
#         import matplotlib.pyplot as pyplot
#         import matplotlib.mlab as mlab
#         import pylab
#         import numpy as np
#         import math
#         
#         i = 0
#         alpha = 0.20
#         c = ['b', 'r', 'y', 'g', 'm', 'c']
#         for y in [2009, 2010, 2011, 2012, 2013, 2014]:
#             start = datetime.strptime("Jan 1 %s" % (y), '%b %d %Y')#datetime.now(GMTUY()) - timedelta(365)
#             end = datetime.strptime("Dec 31 %s" % (y + 1), '%b %d %Y')#datetime.now(GMTUY())#datetime.strptime("Jan 1 %s" % (2012), '%b %d %Y')#
#             if y == 2014:
#                 end = datetime.now(GMTUY())
#             
#             data = Results.objects.filter(Q(date_test__gt = start) & Q(date_test__lte = end)).values_list('ave_rtt', flat=True)
#             range = (min(data),max(data))
#             bins = math.sqrt(len(data))
#             n, bins, patches = pyplot.hist(data, bins=bins, range=range, normed=True, color="%c" % c[i], alpha=1, linewidth=0.3, label=str(y))
#             
#             (mu, sigma) = stats.norm.fit(data)
#             pdf_norm = mlab.normpdf( bins, mu, sigma)
#             pyplot.plot(bins, pdf_norm, "%c" % c[i], alpha=0, linewidth=1, label=None)
#             
#             shape, loc, scale = stats.lognorm.fit(data, floc=0)
#             mu = np.log(scale) # Mean of log(X)
#             sigma = shape # Standard deviation of log(X)
#             M = np.exp(mu) # Geometric mean == median
#             s = np.exp(sigma) # Geometric standard deviation
#             x = np.linspace(range[0], range[1])
#             pdf_lognorm = stats.lognorm.pdf(x, shape, loc=0, scale=scale)
#             pyplot.plot(x, pdf_lognorm, "%c" % c[i], alpha=0, linewidth=1, label=None) # Plot fitted curve
#                 
#             i = i + 1
        
        # v4 vs v6
#         i = 0
#         for v in [4]:
#             data = Results.objects.filter(Q(ip_version = v)).values_list('ave_rtt', flat=True)
#             range = (min(data),max(data))
#             bins = math.sqrt(len(data))
#             n, bins, patches = pyplot.hist(data, bins=bins, range=range, normed=True, color='b', alpha=0.5, linewidth=0.3, label="IPv%c" % v)
#             (mu, sigma) = stats.norm.fit(data)
#             pdf_norm = mlab.normpdf( bins, mu, sigma)
#             pyplot.plot(bins, pdf_norm, c[i], alpha=1, linewidth=0.5, label=str(y))
#             i = i + 1
#         pyplot.legend()
#         pyplot.show()
#         pylab.savefig("%s%s" % ('/Users/agustin/Desktop/', 'normal.png'))
    