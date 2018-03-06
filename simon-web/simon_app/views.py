# -*- encoding: utf-8 -*-

from __future__ import division
from datadog import statsd
from django.contrib.gis.geoip import GeoIP
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from lxml import etree

from lib.helpers import *
from api_views import \
    country_latency_chart as  country_latency_chart_api, \
    region_latency_chart as region_latency_chart_api, tables as tables_api, \
    throughput_json as throughput_json_api, \
    inner_latency_chart as inner_latency_chart_api, \
    servers_locations_maps as servers_locations_maps_api, \
    region_throughput_chart as region_throughput_chart_api, \
    web_configs as web_configs_api, web_points as web_points_api, \
    ntp_points as ntp_points_api, throughput_tables as throughput_tables_api, \
    latency as latency_api, throughput as throughput_api, \
    throughput_by_country_chart as throughput_by_country_chart_api, getCountry
from functions import *
from mailing import send_mail_point_offline
from models import *
from reportes import GMTUY
import simon_project.settings as settings
from _socket import timeout
from django.views.decorators.cache import cache_page
import logging

from simon_app.decorators import timed_command

from django.http import UnreadablePostError
import operator
from datadog import statsd


#  @timed_command
@cache_page(60 * 60 * 24)
def lab(request):
    """
    """
    return render_to_response('lab.html')


#  @timed_command
@cache_page(60 * 60 * 24)
def thanks(request):
    return render_to_response('thanks.html', getContext(request))


#  @timed_command
@cache_page(60 * 60 * 24)
def about(request):
    return render_to_response('about.html', getContext(request))


#  @timed_command
@cache_page(60 * 60 * 24)
def browserstack(request):
    return render_to_response('browserstack.html', getContext(request))


#  @timed_command
@cache_page(60 * 15)
def articles(request):
    return render_to_response('articles.html', getContext(request))


# ##################
# TRACEROUTE FORM #
# ##################

from reportes import UploadFileForm


#  @timed_command
@csrf_exempt
def traceroute(request):
    """
        View donde son posteados los archivos de traceroute
    """
    if request.method == 'POST':
        fileName = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open("%s/data/traceroute/%s" % (settings.STATIC_ROOT, fileName), 'w') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()

            saveTracerouteResults(request, "%s/data/traceroute/%s" % (settings.STATIC_ROOT, fileName))
        return redirect("simon_app.views.thanks")
    else:
        traceroutes = TracerouteResult.objects.clean().order_by('-date_test')[:5]

        return render(request, 'traceroute.html', {'traceroutes': traceroutes})


#  @timed_command
def traceroute_curl(request):
    ip = request.META['REMOTE_ADDR']
    l_root_4 = "199.7.83.42"
    l_root_6 = "2001:500:3::42"
    run4 = 1
    run6 = 0
    if ':' in ip:
        l_root = l_root_6
        run6 = 1
    else:
        l_root = l_root_4

    return render(request, 'traceroute_curl.html',
                  {
                      'l_root': l_root,
                      'run4': run4,
                      'run6': run6,
                      'domain': settings.SIMON_URL
                  },
                  content_type='text/plain')


