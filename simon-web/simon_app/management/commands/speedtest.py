from django.core.management.base import BaseCommand

from simon_app.mailing import send_mail_new_points_found
from simon_app.models import *
from time import gmtime, strftime
from urlparse import urlparse
from netaddr import IPAddress, IPNetwork, AddrFormatError
import socket
import simon_project.settings as settings
from urllib2 import urlopen
from lxml import etree


class Command(BaseCommand):
    def handle(self, *args, **options):
        from sys import stdout
        from simon_app.reportes import GMTUY

        ccs = [c.iso for c in Country.objects.get_region_countries()]
        tz = GMTUY()

        # Read the XML XMLfile
        print "Fetching XML file..."
        XMLfile = urlopen('http://c.speedtest.net/speedtest-servers.php')
        data = XMLfile.read()
        XMLfile.close()
        timeFormat = "%Y-%m-%d %H:%M:%S"


        #Add new registers in the Test Points table
        print "Parsing XML file..."
        servers = etree.fromstring(str(data))[0]
        N = len(servers)
        nuevos = []
        for i, server in enumerate(servers):
            stdout.write("\r%.2f%%" % (100.0 * i / N))
            stdout.flush()

            #Get the IP address and match it against LACNIC resources
            long_url = server.get('url')
            url = urlparse(long_url)[1]
            # 		print str(long_url)

            country = server.get('cc').upper()
            city = server.get('name')
            latitude = server.get('lat')
            longitude = server.get('lon')
            description = server.get('sponsor')
            testtype = 'tcp_web'
            enabled = True
            date_created = strftime(timeFormat, gmtime())

            try:
                #could be done with DNSpython
                ok = False

                if country not in ccs:
                    continue

                for ip_address in socket.getaddrinfo(url, 80, 0, 0, socket.SOL_TCP):
                    ip_address = IPAddress(ip_address[4][0])

                    try:
                        TestPoint.objects.get(ip_address=str(ip_address))
                    except TestPoint.DoesNotExist:
                        # Si es nuevo...

                        if ip_address.version == 4:
                            for resource in settings.v4resources:
                                if ip_address in IPNetwork(resource):
                                    ok = True
                                    break
                        elif ip_address.version == 6:
                            for resource in settings.v6resources:
                                if ip_address in IPNetwork(resource):
                                    ok = True
                                    break
                        if ok is True:
                            tp = SpeedtestTestPoint(
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

                            tp.save()
                            nuevos.append(tp)

            except AddrFormatError:
                print 'Address Format Error'
                pass
            except socket.gaierror:
                print "No address associated with hostname"
                pass

        if len(nuevos) > 0:
            print "The following Test Points have been added:"
            for tp in nuevos:
                print str(tp.ip_address)
            send_mail_new_points_found(ctx={'points':nuevos})