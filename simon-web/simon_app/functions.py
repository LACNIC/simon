'''
Created on 12/11/2012

@author: agustinf
'''
import math
import simon_project.settings as settings
from netaddr import IPAddress, IPNetwork, AddrFormatError
import json as json
import urllib2
from urllib2 import URLError
from django.db.models import Q
from simon_app.models import Results


def whoIs(address):
    # host = 'restwhois.labs.lacnic.net'
    # target = '/restfulwhois/ip/%s' % str(address)
    host = 'rdap.labs.lacnic.net'
    target = '/rdap/ip/%s?apikey=9A6BD512F0DB58C7A87502ACDC053707' % str(address)
    headers = {
        "Accept": "application/json"
    }
    try:
        req = urllib2.Request(('http://%s%s' % (host, target)), None, headers)
        response = urllib2.urlopen(req, timeout=10)
        data = response.read()
        json_data = json.loads(data)
        return json_data
    except URLError:
        print 'Error while getting whois information for %s' % address


def bps2KMG(bps):
    #    Converts throughput numerical rates to human friendly rates
    K = 1000
    M = K * K
    G = K * M
    T = K * G

    if bps > T:
        return format((bps / T), '.2f') + ' Tbps'
    if bps > G:
        return format((bps / G), '.2f') + ' Gbps'
    if bps > M:
        return format((bps / M), '.2f') + ' Mbps'
    if bps > K:
        return format((bps / K), '.2f') + ' Kbps'


def KMG2bps(KMG):
    # KMG must be a string ending in Xbps. Otherwise returns its input. Example '1 Mbps'
    K = 1000
    M = K * K
    G = K * M
    T = K * G

    number = int(KMG[:-4])

    if KMG.find('Tbps') != -1:
        return number * T
    elif KMG.find('Gbps') != -1:
        return number * G
    elif KMG.find('Mbps') != -1:
        return number * M
    elif KMG.find('Kbps') != -1:
        return number * K
    else:
        print 'Failed to convert %s to bps' % KMG

    return KMG  # failed


def networkInLACNICResources(network):
    try:
        for resource in settings.v4resources:
            if IPNetwork(network) in IPNetwork(resource):
                return True

        for resource in settings.v6resources:
            if IPNetwork(network) in IPNetwork(resource):
                return True

    except AddrFormatError:
        print 'Error en el formato de la direccion'

    return False


def inLACNICResources(ip_address):
    try:
        for resource in settings.v4resources:
            if IPAddress(ip_address) in IPNetwork(resource):
                return True

        for resource in settings.v6resources:
            if IPAddress(ip_address) in IPNetwork(resource):
                return True

    except AddrFormatError:
        print 'Error en el formato de la direccion'

    return False


def partOfLACNICResources(network):
    try:
        for resource in settings.v4resources:
            if IPNetwork(network) in IPNetwork(resource):
                return True

        for resource in settings.v6resources:
            if IPNetwork(network) in IPNetwork(resource):
                return True

    except AddrFormatError:
        print 'Error en el formato de la direccion'

    return False


def LACNICResourcesIsPartOf(bigger_network):
    try:
        for resource in settings.v4resources:
            if IPNetwork(resource) in IPNetwork(bigger_network):
                return True

        for resource in settings.v6resources:
            if IPNetwork(resource) in IPNetwork(bigger_network):
                return True

    except AddrFormatError:
        print 'Error en el formato de la direccion'

    return False


def distance_on_unit_sphere(lat1, long1, lat2, long2):
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi / 180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians

    # theta = longitude
    theta1 = long1 * degrees_to_radians
    theta2 = long2 * degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc


def mean_latency(originIso, destinationIso, date_start, date_end):
    results = Results.objects.filter(
        Q(country_origin=originIso) & Q(country_destination=destinationIso) & Q(date_test__gt=date_start) & Q(
            date_test__lte=date_end) & (Q(ave_rtt__lte=800))).values_list('ave_rtt', flat=True)
    if len(results) == 0: return 0
    try:
        return sum(results) / len(results)
    except TypeError:
        return 0
