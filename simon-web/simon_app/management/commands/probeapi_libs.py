#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import *
from simon_app.reportes import GMTUY
from django.template import Template, Context
import urllib2
import json
import requests
from simon_project.settings import KONG_API_KEY
import datetime
import numpy
from random import sample
from multiprocessing.dummy import Pool as ThreadPool
from simon_app.api_views import get_cc_from_ip_address


def get_countries(ccs=[]):
    url = settings.PROBEAPI_ENDPOINT + "/GetCountries"

    try:
        print "Getting countries..."
        response = get_probeapi_response(url)
        py_object = json.loads(response)
        res = {}
        for p in py_object["GetCountriesResult"]:
            cc = p["CountryCode"]
            if cc in ccs:
                res[cc] = p["ProbesCount"]
        return res
    except Exception as e:
        return None


def get_probeapi_response(url):

    response = requests.get(
        url,
        headers={
            'Apikey': KONG_API_KEY
        }
    ).text

    return response