#  @timed_command
def saveTracerouteResults(request, fileName):
    """
        Traceroute calculations
    """
    # from IPy import IP

    f = open("%s" % (fileName), 'r')
    lines = f.readlines()
    f.close()

    ip_origin = request.META['REMOTE_ADDR']
    print "origen : %s" % ip_origin
    for line in lines:
        fields = line.split()
        try:
            ip_destination = fields[1]
            print "destino : %s" % ip_destination

            rtts = []
            for field in fields[2:]:
                try:
                    rtts.append(float(field))
                except ValueError:
                    pass

            if len(rtts) > 0:
                stddev = 0

                if len(rtts) > 1:
                    devs = []
                    mean = sum(rtts) / float(len(rtts))
                    for r in rtts:
                        dev = (r - mean) ** 2
                        devs.append(dev)
                    stddev = math.sqrt(sum(devs) / (len(devs) - 1))

                median_rtt = 0
                if len(rtts) == 1:
                    median_rtt = rtts[0]
                elif len(rtts) == 2:
                    median_rtt = mean
                elif len(rtts) == 3:
                    median_rtt = rtts[1]

                try:
                    country_origin = whoIs(ip_origin)['country']
                    country_destination = whoIs(ip_destination)['country']
                except timeout:
                    country_origin = 'XX'
                    country_destination = 'XX'

                r = Results()

                r.date_test = datetime.datetime.now()
                r.version = '1'
                r.ip_origin = ip_origin
                r.ip_destination = ip_destination
                r.testype = 'traceroute'
                r.number_probes = len(rtts) / 2  # counting 'ms' fields
                r.rtt_min = min(rtts)
                r.rtt_max = max(rtts)
                r.rtt_ave = mean
                r.dev_rtt = stddev
                r.median_rtt = median_rtt
                r.packet_loss = 3 - r.number_probes
                r.country_origin = country_origin
                r.country_destination = country_destination
                r.ip_version = 6 if ":" in ip_destination else 4
                r.tester = 'Traceroute'
                r.tester_version = '1'

                r.save()

                print r

        except ValueError as ve:
            print ve
            pass


#  @timed_command
def servers_locations_maps(request):
    result = servers_locations_maps_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def region_throughput_chart(request):
    result = region_throughput_chart_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def throughput_by_country_chart(request):
    result = throughput_by_country_chart_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def web_points(request):
    result = web_points_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def ntp_points(request):
    result = ntp_points_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def web_configs(request):
    response = web_configs_api(request)
    return HttpResponse(response)


#  @timed_command
@cache_page(60 * 60 * 24)
def api(request):
    return render_to_response('api.html', getContext(request))


#  @timed_command
def country_latency_chart(request, country):
    result = country_latency_chart_api(request, country)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def region_latency_chart(request):
    result = region_latency_chart_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def inner_latency_chart(request):
    result = inner_latency_chart_api(request)
    return HttpResponse(result, content_type="application/json")


#  @timed_command
def latency(request, country='all', ip_version=4, year=2009, month=01):
    return latency_api(request, country, ip_version, year, month)


#  @timed_command
def throughput(request, country='all', ip_version=4, year=2009, month=01):
    return throughput_api(request, country, ip_version, year, month)


#  @timed_command
def throughput_json(request, country_iso, ip_version, year, month, tester, tester_version):  # , test_type):
    json = throughput_json_api(request, country_iso, ip_version, year, month, tester, tester_version)
    return HttpResponse(json, content_type="application/json")


#  @timed_command
def throughput_tables(request, country_iso, ip_version, year, month, tester, tester_version):  # , test_type):
    json, ip_version, country_name, date, now, tester, tester_version = throughput_tables_api(request, country_iso,
                                                                                              ip_version, year, month,
                                                                                              tester, tester_version)
    return render_to_response('table.html',
                              {'json': json, 'ip_version': ip_version, 'country': country_name, 'date': date,
                               'now': now, 'tester': tester, 'tester_version': tester_version}, getContext(request))


#  @timed_command
def err404(request):
    return render_to_response('404.html')


#  @timed_command
@csrf_exempt
def post_xml_result(request):
    """
        View que recibe los datos de las mediciones
    """

    logger = logging.getLogger(__name__)

    if request.method != 'POST':
        return HttpResponse("invalid method: %s" % request.method)

    schema_file = '%s/SimonXMLSchema.xsd' % settings.STATIC_ROOT
    # IMPORTANTE ARREGLAR EL SCHEMA DEL PAIS!!
    with open(schema_file) as f_schema:
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(schema=schema)

        try:
            f_source = request.body
        except UnreadablePostError as upe:
            logger.error("UnreadablePostError: %s" % (upe))

        try:
            simon = etree.fromstring(str(f_source), parser)
            tests_list = simon.xpath("test")
            for tests in tests_list:
                result = Results()

                result.version = simon.find('version').text
                result.set_date_time(simon.find('date').text, simon.find('time').text)
                result.country_origin = simon.find('local_country').text

                for field in tests:
                    result.set_data_test(field.tag, field.text)

                result.country_destination = TestPoint.objects.get(ip_address=result.ip_destination).country
                result.tester = simon.find('tester').text
                result.tester_version = simon.find('tester_version').text
                result.as_origin = AS.objects.get_as_by_ip(result.ip_origin).asn
                result.as_destination = AS.objects.get_as_by_ip(result.ip_destination).asn
                result.user_agent = simon.find('user_agent').text
                result.url = simon.find('url').text

                statsd.increment(
                    'Result via HTTP POST',
                    tags=['type:HTTP', 'tester:' + result.tester, 'url:' + result.url] + settings.DATADOG_DEFAULT_TAGS
                )

                result.save()
        except etree.XMLSyntaxError as e:
            # this exception is thrown on schema validation error
            exception = "XML syntax error. exception: %s" % (e)
            logger.error(exception)
        except Exception as e:
            exception = "Error at POST endpoint: %s" % (e)
            logger.error(exception)

    return HttpResponse("END")


