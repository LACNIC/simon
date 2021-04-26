from cookielib import CookieJar

from django.core.management.base import BaseCommand

from simon_app.mailing import send_mail_new_points_found
from simon_app.models import *
from time import gmtime, strftime
from urlparse import urlparse
from netaddr import IPAddress, IPNetwork, AddrFormatError
import socket
import simon_project.settings as settings
from urllib2 import urlopen, build_opener, HTTPCookieProcessor
from lxml import etree
import logging
from simon_app.functions import GMTUY
from simon_app.decorators import timed_command, mem_comsumption
from tqdm import tqdm
import multiprocessing
# We must import this explicitly, it is not imported by the top-level
# multiprocessing module.
from simon_project.settings import DEBUG
import multiprocessing.pool
from multiprocessing import Pool, TimeoutError, Process
from datetime import datetime
import requests
import signal
from dns import query, rdatatype, rdataclass, message, name
from tqdm import tqdm


tz = GMTUY()
HTTPS_POOL_SIZE = 50  # simultaneous checks through the network

# Register None for timeouts
signal.signal(signal.SIGALRM, lambda _, __: None)


class NoDaemonProcess(Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


class Command(BaseCommand):

    command = "Fetching speedtest points"

    @timed_command(name=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        ccs_lacnic = [c.iso for c in Country.objects.get_lacnic_countries()]
        ccs_afrinic = [c.iso for c in Country.objects.get_afrinic_countries()]
        ccs_apnic = [c.iso for c in Country.objects.get_apnic_countries()]
        ccs_ripencc = Country.objects.get_ripencc_countrycodes()

        # Read the XML file
        logging.info("Fetching XML file...")
        url = "http://www.speedtest.net/speedtest-servers.php"

        data = requests.get(url, allow_redirects=True).text

        logging.info("Parsing XML file...")
        xml_ = etree.fromstring(data.encode('utf-8'))
        servers = xml_[0]

        # lxmlib can't be pickled in this version, we'll need to perform xml
        # operations first, then parallelize
        tps_to_check = []
        for tp in tqdm([xml_to_dict(s) for s in servers], desc="Performing address lookups (A)"):
            tps_to_check.append(b(tp))

        tps_checked = []
        for tp in tqdm(filter(None, tps_to_check), desc="Checking for new points"):
            for _tp in a(tp):
                tps_checked.append(_tp)
        # tps_to_check = [a(tp) for tp in tps_to_check if tp is not None]  # now they're TPs

        tps_checked_2 = []
        for tp in tqdm(filter(None, tps_checked)):
            tps_checked_2.append(perform_https_check(tp))
        # res = [perform_https_check(tp) for tp in tps_to_check if tp is not None]
        nuevos = filter(None, tps_checked_2)

        if nuevos:
            logging.info("The following Test Points have been added (%.0f):" % (len(nuevos)))
            for tp in nuevos:
                logging.info(str(tp.ip_address))
            # send_mail_new_points_found(ctx={'points': nuevos})


def xml_to_dict(server):

    res = {}
    for attr in ['url', 'cc', 'name', 'lat', 'lon', 'sponsor']:

        if attr not in server.keys():
            continue

        res.update({
            attr: server.get(attr)
        })
    return res


def b(server):
    long_url = server.get('url')
    url = urlparse(long_url)[1].split(':')[0]

    qname = name.from_text(url)
    q = message.make_query(qname, rdatatype.A)  # TODO AAAA
    r = query.udp(q, '8.8.8.8' if DEBUG else '200.7.84.14')
    try:
        rrset = r.find_rrset(r.answer, qname, rdataclass.IN, rdatatype.A)
        server['addresses'] = [rr.address for rr in rrset]
    except KeyError as e:
        # No RRset
        return None
    return server

    # try:
    #     return Pool(processes=1).apply_async(a, [server]).get(timeout=timeout)
    # except TimeoutError as e:
    #     logging.warn(e)
    # except socket.error as e:
    #     logging.warn(e)


def a(server):

    if server is None:
        return None

    print '.',

    # Get the IP address
    long_url = server.get('url')
    url = urlparse(long_url)[1].split(':')[0]

    country = server.get('cc').upper()
    city = server.get('name')
    latitude = server.get('lat')
    longitude = server.get('lon')
    description = server.get('sponsor')
    testtype = 'tcp_web'
    enabled = True
    date_created = datetime.now(tz=tz)

    # if country not in ccs_lacnic and country not in ccs_afrinic and country not in ccs_apnic and country not in ccs_ripencc:
    #     continue

    # try:
    #     addresses = socket.getaddrinfo(url.split(':')[0], 80, 0, 0, socket.SOL_TCP)
    # except socket.gaierror:
    #     logging.warn("No address associated with hostname {hostname}".format(hostname=url))
    #     return None

    res = []
    for ip_address in server.get('addresses'):

        (object, created) = SpeedtestTestPoint.objects.update_or_create(
            description=description,
            testtype=testtype,
            ip_address=str(ip_address),
            country=country,
            enabled=enabled,
            date_created=date_created,
            url=long_url,
            speedtest_url=long_url,
            city=city,
            latitude=latitude,
            longitude=longitude
        )

        if created:
            res.append(object)

    return res

        # TODO check if not in settinvg.v6resources


def perform_https_check(tp):

    if tp is None:
        return None

    protocol = "https"

    https_check = HttpsCheck.objects.create(
        date=datetime.now(tz=tz),
        test_point=tp,
        status=tp.make_request(protocol=protocol)
    )
    tp.httpscheck_set.add(https_check)

    if https_check.status:
        return tp
