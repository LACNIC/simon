#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from simon_app.models import Country
        from simon_app.reportes import GMTUY
        from simon_project import passwords
        import urllib2
        import json
        import datetime

        now = datetime.datetime.now(GMTUY())

        ccs = Country.objects.get_region_countries().values_list('iso', flat=True)

        opener = urllib2.build_opener()
        opener.addheaders = [
            ("X-Mashape-Key", passwords.PROBEAPI),
            ("Accept", "application/json")
        ]

        url = "https://probeapifree.p.mashape.com/Probes.svc/GetCountries"

        print url

        response = opener.open(url).read()
        py_object = json.loads(response, parse_int=int)

        region_count = 0
        for object in py_object["GetCountriesResult"]:
            code_ = object["CountryCode"]
            if code_ in ccs:
                count = object["ProbesCount"]
                print code_, count
                region_count += count

        print "Regional count %s" % (region_count)
        print "Query took %s" % (datetime.datetime.now(GMTUY()) - now)