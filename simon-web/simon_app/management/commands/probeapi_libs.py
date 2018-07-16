#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from simon_project.settings import KONG_API_KEY, PROBEAPI_ENDPOINT


def get_countries(ccs=[]):
    url = PROBEAPI_ENDPOINT + "/GetCountries"

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
