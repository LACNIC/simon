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
import random
import re
import simon_project.settings as settings
from django.views.decorators.csrf import csrf_exempt


def ntp_points(request):
    points = TestPoint.objects.filter(testtype='ntp', enabled=True)
    json_points = []
    i = 0
    for point in points:
        point_dict = {'index': i, 'description': point.description, 'testtype': point.testtype,
                      'ip_address': point.ip_address, 'countryCode': point.country,
                      'date_added': str(point.date_created)}
        json_points.append(point_dict)
        i += 1

    response = json.dumps(json_points)
    #    response = "{ \"points\": "+response+" }"

    return response


def web_points(request, amount, ip_version):
    """
        Returns a JSONP array containing the WEB points
    """
    callback = request.GET.get('callback')

    points = []
    if int(ip_version) == 6:
        points = SpeedtestTestPoint.objects.get_ipv6()
    elif int(ip_version) == 4:
        points = SpeedtestTestPoint.objects.get_ipv4()

    country = Country.objects.get_countries_with_testpoints().order_by('?')[0]
    #     points = points.filter(testtype='tcp_web', country=country.iso, enabled=True).order_by('?')[:int(amount)]
    points = points.filter(testtype='tcp_web', enabled=True).order_by('?')[:int(amount)]

    countries = Country.objects.all()

    all_images_in_testpoints = Images_in_TestPoints.objects.all()
    all_images = Images.objects.all()
    json_points = []

    for point in points:

        point_dict = {'ip': '', 'url': '', 'country': '', 'region': '', 'countryName': '', 'images': ''}
        point_dict['ip'] = point.ip_address
        point_dict['url'] = point.url
        point_dict['country'] = point.country
        point_dict['countryName'] = countries.get(iso=point.country).printable_name

        try:
            point_dict['region'] = countries.get(iso=point.country).region.numcode
            # city = whoIs(point.ip_address)['operator']['city']
            # city = whoIs(point.ip_address)['entities'][0]['postalAddress'][2]
            #             city = whoIs(point.ip_address)['entities'][0]['vcardArray'][1][2][3][3]
            city = point.city
            point_dict['city'] = city
        except (TypeError, HTTPError):
            # IP is probably a local address
            print 'Error retrieving test point city'
        except Region.DoesNotExist:
            # Extreme cases (Antartica?)
            print 'Error retrieving test point region'

        pointImages = all_images_in_testpoints.filter(testPoint_id=point.id)

        imagesList = []
        for pointImage in pointImages:
            image = all_images.get(pk=pointImage.image_id)
            image_dict = {'path': pointImage.local_path, 'size': image.size, 'width': image.width,
                          'height': image.height, 'type': image.type, 'timeout': image.timeout, 'name': image.name}

            imagesList.append(image_dict)

        point_dict['images'] = json.dumps(imagesList)
        json_points.append(point_dict)

    random.shuffle(json_points)  # Randomize points to give an illusion of parallelism to the user

    response = json.dumps(json_points)
    response = "{ \"points\": " + response + " }"

    if callback is None:
        return response
    else:
        return '%s( %s );' % (callback, response)  # JSONP wrapper


def web_configs(request):
    """
        Returns JSONP from all the configs
    """

    callback = request.GET.get('callback')

    res = {}
    for config in Configs.objects.all():
        res[config.config_name] = config.config_value

    response = "{ \"configs\": " + json.dumps(res) + " }"
    response = '%s( %s );' % (callback, response)
    return HttpResponse(response)




    #######
    # API #
    #######


def latency(request, country='all', ip_version='all', year=2009, month=01):
    """
    API View in charge of returning Latency queries

    :param request:
    :param country:
    :param ip_version:
    :param year:
    :param month:
    :return:
    """

    # if request.GET.get('year') is not None:

    date_from = datetime.date(int(year), int(month), 1)
    results = Results.objects.filter(Q(date_test__gt=date_from))

    if ip_version is not 'all':
        results = results.filter(Q(ip_version=ip_version))

    if country is not 'all':
        results = results.filter(Q(country_origin=country) | Q(country_destination=country))

    response = []
    for result in results:
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
        response.append(row)

    json_response = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))

    return HttpResponse(json_response, mimetype="application/json")