#  @timed_command
@csrf_exempt
def post_traceroute(request):
    """
        View que recibe los datos de traceroute.
        Asume que la interfaz que postea los resultados es la misma que originó los tracroutes
    """

    if (request.method != 'POST'):
        return HttpResponse("invalid method: %s" % request.method)

    try:
        output = request.POST['output']
        ip_origin = request.META['REMOTE_ADDR']
    except Exception as e:
        return HttpResponse("ERROR")

    tracerouteResult = TracerouteResult()
    tracerouteResult.output = output
    tracerouteResult.ip_origin = ip_origin
    # tracerouteResult.ip_destination = tracerouteResult.parse().dest_ip

    tracerouteResult.save()

    return HttpResponse("Thanks!\n")


#  @timed_command
@csrf_exempt
def post_xml_throughput_result(request):
    if (request.method != 'POST'):
        return HttpResponse("invalid method: %s" % request.method)

    schema_file = '%s/SimonXMLSchemaThroughput.xsd' % settings.STATIC_ROOT

    with open(schema_file) as f_schema:
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(schema=schema)

        f_source = request.raw_post_data
        # with open(source_file) as f_source:
        try:
            # simon = etree.parse(f_source, parser)
            # simon = simon.getroot()
            simon = etree.fromstring(f_source, parser)

            tests_list = simon.xpath("test")

            for tests in tests_list:
                result = ThroughputResults()

                # seteo los valores de simon
                result.version = simon.find('version').text
                result.set_date_time(simon.find('date').text, simon.find('time').text)
                result.country_origin = simon.find('local_country').text
                result.ip_origin = request.META['REMOTE_ADDR']

                for field in tests:
                    result.set_data_test(field.tag, field.text)

                # seteo el pais de destino
                result.country_destination = TestPoint.objects.filter(ip_address=result.ip_destination).get().country
                result.tester = simon.find('tester').text
                result.tester_version = simon.find('tester_version').text

                result.save()
        except etree.XMLSyntaxError as e:
            # this exception is thrown on schema validation error
            print e
        except Exception as e:
            print e

    return HttpResponse("END")


#  @timed_command
@csrf_exempt
def post_offline_testpoints(request):
    logger = logging.getLogger(__name__)

    if request.method != 'POST':
        return HttpResponse("Invalid method: %s" % request.method)

    schema_file = '%s/SimonXMLSchemaOfflinePoint.xsd' % settings.STATIC_ROOT

    with open(schema_file) as f_schema:
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(schema=schema)

        f_source = request.body

        try:
            report = etree.fromstring(f_source, parser)
            points = report.xpath("point")

            for point in points:
                offline_ip = point.find('destination_ip').text

                statsd.increment(
                    'Offline Testpoint via HTTP POST',
                    tags=['type:HTTP'] + settings.DATADOG_DEFAULT_TAGS
                )

                try:
                    # match
                    offline_report = OfflineReport.objects.get(ip_address=offline_ip)
                    offline_report.report_count += 1

                    tp = TestPoint.objects.get(ip_address=offline_ip)
                    tp.enabled = False
                    tp.save()

                    # send_mail_point_offline(ctx={'point': tp})

                except OfflineReport.DoesNotExist:
                    # New report
                    offline_report = OfflineReport()
                    offline_report.ip_address = offline_ip
                    offline_report.date_reported = datetime.now(GMTUY())
                    offline_report.report_count = 1
                    offline_report.save()

        except etree.XMLSyntaxError as e:
            exception = "Error when matching with schema. Exception: %s" % (e)
            logger.error(exception)
        except Exception as e:
            exception = "Error at offline endpoint. Exception: %s" % (e)
            logger.error(exception)

    return HttpResponse("END")


