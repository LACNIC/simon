'''
Created on 12/11/2012

@author: agustinf
'''
# -*- encoding: utf-8 -*-
from __future__ import division
from django.db.models import Q
from django.http import HttpResponse
from simon_app.functions import bps2KMG, whoIs
from simon_app.models import *
import datetime
import gviz_api
import json
import math
import psycopg2
import re
import simon_project.settings as settings
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.decorators.http import require_http_methods
from django.conf.urls import url

# Final URLs object
# urlpatterns = [
#                        url(r'^$', latency)
# ]

@require_http_methods(["GET"])
def latency(request):

    # country='all'
    # ip_ver='all'
    # year=2009
    # month=01

    year_from = request.GET.get("year_from")
    year_to = request.GET.get("year_to")
    month_from = request.GET.get("month_from")
    month_to = request.GET.get("month_to")
    day_from = request.GET.get("day_from")
    day_to =request.GET.get("day_to")
    country_origin = request.GET.get("country_origin")
    country_destination = request.GET.get("country_dest")
    ip_version = request.GET.get("ip_version")
    protocol = request.GET.get("protocol")
    as_origin =  request.GET.get("as_origin")
    as_destination = request.GET.get("as_dest")
    item_nums = request.GET.get("number_of_items")
    # url = request.GET.get("url")

    # Date filters
    if year_from == None:
        year_from = 2009
    if month_from == None:
        month_from = 01
    if day_from == None:
        day_from = 1
    if year_to == None:
        year_to = datetime.date.today().year
    if month_to == None:
        month_to = datetime.date.today().month
    if day_to == None:
        day_to = datetime.date.today().day
    date_from = datetime.date(int(year_from), int(month_from), int(day_from))
    date_to = datetime.date(int(year_to), int(month_to), int(day_to))
    date_filter = Q(date_test__gte = date_from) & Q(date_test__lte = date_to)

    #Verifying country codes
    cc = Country.objects.get_lacnic_countrycodes()

    if str(country_origin) in cc and str(country_destination) in cc:
        country_filter = Q(country_origin = country_origin) & Q(country_destination = country_destination)
    elif str(country_origin) not in cc and str(country_destination) in cc:
        country_filter = Q(country_destination = country_destination)
    elif str(country_destination) not in cc and str(country_origin) in cc:
        country_filter = Q(country_origin=country_origin)
    else:
        country_filter = Q()

    # ASN filters
    if str(as_origin) in settings.asns and str(as_destination) in settings.asns:
        as_filter = Q(as_origin = as_origin) & Q(as_destination = as_destination)
    elif str(as_origin) not in settings.asns and str(as_destination) in settings.asns:
        as_filter = Q(as_destination = as_destination)
    elif str(as_destination) not in settings.asns and str(as_origin) in settings.asns:
        as_filter = Q(as_origin=as_origin)
    else:
        as_filter = Q()

    # Verifying ip version
    if ip_version == None or int(ip_version) != 4 and int(ip_version) !=6:
        ip_version_filter = Q()
    else:
        ip_version_filter = Q(ip_version = ip_version)

    # Setting tester
    prot = ['HTTP', 'ICMP', 'NTP']
    if protocol != None and str(protocol) in prot:
        tester = settings.PROTOCOLS[str(protocol)]
        tester_filter = Q(tester = tester)
    else:
        tester_filter = Q()

    results = Results.objects.filter(date_filter, country_filter, as_filter, ip_version_filter, tester_filter)

    # number of items per page
    if item_nums == None:
        item_nums = 50

    # date_from = datetime.date(int(year), int(month), 1)
    # results = Results.objects.filter(Q(date_test__gt=date_from))
    #
    # ip_filter = Q()
    # if ip_ver is not 'all':
    #     ip_filter = Q(ip_version=ip_ver)
    #
    # country_filter = Q()
    # if country is not 'all':
    #     country_filter = Q(country_origin=country) | Q(country_destination=country)
    #
    # results = results.filter(ip_filter, country_filter) # All filters are applied

    paginator = Paginator(results, item_nums)

    page = request.GET.get('page_number')
    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        res = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        res = paginator.page(paginator.num_pages)

    results_list = []
    for result in res.object_list:
        row = {}
        row['min_rtt'] = result.min_rtt
        row['max_rtt'] = result.max_rtt
        row['ave_rtt'] = result.ave_rtt
        row['dev_rtt'] = result.dev_rtt
        row['median_rtt'] = result.median_rtt
        row['country_origin'] = result.country_origin
        row['country_destination'] = result.country_destination
        row['as_origin'] = result.as_origin
        row['as_destination'] = result.as_destination
        row['date_test'] = str(result.date_test)
        row['ip_version'] = str(result.ip_version)
        row['tester'] = str(result.tester)
        results_list.append(row)

    if res.has_next():
        next = settings.SIMON_URL+"/apiv2/?page="+str(res.next_page_number())
    else:
        next = ""

    if res.has_previous():
        prev = settings.SIMON_URL+"/apiv2/?page="+str(res.previous_page_number())
    else:
        prev = ""

    response = {
        "results": results_list,
        "next": next,
        "previous": prev,
        "pages": str(paginator.num_pages),
        "current": str(res.number),
        "per_page": str(paginator.per_page),
        "total_results": str(paginator.count),
        "start_index": str(res.start_index()),
        "end_index": str(res.end_index())
    }

    json_response = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
    return HttpResponse(json_response , content_type='application/json')