def ases(request, asn_origin, asn_destination):
    """
    API View in charge of returning AS queries

    :param request:
    :param asn_origin:
    :param asn_destination:
    :return:
    """

    res = Results.objects.get_results_by_as_origin_and_destination(int(asn_origin), int(asn_destination))

    response = []
    for result in res:
        row = {}
        row['min_rtt'] = result.min_rtt
        row['max_rtt'] = result.max_rtt
        row['ave_rtt'] = result.ave_rtt
        row['dev_rtt'] = result.dev_rtt
        row['median_rtt'] = result.median_rtt
        row['as_origin'] = result.as_origin
        row['as_destination'] = result.as_destination
        row['date_test'] = str(result.date_test)
        row['ip_version'] = str(result.ip_version)
        row['tester'] = str(result.tester)
        response.append(row)

    json_response = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))

    return HttpResponse(json_response, mimetype="application/json")


def throughput(request, country='all', ip_version='all', year=2009, month=01):
    # Returns JSON with latency

    date_from = datetime.date(int(year), int(month), 1)
    results = ThroughputResults.objects.filter(Q(date_test__gt=date_from))

    if ip_version is not 'all':
        results = results.filter(Q(ip_version=ip_version))

    if country is not 'all':
        results = results.filter(Q(country_origin=country) | Q(country_destination=country))

    response = []
    for result in results:
        row = {}
        row['time'] = result.time
        row['size'] = result.size
        row['country_origin'] = result.country_origin
        row['country_destination'] = result.country_destination
        row['date_test'] = str(result.date_test)
        row['ip_version'] = str(result.ip_version)
        row['tester'] = str(result.tester)
        response.append(row)

    json_response = json.dumps(response)

    return HttpResponse(json_response, mimetype="application/json")

    ##########
    # CHARTS #
    ##########


def servers_locations_maps(request):
    """
    View that returns an array with all those cities which have test points. The returned array contains unique cities and their point
    count. It has the following format: [{'city' : Montevideo, 'num_points' : 3}, ... , {'city' : Santiago de Chile, 'num_points' : 5}].
    """
    table = []

    for t in TestPoint.objects.all():
        done = False
        try:
            for i, row in enumerate(table):
                if row['city'] == t.city:
                    table[i]['num_points'] += 1
                    done = True
                    break
            if not done:
                new_row = {}
                new_row['city'] = t.city
                new_row['num_points'] = 1
                table.append(new_row)
        except TypeError:
            print 'Error when getting city.'

    description = {
        "city": ("string", "City"),
        "num_points": ("number", "Number of servers")
    }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    servers_map = data_table.ToJSon(
        columns_order=("city", "num_points"),
        order_by="city"
    )

    result = '{\"table\":  ' + servers_map + '}'
    return result


def servers_locations_maps2(request):
    keys = ['city', 'num_points']
    table = []
    for ip_address in TestPoint.objects.all().values_list('ip_address', flat=True):
        row = []
        try:
            # city = whoIs(ip_address)['operator']['city']# g.city(ip_address)['city']
            # city = whoIs(ip_address)['entities'][0]['postalAddress'][2]
            city = whoIs(ip_address)['entities'][0]['vcardArray'][1][2][3][3]
            row.append(city)
            row.append(1)
            table.append(dict(zip(keys, row)))
        except TypeError:
            print 'Error when getting %s city.' % ip_address

    description = {
        "city": ("string", "City"),
        "num_points": ("number", "Number of servers")
    }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    servers_map = data_table.ToJSon(
        columns_order=("city", "num_points"),
        order_by="city"
    )

    #    keys = ['country', 'num_points']
    #    table = []
    #    for country in Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).values_list('iso', flat=True):
    #        row = []
    #        try:
    #            testpoints = TestPoint.objects.all().filter(country=country)
    #            row.append(country)
    #            row.append(len(testpoints))
    #            table.append(dict(zip(keys, row)))
    #        except TestPoint.DoesNotExist:
    #            print 'Exception: Country %s has no testpoints.' % country
    #
    #    description = {
    #                   "country": ("string", "Country"),
    #                   "num_points": ("number", "Number of servers")
    #                   }
    #    data_table = gviz_api.DataTable(description)
    #    data_table.LoadData(table)
    #    servers_map = data_table.ToJSon(
    #                             columns_order=("country", "num_points"),
    #                             order_by="country"
    #                             )

    result = '{\"table\":  ' + servers_map + '}'
    return result