#  @timed_command
@cache_page(60 * 60 * 24)
def home(request):
    return render_to_response('home.html', getContext(request))


#  @timed_command
def prueba(request):
    context = getContext(request)
    return render_to_response('prueba.html', context)


#  @timed_command
def speedtest(request):
    context = getContext(request)
    return render_to_response('speedtest.html', context)


#  @timed_command
def prueba_rt(request):
    context = getContext(request)
    response = render_to_response('prueba_rt.html', context)
    return response


#  @timed_command
def objectives(request):
    return render_to_response('objectives.html', getContext(request))


#  @timed_command
def participate(request):
    return render_to_response('participate.html', getContext(request))


#  @timed_command
def reports(request):
    from reportes import ReportForm
    from api_views import get_cc_from_ip_address
    from datetime import timedelta

    latency_histogram_applet = latency_histogram_js = latency_histogram_probeapi = latency_histogram_ripe_atlas = cc1 = ""
    matrix_js = matrix_js_origin_cc = matrix_js_destination_cc = []

    if request.method != "POST":
        cc = get_cc_from_ip_address(request.META['REMOTE_ADDR'])
        form = ReportForm(
            initial={
                "country1": Country.objects.get_or_none(iso=cc),
                "date_from": datetime.now() - timedelta(days=365),
                "date_to": datetime.now()
            }
        )
        context = getContext(request)
        context['form'] = form
        context['collapse'] = ""
        return render_to_response('reports.html', context)

    form = ReportForm(request.POST)
    if not form.is_valid():
        return render_to_response('reports.html', {'form': form})

    data = form  # .clean_data

    if data['bidirectional'] == '2':
        bidirectional = True
    else:
        bidirectional = False

    date_from = datetime.strptime(form['date_from'].value(), "%d/%m/%Y")
    date_to = form['date_to'].value()
    if date_to != '':
        date_to = datetime.strptime(date_to, "%d/%m/%Y")
    else:
        date_to = datetime.now(GMTUY())

    country1 = data['country1'].value()
    country2 = data['country2'].value()
    country1_object = Country.objects.get(id=country1)
    cc1 = country1_object.iso
    if country2 == "" or country2 is None:
        cc2 = None
    else:
        cc2 = Country.objects.get(id=country2).iso

    matrix_region_js = Results.objects.results_matrix_cc(tester="JavaScript")
    matrix_js = [(
        m[0],
        m[1],
        int(m[2]),
        int(m[3]),
        int(m[4])
    ) for m in matrix_region_js if m[0] == cc1 or m[1] == cc1]
    matrix_js = sorted(matrix_js, key=lambda tup: tup[2])
    matrix_js_origin_cc = [m for m in matrix_js if m[0] == cc1]  # having origin as CC
    matrix_js_destination_cc = [m for m in matrix_js if m[1] == cc1]  # having destination as CC

    js = Chart.objects.filterQuerySet(
        Results.objects.javascript(),
        cc1=cc1,
        cc2=cc2,
        date_from=date_from,
        date_to=date_to,
        bidirectional=bidirectional
    )
    _a1 = js.filter(country_origin=cc1).values_list('as_origin', flat=True)
    _a2 = js.filter(country_destination=cc1).values_list('as_destination', flat=True)
    countries_js = js.filter(
        country_origin=cc1
    ).values_list('country_destination', flat=True).distinct(
        'country_destination'
    )
    ases_js = []
    [ases_js.append(a) for a in _a1 if a not in ases_js]
    [ases_js.append(a) for a in _a2 if a not in ases_js]
    v6_js = js.filter(ip_version=6)
    v6_count_js = v6_js.count()
    
    MAX_URL_RESULTS = 1500

    latency_histogram_js = {
        'x': [j for j in js][:MAX_URL_RESULTS]
    }

    probeapi = Chart.objects.filterQuerySet(
        Results.objects.probeapi(),
        cc1=cc1,
        cc2=cc2,
        date_from=date_from,
        date_to=date_to,
        bidirectional=bidirectional
    )

    latency_histogram_probeapi = {
        'x': [p for p in probeapi][:MAX_URL_RESULTS]
    }

    countries_probeapi = probeapi.filter(
        country_origin=cc1
    ).values_list('country_destination', flat=True).distinct(
        'country_destination'
    )

    ripe_atlas = Chart.objects.filterQuerySet(
        Results.objects.ripe_atlas(),
        cc1=cc1,
        cc2=cc2,
        date_from=date_from,
        date_to=date_to,
        bidirectional=bidirectional
    )

    latency_histogram_ripe_atlas = {
        'x': [a for a in ripe_atlas]
    }

    v6 = 100.0 * v6_count_js / len(js)
    v4 = 100.0 - v6
    pie_chart = {
        'value': [v4, v6]
    }

    context = getContext(request)
    context['collapse'] = "in"
    context['form'] = form
    context['latency_histogram_probeapi'] = latency_histogram_probeapi
    context['latency_histogram_js'] = latency_histogram_js
    context['latency_histogram_ripe_atlas'] = latency_histogram_ripe_atlas

    context['cc'] = cc1
    context['country'] = country1_object.printable_name
    context['matrix_js'] = matrix_js
    context['matrix_js_origin_cc'] = matrix_js_origin_cc
    context['matrix_js_destination_cc'] = matrix_js_destination_cc
    context['js'] = js
    context['applet'] = applet
    context['ripe_atlas'] = ripe_atlas
    context['probeapi'] = probeapi
    context['date_from'] = date_from
    context['ases_js'] = ases_js
    context['countries_js'] = countries_js
    context['countries_probeapi'] = countries_probeapi
    context['pie_chart'] = pie_chart
    context['v6_count_js'] = "%.1f" % (100.0 * v6_count_js / len(js))

    return render_to_response('reports.html', context)


