from future import standard_library
standard_library.install_aliases()
from django.core.management.base import BaseCommand
from simon_app.models import *
from django.db.models import Q
from sys import stdout
from simon_app.functions import networkInLACNICResources
from simon_project import settings
import zlib, urllib.request, urllib.error, urllib.parse
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Command that updates Results table with most recent ASN information

        :param args:
        :param options:
        :return:
        """

        rs = Results.objects.exclude(ip_origin=None).exclude(ip_destination=None).filter(Q(as_origin=None) | Q(as_destination=None))
        N = len(rs)
        i = 0
        for r in rs:
            stdout.write("\r%.2f%%" % (100.0 * i / N))
            i += 1
            stdout.flush()

            r.as_origin = AS.objects.get_as_by_ip(r.ip_origin).asn
            r.as_destination = AS.objects.get_as_by_ip(r.ip_destination).asn
            r.save()