def region_latency_chart(request):
    ##########################
    # DISTRIBUTION - LATENCY #
    ##########################

    keys = ['category', 'latencyv4', 'latencyv6']
    table = []
    results = Results.objects.all()
    maximum = 500  # results[n-1]
    categories = 20
    for i in range(1, categories):
        row = []
        category_max = i * maximum / float(categories)
        category_min = (i - 1) * maximum / float(categories)
        categroy_results = results.filter(Q(ave_rtt__gte=category_min) & Q(ave_rtt__lt=category_max))
        row.append((category_min + category_max) / 2.0)

        for v in [4, 6]:
            n = len(results.filter(ip_version=v))
            m = len(categroy_results.filter(ip_version=v).values_list('ave_rtt', flat=True).order_by('ave_rtt'))
            row.append(float("%0.2f" % (100 * (m / float(n)))))

        table.append(dict(zip(keys, row)))

    description = {"category": ("number", "Latencia"),
                   "latencyv4": ("number", "IPv4"),
                   "latencyv6": ("number", "IPv6"),
                   }

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    distribution = data_table.ToJSon(
        columns_order=("category", "latencyv4", "latencyv6"),
        order_by="category"
    )

    result = '{\"table\":  ' + distribution + '}'
    return result


def country_latency_chart(request, country):
    """
    View that returns statistical distributions of the requested country, by years.
    """

    #    check if country is country code or number
    cc_regex = '[A-Z]{2}'
    nn_regex = '[0-9]{1,3}'
    if re.match(cc_regex, str(country)) is not None:
        db_country = Country.objects.get(iso=country)
    elif re.match(nn_regex, str(country)):
        db_country = Country.objects.get(id=country)

    maximum = 1000  # maximum latency
    categories = 20  # number of categories that the distribution will have

    country = db_country.iso
    results_country = Results.objects.filter(
        (Q(country_origin=country) | Q(country_destination=country)) & Q(ave_rtt__gte=10))

    results_rtt = results_country.values_list('ave_rtt', flat=True).order_by(
        'ave_rtt')  # results_country.values_list('ave_rtt', flat=True).order_by('ave_rtt')

    years_db = results_country.values_list('date_test', flat=True)  # Get a list containing unique years only
    history_years = []  # list that holds only the year value. ['2009', '2010', ... ]
    for anio_db in years_db:
        history_years.append(anio_db.year)
    history_years = list(set(history_years))  # get unique years only

    keys_history = ['category']
    for year in history_years:
        keys_history.append('latency_%s' % (year))  # ['category', 'latency_2009', 'latency_2010', ...]

    table_history = []
    for i in range(1, categories):
        category_max = i * maximum / float(categories)
        category_min = (i - 1) * maximum / float(categories)

        row = []
        row.append((category_min + category_max) / 2.0)
        for history_year in history_years:
            date_from = datetime.date(history_year, 01, 01)
            date_to = datetime.date(history_year + 1, 01, 01)
            n = results_rtt.filter(Q(date_test__gte=date_from) & Q(date_test__lt=date_to)).count()
            m = results_rtt.filter(
                Q(ave_rtt__gte=category_min) & Q(ave_rtt__lt=category_max) & Q(date_test__gte=date_from) & Q(
                    date_test__lt=date_to)).count()
            try:
                row.append(float("%0.2f" % (100 * (m / float(n)))))
            except ZeroDivisionError:
                print 'Division by zero at tables view'
                row.append(0)
        table_history.append(dict(zip(keys_history, row)))

    description = {"category": ("number", "Latencia")}
    for year in history_years:
        date_from = datetime.date(year, 01, 01)
        date_to = datetime.date(year + 1, 01, 01)
        probes = "%s muestras" % (
        str(len(results_country.filter(Q(date_test__gt=date_from) & Q(date_test__lt=date_to)))))
        description['latency_%s' % (year)] = ("number", '%s (%s)' % (year, probes))

    #     description = {"category": ("number", "Latencia"),
    #                    "latency_2009": ("number", "2009 (%)"),
    #                    "latency_2010": ("number", "2010 (%)"),
    #                    "latency_2011": ("number", "2011 (%)"),
    #                    "latency_2012": ("number", "2012 (%)"),
    #                    "latency_2013": ("number", "2013 (%)"),
    #                    }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table_history)
    distribution_history = data_table.ToJSon(
        order_by="category"
    )
    result = '{\"table\":  ' + distribution_history + '}'
    return result