#  @timed_command
def reports_as(request):
    from reportes import ASForm

    context = getContext(request)
    form = ASForm()
    if request.method != "POST":
        context['form'] = form
        context['collapse'] = ""
        return render_to_response('reports_as.html', context)

    id = request.POST['as_dropdown']
    as_ = AS.objects.get(id=id)

    print as_.asn
    print Results.objects.filter(as_origin=as_.asn)

    context['collapse'] = "in"
    context['as'] = as_

    return render_to_response('reports_as.html', context)


#  @timed_command
def charts(request):
    """

        Regional Charts "Reports" page.

    :param request:
    :return:
    """
    import datetime, json, requests

    # ###########
    # DROPDOWN #
    # ###########


    try:
        ip = request.META.get('REMOTE_ADDR', None)
        g = GeoIP()
        cc = g.country(ip)['country_code']
        logging.info("Accessing from %s" % cc)
    except Exception:
        logging.warning("Error at getting geo information for %s" % ip)

    # ######
    # MAP #
    # ######

    testpoints = TestPoint.objects.all()
    countries = {}
    for tp in testpoints:
        if tp.country is not None:
            cc = tp.country.encode("utf8")
            try:
                countries[cc] += 1
            except KeyError:
                countries[cc] = 1
    items = countries.items()
    countries = ""
    for i in items:
        countries += "%s," % (str(list(i)))

    # #############
    # Histograms #
    ##############

    now = datetime.datetime.now()
    a_month_ago = now - datetime.timedelta(days=30)
    rtts_probeapi = Results.objects.probeapi().filter(
        date_test__gte=a_month_ago,
        country_origin__in=Country.objects.get_lacnic_countrycodes(),
        country_destination__in=Country.objects.get_lacnic_countrycodes()
    ).values_list(
        'ave_rtt', flat=True
    )
    rtts_js = Results.objects.javascript().filter(
        date_test__gte=a_month_ago,
        country_origin__in=Country.objects.get_lacnic_countrycodes(),
        country_destination__in=Country.objects.get_lacnic_countrycodes()
    ).values_list(
        'ave_rtt', flat=True
    )

    # IPv6 penetration chart
    rs = Results.objects.ipv6_penetration_timeline()
    ipv6_penetration_ratios = [(r[2] * 1.0 / (r[1] + r[2])) for r in rs if r[1] > 0 or r[2] > 0]
    results_timeline = Results.objects.get_results_timeline()

    # Inner Latency Chart
    t0 = datetime.datetime.now()

    from operator import itemgetter
    inners = Results.objects.inner(tester=settings.PROTOCOLS["HTTP"], months=6)
    inners = [(cc, _min, _avg, _max, _count) for cc, _min, _avg, _max, _count in inners if
              cc in Country.objects.get_lacnic_countrycodes()]
    inners = sorted([i for i in inners], key=itemgetter(1), reverse=True)  # ordered by min RTT
    inner_isos = []
    inner_lats = []
    inner_lats_min = []
    inner_lats_max = []
    for i, v in enumerate(inners):
        # if v[0] not in Country.objects.get_lacnic_countrycodes(): continue
        if v[1] is None: continue

        iso = "%02d - %s" % (i, str(v[0]))
        inner_isos.append(iso)
        inner_lats_min.append(float(v[1]))
        inner_lats.append(float(v[2]))
        inner_lats_max.append(float(v[3]))

    ###################
    # Charts Services #
    ###################

    # Sync Charts

    url = settings.CHARTS_URL + "/hist/code/"
    data = dict(
        x=json.dumps(
            list(rtts_js)
        ),
        divId='latency_histogram_js',
        labels=json.dumps(['HTTP']),
        colors=json.dumps(['#608BC4'])
    )
    latency_histogram_js = requests.post(url, data=data, headers={'Connection': 'close'}).text
    data = dict(
        x=json.dumps(
            list([rtt for rtt in rtts_probeapi])
        ),
        divId='latency_histogram_probeapi',
        labels=json.dumps(['ICMP']),
        colors=json.dumps(['#608BC4'])
    )
    latency_histogram_probeapi = requests.post(url, data=data, headers={'Connection': 'close'}).text

    results_timeline = {
        'x': list(d[0].strftime("%Y-%m-%d") for d in results_timeline),
        'ys': [
            [int(r[1]) for r in results_timeline],
            [int(r[2]) for r in results_timeline]
        ]
    }

    v6 = {
        'x': list(d[0].strftime("%Y-%m-%d") for d in rs),
        'y': list(ipv6_penetration_ratios)
    }

    inner_count = len(inner_isos)

    avg_list = [a - m for a, m in zip(list(inner_lats), list(inner_lats_min))]
    max_list = [max_ - avg for avg, max_ in zip(list(inner_lats), list(inner_lats_max))]

    inner_latency = {
        'x': inner_isos,
        'y': [list(inner_lats_min), avg_list, max_list]
    }

    # Country information
    from operator import itemgetter

    inner_area = []
    inner = Results.objects.inner(
        tester=settings.PROTOCOLS["HTTP"],
        months=6
    )
    ccs = Country.objects.get_lacnic_countrycodes()
    inner = [(cc, _min, _avg, _max, latency) for cc, _min, _avg, _max, latency in inner if cc in ccs]

    lines = open("%s/restcountries.json" % settings.STATIC_ROOT, 'r').readlines()
    restcountries = json.loads(
        str(lines[0])
    )
    for c in restcountries:
        alpha2Code = c["alpha2Code"]
        if alpha2Code not in ccs:
            continue
        latency_ = 0.0
        for i in inner:
            if i[0] == alpha2Code:
                latency_ = float(i[1])

        borders = c["borders"]

        area = c["area"]
        if area == None: continue

        latency_per_area = 1.0 * latency_ / area
        if latency_per_area > 0.02: continue

        inner_area.append(dict(alpha2Code=alpha2Code, area=area, borders=borders, latency=latency_,
                               latency_per_area=latency_per_area))

    inner_area = sorted([i for i in inner_area if i["latency"] > 0], key=itemgetter("latency_per_area"),
                        reverse=True)  # order
    for i, v in enumerate(inner_area):
        new_key = "%02d - %s" % (i, v["alpha2Code"])
        inner_area[i]["alpha2Code"] = new_key
    inner_area_max = max(list((k["latency_per_area"]) for k in inner_area))

    inner_latency_area = {
        'x': list(k["alpha2Code"].encode('utf-8') for k in inner_area),
        'y': list((k["latency_per_area"] / inner_area_max) for k in inner_area)
    }

    ############
    # RESPONSE #
    ############

    from django.template import RequestContext
    from lib.helpers import simon_processor

    ctx = RequestContext(request, {
        'countries': countries,
        'latency_histogram_probeapi': latency_histogram_probeapi,
        'latency_histogram_js': latency_histogram_js,
        # 'ipv6_penetration': ipv6_penetration,
        'v6': v6,
        'results_timeline': results_timeline,
        'inner_latency': inner_latency,
        'inner_latency_area': inner_latency_area,
        'inner_count': inner_count * 2
    }, processors=[simon_processor])

    return render_to_response('charts.html', ctx)


