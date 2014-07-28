import matplotlib.pyplot as pyplot
import matplotlib.mlab as mlab
import numpy as np
from scipy import stats
import pylab
from scipy.stats.distributions import lognorm
from numpy import exp
from scipy.stats import norm, exponpow

carpeta = '/Users/agustin/Desktop/tcpDump/'
files = ['nicMXjsRTT', 'nicMXtcpRTT']
labels = ['JavaScript', 'TCP']
colores = ['r', 'g']
titulo = "TCP and JavaScript latency comparison"
ejeX = "Latency (ms)"
ejeY = "Occurrence (%)"

pyplot.xlabel("%s" % ejeX)
pyplot.ylabel("%s" % ejeY)
pyplot.title(titulo)

def plot(fileName, color, label):
    data = []
    f = open('%s%s' % (carpeta, file), 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        data.append(float(line))
    
    n, bins, patches = pyplot.hist(data, bins=15, range=(100, 500), normed=True, color="%c" % color, label=label, alpha=0.53, linewidth=0.3)
    
    # normal fitting
    (mu, sigma) = norm.fit(data)
    pdf_norm = mlab.normpdf( bins, mu, sigma)
    pyplot.plot(bins, pdf_norm, "%c--" % color, linewidth=1, label=None)
    
    # lognormal fitting
    shape, loc, scale = stats.lognorm.fit(data, floc=0)
    mu = np.log(scale) # Mean of log(X)
    sigma = shape # Standard deviation of log(X)
    M = np.exp(mu) # Geometric mean == median
    s = np.exp(sigma) # Geometric standard deviation
    x = np.linspace(100, 500)
    pdf_lognorm = stats.lognorm.pdf(x, shape, loc=0, scale=scale)
    pyplot.plot(x, pdf_lognorm, "%c" % color, linewidth=1, label=None) # Plot fitted curve
    
    pyplot.vlines(mu, 0, pdf_norm.max(), linestyle='-', label=None)
    pyplot.vlines(M, 0, pdf_lognorm.max(), linestyle=':', label=None)
    ax = pyplot.gca() # Get axis handle for text positioning
    ax.text(M, pdf_norm.max(), u"%s\nmedian=%.2f ms\n%i samples" % (fileName, M, len(data)), style='italic', color=color, size='small')
    pyplot.legend()
    pylab.savefig("%s%s" % (carpeta, 'img.png'))


i = 0
for file in files:
    plot(file, colores[i], labels[i])
    i = i + 1

# pyplot.show()


# n, bins, patches = pylab.hist(  datas,
#                                 35,
#                                 normed=True,
#                                 color=["crimson", "burlywood"],
#                                 label=["Crimson", "Burlywood"],
#                                 alpha=0.7,
#                                 histtype='bar')
# 
# pylab.show()