def inner_latency_chart(request):
    countries = Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).values_list('iso', flat=True)
    keys = ['country', 'latency']
    table = []
    for country in countries:
        results = Results.objects.filter(Q(country_origin=country) & Q(country_destination=country)).values_list(
            'ave_rtt', flat=True)
        row = []
        if len(results) is not 0:
            average = sum(results) / len(results)
            #        else:
            #            average = 0
            row.append(country)
            row.append(average)
            table.append(dict(zip(keys, row)))

    # table description
    description = {"country": ("string", "Country"),
                   "latency": ("number", "Latency")
                   }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    bar_chart = data_table.ToJSon(
        columns_order=("country", "latency"),
        order_by="latency"
    )

    result = '{\"table\":  ' + bar_chart + '}'
    return result


def region_throughput_chart(request):
    K = 1000
    M = K * K
    G = M * K

    keys = ['category', 'bandwidth']
    table = []
    results = ThroughputResults.objects.all().values('size', 'time')
    n = len(results)
    maximum = 20 * M  # results[n-1]
    categories = 9

    # Pre-process
    bandwidths = []
    for result in results:
        if result['time'] is not 0:
            bandwidth = result['size'] * 8000 / result['time']
        else:
            bandwidth = 0
        bandwidths.append(bandwidth)
    # As throughput is not accessible via filters (Q function), we have to 'classify' the data previously'
    categorized_bandwidths = [[]] * categories
    for i in range(1, categories):
        category_max = i * maximum / categories
        category_min = (i - 1) * maximum / categories

        categorized_bandwidths[i] = []
        for bandwidth in bandwidths:
            if bandwidth > category_min and bandwidth < category_max:
                categorized_bandwidths[i].append(bandwidth)

    # Construction of the table
    for categorized_bandwidth in categorized_bandwidths:
        row = []
        m = len(categorized_bandwidth)
        if len(categorized_bandwidth) > 0:
            row.append(float("%0.2f" % (
            (categorized_bandwidth[len(categorized_bandwidth) - 1] + categorized_bandwidth[0]) / (
            2 * M))))  # Display in Mbps
        else:
            row.append(0)
        row.append(float("%0.2f" % (100 * (m / n))))
        table.append(dict(zip(keys, row)))

    description = {"category": ("number", "Ancho de Banda (Mbps)"),
                   "bandwidth": ("number", "Cantidad (%)"),
                   }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    bandwidth_distribution = data_table.ToJSon(
        columns_order=("category", "bandwidth"),
        order_by="category"
    )
    result = '{\"table\":  ' + bandwidth_distribution + '}'
    return result