#  @timed_command
def charts_reports_bandwidth(request):
    return render_to_response('charts_reports_bandwidth.html', getContext(request))


#  @timed_command
def feedbackForm(request):
    """
    View in charge of precessing the feedback form
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse("Invalid Method")

    from django.core.mail import EmailMessage

    post = request.POST
    mensaje = post['mensaje']
    remitente = post['remitente']

    Comment(person=remitente, comment=mensaje).save()

    subject = 'Feedback desde Simón'
    mssg = "%s dice:\n%s" % (remitente, mensaje)
    from_ = 'agustin@lacnic.net'

    to = []
    for admin in settings.ADMINS:
        to.append(admin[1])

    # EmailMessage(subject, mssg, to=["agustin@lacnic.net"]).send()
    # send_mail(subject, mssg, from_, to, fail_silently=False)

    # request.method = 'GET'
    return redirect('simon_app.views.home')


#  @timed_command
def applet(request):
    # return render(request, 'applet.html')
    return render_to_response('applet.html', getContext(request))


#  @timed_command
def applet_run(request):
    # return render(request, 'applet.html')
    return render_to_response('applet_run.html', getContext(request))


#  @timed_command
def v6perf(request):
    ctx = getContext(request)

    latest_v6_perfs = V6Perf.objects.latest_measurements()
    latest_v6_perfs_sorted = sorted(latest_v6_perfs, key=operator.attrgetter('diff'))

    ctx['v6_perfs'] = latest_v6_perfs_sorted

    return render_to_response('v6perf.html', ctx)


#  @timed_command
def v6adoption(request):
    ctx = getContext(request)
    ctx['v6_perfs'] = V6Perf.objects.latest_measurements()
    return render_to_response('v6adoption.html', ctx)


#  @timed_command
@cache_page(60 * 60 * 24)
def atlas(request):
    from collections import Counter, OrderedDict
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    rs = RipeAtlasProbeStatus.objects.get_timeline()

    # get the amount of times the cron job was ran in that day so far
    cron_frequencies = RipeAtlasProbeStatus.objects.get_cron_frequencies()

    connected_timeline = zip([r[1] for r in rs], [cf[1] for cf in cron_frequencies])
    disconnected_timeline = zip([r[2] for r in rs], [cf[1] for cf in cron_frequencies])
    abandoned_timeline = zip([r[3] for r in rs], [cf[1] for cf in cron_frequencies])
    never_timeline = zip([r[4] for r in rs], [cf[1] for cf in cron_frequencies])

    connected_timeline = [conn[0] / conn[1] for conn in connected_timeline]
    disconnected_timeline = [conn[0] / conn[1] for conn in disconnected_timeline]
    abandoned_timeline = [conn[0] / conn[1] for conn in abandoned_timeline]
    never_timeline = [conn[0] / conn[1] for conn in never_timeline]
    data = dict(data=json.dumps(
        [list(d[0].strftime("%d/%m/%Y") for d in rs), connected_timeline, disconnected_timeline, abandoned_timeline,
         never_timeline]),
        divId='statuses_timeline',
        labels=json.dumps(['Connected', 'Disconnected', 'Abandoned', 'Never Connected']),
        colors=json.dumps(['#9BC53D', '#C3423F', '#FDE74C', 'darkgray']),
        kind='AreaChart',
        xAxis='date')
    url = settings.CHARTS_URL + "/code"
    statuses_timeline = requests.post(url, data=data, headers={'Connection': 'close'}).text

    # Basic Atlas stats

    from collections import defaultdict
    status_dict = defaultdict(int)
    status_all = RipeAtlasProbeStatus.objects.distinct('probe')
    for s in status_all:
        status_dict[s.status] += 1

    n = status_all.count()
    if n > 0:
        connected = "%.1f%%" % (status_dict["Connected"] * 100.0 / n)
        disconnected = "%.1f%%" % (status_dict["Disconnected"] * 100.0 / n)
        never = "%.1f%%" % (status_dict["Never Connected"] * 100.0 / n)
        abandoned = "%.1f%%" % (status_dict["Abandoned"] * 100.0 / n)
    else:
        connected = "0.0%%"
        disconnected = "0.0%%"
        never = "0.0%%"
        abandoned = "0.0%%"

    # per country stats

    probes_all = RipeAtlasProbe.objects.all().order_by('country_code')
    countries_with_probes = probes_all.values_list('country_code', flat=True)
    countries_without_probes = [{'iso': c.iso, 'printable_name': c.printable_name} for c in
                                Country.objects.get_lacnic_countries() if c.iso not in countries_with_probes]
    counter = Counter(countries_with_probes)

    # Dict for the map
    map = ""
    for c in counter.items():
        map += "%s," % ([c[0].encode("utf8"), c[1]])

    for cc in counter:
        n = len(probes_all.filter(country_code=cc))
        if n == 0:
            continue

        country_statuses = RipeAtlasProbeStatus.objects.filter(probe__country_code=cc)
        counter[cc] = dict()

        country_connected = len(
            country_statuses.filter(status="Connected").order_by('probe', '-date').distinct('probe'))
        country_disconnected = len(
            country_statuses.filter(status="Disconnected").order_by('probe', '-date').distinct('probe'))
        country_abandoned = len(
            country_statuses.filter(status="Abandoned").order_by('probe', '-date').distinct('probe'))
        country_never = len(
            country_statuses.filter(status="Never Connected").order_by('probe', '-date').distinct('probe'))
        country_all_count = country_connected + country_disconnected + country_abandoned + country_never

        counter[cc]['connected_count'] = country_connected
        counter[cc]['disconnected_count'] = country_disconnected
        counter[cc]['abandoned_count'] = country_abandoned
        counter[cc]['never_count'] = country_never
        counter[cc]['country_all_count'] = country_all_count

        counter[cc]['connected'] = "%.1f%%" % (country_connected * 100.0 / country_all_count)
        counter[cc]['disconnected'] = "%.1f%%" % (country_disconnected * 100.0 / country_all_count)
        counter[cc]['abandoned'] = "%.1f%%" % (country_abandoned * 100.0 / country_all_count)
        counter[cc]['never'] = "%.1f%%" % (country_never * 100.0 / country_all_count)

        counter[cc]['country_name'] = Country.objects.get(iso=cc).printable_name

    counter = OrderedDict(sorted(counter.items(), key=lambda t: t[0]))

    # paginator = Paginator(probes_all, 15)
    # page = request.GET.get('page')
    # try:
    #     probes_paginated = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     probes_paginated = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     probes_paginated = paginator.page(paginator.num_pages)

    ctx = {
        'probes': probes_all,
        'connected': connected,
        'disconnected': disconnected,
        'never': never,
        'abandoned': abandoned,
        'counter': counter,
        'countries_without_probes': countries_without_probes,

        'statuses_timeline': statuses_timeline,

        'map': map
    }

    return render_to_response("atlas.html", ctx, getContext(request))