def throughput_by_country_chart(request):
    K = 1000
    M = K * K
    G = M * K

    countries = Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).values_list('iso', flat=True)
    keys = ['country', 'throughput']
    table = []
    for country in countries:
        results = ThroughputResults.objects.filter(Q(country_origin=country) | Q(country_destination=country)).values(
            'size', 'time')

        row = []
        if len(results) is not 0:
            throughput_results = []
            for result in results:
                if result['time'] is not 0:
                    throughput_results.append(result['size'] * 8000 / (
                    result['time'] * M))  # list of throughput (bps), not {{size, time},{size, time},....}

            average = float("%0.2f" % (sum(throughput_results) / len(throughput_results)))
            #        else:
            #            average = 0
            row.append(country)
            row.append(average)
            table.append(dict(zip(keys, row)))

    # table description
    description = {"country": ("string", "Pais"),
                   "throughput": ("number", "Ancho de Banda")
                   }
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(table)
    bar_chart = data_table.ToJSon(
        columns_order=("country", "throughput"),
        order_by="throughput"
    )

    result = '{\"table\":  ' + bar_chart + '}'
    return result


def tables(request, country_iso, ip_version, year, month, tester, tester_version):  # , test_type):
    #########
    # TABLE #
    #########

    # View that filters the results table for a specific country and processes the data to be presented as a graphical table
    year = int(year)
    month = int(month)
    # Selection is only by YY-mm
    day = 01

    target_countries = Results.objects.all().values_list('country_destination', flat='True').distinct().order_by()
    tests_list = []

    # For large data sets, a raw query performs better than Django built-in queries (filters)
    host = settings.DATABASES['default']['HOST']
    dbname = settings.DATABASES['default']['NAME']
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    for country in target_countries:

        cursor.execute(settings.TABLES_QUERY,
                       [country_iso, country, ip_version, datetime.datetime(year, month, day), tester,
                        tester_version])  # , test_type])
        country_test_subtable = cursor.fetchone()

        min_rtt = country_test_subtable[0]
        max_rtt = country_test_subtable[1]
        if country_test_subtable[2] > 0:
            ave_rtt = math.floor(country_test_subtable[2])
        else:
            ave_rtt = 0
        if country_test_subtable[3] > 0:
            dev_rtt = math.floor(country_test_subtable[3])
        else:
            dev_rtt = 0
        number_probes = country_test_subtable[4]
        if country_test_subtable[5] > 0:
            median_rtt = math.floor(country_test_subtable[5])
        else:
            median_rtt = 0
        packet_loss = country_test_subtable[6]

        # Print: Name (NM)
        country_code = country
        # Name not found, special cases such as EU
        try:
            country_name = Country.objects.get(iso=country)
        except Country.DoesNotExist:
            country_name = 'N/A'
        country = str(country_name) + ' (' + str(country_code) + ')'

        test_item = [country, number_probes, min_rtt, ave_rtt, max_rtt, dev_rtt, median_rtt, packet_loss, ip_version,
                     tester, tester_version]
        keys = ['country_destination', 'number_probes', 'min_rtt', 'ave_rtt', 'max_rtt', 'dev_rtt', 'median_rtt',
                'packet_loss', 'ip_version', 'tester', 'tester_version']
        tests_list.append(dict(zip(keys, test_item)))

    # Columns definitions
    description = {
        "country_destination": ("string", "Country (code)"),
        "number_probes": ("number", "Number probes"),
        "min_rtt": ("number", "Min. RTT (ms)"),
        "ave_rtt": ("number", "Avge. RTT (ms)"),
        "max_rtt": ("number", "Max. RTT (ms)"),
        "dev_rtt": ("number", "Avge. Deviation"),
        "median_rtt": ("number", "Median RTT"),
        "packet_loss": ("number", "Packet loss count"),
        "ip_version": ("string", "IP version"),
        "tester": ("string", "Tester"),
        "tester_version": ("string", "Tester version")
    }

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(tests_list)

    # Creating a JSon string
    table_json = data_table.ToJSon(
        columns_order=("country_destination", "number_probes", "min_rtt", "ave_rtt", "max_rtt", "dev_rtt"),
        order_by="country_destination"
    )

    country_name = Country.objects.get(iso=country_iso)
    date = datetime.datetime(year, month, day)
    now = datetime.datetime.now()

    return table_json, ip_version, country_name, date, now, tester, tester_version


def latency_box_chart(request, country_iso, ip_version, year, month, tester, tester_version):
    print ''


def throughput_json(request, country_iso, ip_version, year, month, tester, tester_version):  # , test_type):
    # View that filters the results table for a specific country and processes the data to be presented as a graphical table
    year = int(year)
    month = int(month)
    # Selection is only by YY-mm
    day = 01

    target_countries = ThroughputResults.objects.all().values_list('country_destination',
                                                                   flat='True').distinct().order_by()
    tests_list = []

    # For large data sets, a raw query performs better than Django built-in queries (filters)
    host = settings.DATABASES['default']['HOST']
    dbname = settings.DATABASES['default']['NAME']
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    for country in target_countries:

        #        cursor.execute(settings.THROUGHPUT_TABLES_QUERY , [country_iso, country, ip_version, datetime.datetime(year, month, day), tester, tester_version])
        cursor.execute(settings.THROUGHPUT_TABLES_QUERY,
                       [country_iso, country, country, country_iso, ip_version, tester,
                        tester_version])  # , test_type])
        country_test_subtable = cursor.fetchone()

        if country_test_subtable is not None:
            if country_test_subtable[0] is not None:
                time = float(country_test_subtable[0]) / 1000
            else:
                time = 0
            if country_test_subtable[1] is not None:
                size = float(country_test_subtable[1]) * 8
            else:
                size = 0

            number_probes = country_test_subtable[2]

            if country_test_subtable[3] is not None and country_test_subtable[4] is not None and country_test_subtable[
                4] is not 0:
                ave_thput = math.floor(country_test_subtable[3] * 8000 / country_test_subtable[4])
                ave_thput = bps2KMG(ave_thput)  # Human-friendly
            else:
                ave_thput = 0
            if country_test_subtable[5] is not None:
                std_dev = math.floor(country_test_subtable[5])
                std_dev = bps2KMG(std_dev)
            else:
                std_dev = 0
        else:
            time = 0
            size = 0
            number_probes = 0
            ave_thput = 0
            std_dev = 0

        # Print: Name (NM)
        country_code = country
        # Name not found, special cases such as EU
        try:
            country_name = Country.objects.get(iso=country)
        except Country.DoesNotExist:
            country_name = 'N/A'
        country = str(country_name) + ' (' + str(country_code) + ')'

        # Make the dictionary
        test_item = [time, size, country, number_probes, ave_thput, std_dev, ip_version, tester, tester_version]
        keys = ['ave_time', 'ave_size', 'country_destination', 'number_probes', 'ave_thput', 'std_dev', 'ip_version',
                'tester', 'tester_version']
        tests_list.append(dict(zip(keys, test_item)))

    #
    # Table creation
    #

    # Columns definitions
    description = {
        "ave_time": ("string", "Avge. time"),
        "ave_size": ("string", "Avge. size"),
        "country_destination": ("string", "Country"),
        "number_probes": ("string", "Number probes"),
        "ave_thput": ("string", "Avge. throughput"),
        "std_dev": ("string", "Std. Deviation"),
        "ip_version": ("string", "IP version"),
        "tester": ("string", "Tester"),
        "tester_version": ("string", "Tester version"),
    }

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(tests_list)

    # Creating a JSon string
    json = data_table.ToJSon(
        columns_order=("country_destination", "number_probes", "ave_thput"),
        order_by="country_destination"
    )

    #
    # Matrix creation
    #



    country_name = Country.objects.get(iso=country_iso)
    #    date = datetime.datetime(year, month, day)
    #    now = datetime.datetime.now()
    return json


#    return render_to_response('table.html', {'json': json, 'ip_version':ip_version, 'country':country_name, 'date':date, 'now':now, 'tester':tester, 'tester_version':tester_version}, getContext(request))

def throughput_tables(request, country_iso, ip_version, year, month, tester, tester_version):  # , test_type):
    # View that filters the results table for a specific country and processes the data to be presented as a graphical table
    year = int(year)
    month = int(month)
    # Selection is only by YY-mm
    day = 01

    target_countries = ThroughputResults.objects.all().values_list('country_destination',
                                                                   flat='True').distinct().order_by()
    tests_list = []

    # For large data sets, a raw query performs better than Django built-in queries (filters)
    host = settings.DATABASES['default']['HOST']
    dbname = settings.DATABASES['default']['NAME']
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    for country in target_countries:

        #        cursor.execute(settings.THROUGHPUT_TABLES_QUERY , [country_iso, country, ip_version, datetime.datetime(year, month, day), tester, tester_version])
        cursor.execute(settings.THROUGHPUT_TABLES_QUERY,
                       [country_iso, country, country, country_iso, ip_version, tester,
                        tester_version])  # , test_type])
        country_test_subtable = cursor.fetchone()

        if country_test_subtable is not None:
            if country_test_subtable[0] is not None:
                time = float(country_test_subtable[0]) / 1000
            else:
                time = 0
            if country_test_subtable[1] is not None:
                size = float(country_test_subtable[1]) * 8
            else:
                size = 0

            number_probes = country_test_subtable[2]

            if country_test_subtable[3] is not None and country_test_subtable[4] is not None and country_test_subtable[
                4] is not 0:
                ave_thput = math.floor(country_test_subtable[3] * 8000 / country_test_subtable[4])
                ave_thput = bps2KMG(ave_thput)  # Human-friendly
            else:
                ave_thput = 0
            if country_test_subtable[5] is not None:
                std_dev = math.floor(country_test_subtable[5])
                std_dev = bps2KMG(std_dev)
            else:
                std_dev = 0
        else:
            time = 0
            size = 0
            number_probes = 0
            ave_thput = 0
            std_dev = 0

        # Print: Name (NM)
        country_code = country
        # Name not found, special cases such as EU
        try:
            country_name = Country.objects.get(iso=country)
        except Country.DoesNotExist:
            country_name = 'N/A'
        country = str(country_name) + ' (' + str(country_code) + ')'

        # Make the dictionary
        test_item = [time, size, country, number_probes, ave_thput, std_dev, ip_version, tester, tester_version]
        keys = ['ave_time', 'ave_size', 'country_destination', 'number_probes', 'ave_thput', 'std_dev', 'ip_version',
                'tester', 'tester_version']
        tests_list.append(dict(zip(keys, test_item)))

    #
    # Table creation
    #

    # Columns definitions
    description = {
        "ave_time": ("string", "Avge. time"),
        "ave_size": ("string", "Avge. size"),
        "country_destination": ("string", "Country"),
        "number_probes": ("string", "Number probes"),
        "ave_thput": ("string", "Avge. throughput"),
        "std_dev": ("string", "Std. Deviation"),
        "ip_version": ("string", "IP version"),
        "tester": ("string", "Tester"),
        "tester_version": ("string", "Tester version"),
    }

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(tests_list)

    # Creating a JSon string
    json = data_table.ToJSon(
        columns_order=("country_destination", "number_probes", "ave_thput"),
        order_by="country_destination"
    )

    #
    # Matrix creation
    #



    country_name = Country.objects.get(iso=country_iso)
    date = datetime.datetime(year, month, day)
    now = datetime.datetime.now()

    return json, ip_version, country_name, date, now, tester, tester_version


import geoip2.database


@csrf_exempt
def getCountry(request):
    def getResponse(callback, cc):
        if callback is None:
            httpResponse = cc
        else:
            httpResponse = '%s({ cc : "%s"});' % (callback, cc)

        return HttpResponse(httpResponse, mimetype="application/json")

    if (request.method != 'GET'):
        return HttpResponse("Invalid method: %s" % request.method)

    try:
        callback = request.GET.get('callback')

        cc = get_cc_from_ip_address(request.META['REMOTE_ADDR'])

        return getResponse(callback, cc)

    except Exception as e:
        return getResponse(callback, cc)


def get_cc_from_ip_address(ip_address):
    error = "XX"
    try:
        reader = geoip2.database.Reader("%s/%s" % (settings.STATIC_ROOT, "geolocation/GeoLite2-City.mmdb"))
        cc = reader.city(ip_address).country.iso_code
    except:
        cc = error
    return cc
