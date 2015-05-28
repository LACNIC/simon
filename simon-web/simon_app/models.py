from django.db.models import Q
from django.db import models, connection
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from datetime import datetime, timedelta
import trparse
import simon_project.settings as settings
import geoip2
import json, requests


class Region(models.Model):
    name = models.CharField(max_length=80)
    numcode = models.IntegerField(null=True)

    def __unicode__(self):
        return self.printable_name


class CountryManager(models.Manager):
    def get_region_countries(self):
        return Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3))

    def get_region_countrycodes(self):
        return self.get_region_countries().values_list('iso', flat=True)

    def get_countries_with_no_testpoints(self):
        return self.get_region_countries().exclude(iso__in=TestPoint.objects.values_list('country', flat=True))

    def get_countries_with_testpoints(self):
        return self.get_region_countries().filter(iso__in=TestPoint.objects.values_list('country', flat=True))

    def get_country_with_least_results(self, ip_version, test_type='tcp_web', amount=1, days=7, country_origin=''):
        """
			Function that provides the next country to perform the test.
			It must be very fast, as every single tester will make this call, at least once (lots of traffic).
		"""

        amount = int(amount)
        days = int(days)
        if amount <= 0 or days <= 0:
            return None

        # First check those countries without any tests in the last 'days' days
        # cc_all = Country.objects.get_region_countries().values_list('iso', flat=True)
        # cc_with =  Results.objects.filter(date_test__gte=datetime.now() - timedelta(days), testype = test_type).values_list('country_destination', flat=True)
        # cc_without_testpoints = Country.objects.get_countries_with_no_testpoints().values_list('iso', flat=True)
        # cc_without = list(set(cc_all) - set(set(cc_without_testpoints)) - set(cc_with))
        # n  = len(cc_without)

        # in case i'm asking for more than i can
        # if amount > n:
        # amount = n

        # if n > 0:
        # print 'without'
        # return cc_without[:amount]

        # If all countries have tests in the last 'days' days, then check the one which has least amount of tests
        if country_origin != '':
            country_origin = "country_origin = '%s' and" % country_origin
        cursor = connection.cursor()
        sql = "select country_destination from ( select country_destination , count(*) from ( select * from simon_app_results where %s testype = '%s' and date_test >= now() - interval '%sd' ) AS x group by country_destination order by count asc limit %s ) AS y" % (
            country_origin, test_type, days, amount)
        cursor.execute(sql)
        R = cursor.fetchall()

        result = []
        for r in R:
            result.append(r[0])

        return result


class Country(models.Model):
    iso = models.CharField(max_length=2)
    name = models.CharField(max_length=80)
    printable_name = models.CharField(max_length=80)
    iso3 = models.CharField(max_length=3, null=True, blank=True)
    numcode = models.IntegerField(null=True)
    region = models.ForeignKey(Region)
    objects = CountryManager()

    def __unicode__(self):
        return self.printable_name


class ThroughputResults(models.Model):
    date_test = models.DateTimeField('test date')
    ip_origin = models.GenericIPAddressField()
    ip_destination = models.GenericIPAddressField()
    testype = models.CharField(max_length=20)
    time = models.IntegerField(null=True)
    size = models.IntegerField(null=True)
    country_origin = models.CharField(max_length=2)
    country_destination = models.CharField(max_length=2)
    ip_version = models.IntegerField()
    tester = models.CharField(max_length=20)
    tester_version = models.CharField(max_length=10)

    def __unicode__(self):
        return self.ip_origin

    def set_date_time(self, date, time):
        self.date_test = date + " " + time

    def set_data_test(self, tag, text):
        # if(tag == 'version'):
        # self.version = text
        # if(tag == 'local_country'):
        # self.country_origin = text
        if (tag == 'destination_ip'):
            self.ip_destination = text
        if (tag == 'testtype'):
            self.testype = text
        # if(tag == 'number_probes'):
        # self.number_probes = text
        if (tag == 'size'):
            self.size = text
        if (tag == 'time'):
            self.time = text
        if (tag == 'ip_version'):
            self.ip_version = text
        if (tag == 'tester'):
            self.tester = text
        if (tag == 'tester_version'):
            self.tester_version = text


class ASManager(models.Manager):
    def get_as_by_ip(self, ip_address):
        try:
            return AS.objects.raw(
                "SELECT * FROM simon_app_as WHERE INET(network) >>= inet '%s' ORDER BY pfx_length DESC LIMIT 1" % ip_address)[0]
        except IndexError:
            return AS.objects.get(id=1)  # 0.0.0.0/0


# for autsys in AS.objects.order_by('-pfx_length'):
# if IPAddress(ip_address) in IPNetwork(autsys.network):
# return autsys

class AS(models.Model):
    asn = models.IntegerField()
    network = models.GenericIPAddressField()
    pfx_length = models.IntegerField()
    objects = ASManager()

    def __unicode__(self):
        return "ASN %s" % (self.asn)


class ResultsManager(models.Manager):
    def clean(self):
        return Results.objects.filter(ave_rtt__lte=800).filter(ave_rtt__gt=0)

    def applet(self):
        return Results.objects.clean().filter(tester='Applet')

    def javascript(self):
        return Results.objects.clean().filter(tester='JavaScript')

    def inner(self):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("SELECT country_destination, AVG(ave_rtt) FROM simon_app_results WHERE country_origin = country_destination GROUP BY country_destination")
        return cursor.fetchall()

    def ipv4(self):
        return Results.objects.clean().filter(ip_version='4')

    def ipv6(self):
        return Results.objects.clean().filter(ip_version='6')

    def get_yearly_results(self):
        return Results.objects.javascript().filter(date_test__gt=datetime.now() - timedelta(365))

    def get_weekly_results(self):
        return Results.objects.javascript().filter(date_test__gt=datetime.now() - timedelta(7))

    def get_daily_results(self):
        return Results.objects.javascript().filter(date_test__gt=datetime.now() - timedelta(1))

    def get_hourly_results(self):
        return Results.objects.javascript().filter(date_test__gt=datetime.now() - timedelta(hours=1))

    def get_results_by_as_origin(self, as_number):
        res = []
        for asn in AS.objects.filter(asn=as_number):  # asns list
            res.append(Results.objects.filter(as_origin_id=asn.id))
        return res

    def get_results_by_as_destination(self, as_number):
        res = []
        for asn in AS.objects.filter(asn=as_number):  # asns list
            res.append(Results.objects.filter(as_destination_id=asn.id))
        return res

    def get_results_by_as_origin_and_destination(self, asn_origin, asn_destination):
        # return Results.objects.filter(Q(as_destination__asn=asn_origin) & Q(as_origin__asn=asn_destination))

        res = []
        for as_origin in AS.objects.filter(asn=asn_origin):  # asns list
            for as_destination in AS.objects.filter(asn=asn_destination):  # asns list
                if Results.objects.filter(
                                Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)).count() > 0:
                    res.extend(
                        Results.objects.filter(Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)))
        return res

    def get_results_by_as(self, as_number):
        from itertools import chain

        return list(chain(self.get_results_by_as_origin(as_number), self.get_results_by_as_destination(as_number)))


class Results(models.Model):
    date_test = models.DateTimeField('test date', default=datetime.now())
    version = models.IntegerField(null=True, default=0)
    ip_origin = models.GenericIPAddressField(default='127.0.0.1')
    ip_destination = models.GenericIPAddressField(default='127.0.0.1')
    testype = models.CharField(max_length=20, default='N/A')
    number_probes = models.IntegerField(null=True)
    min_rtt = models.IntegerField(null=True)
    max_rtt = models.IntegerField(null=True)
    ave_rtt = models.IntegerField(null=True)
    dev_rtt = models.IntegerField(null=True)
    median_rtt = models.IntegerField(null=True)
    packet_loss = models.IntegerField(null=True)
    country_origin = models.CharField(max_length=2)
    country_destination = models.CharField(max_length=2)
    ip_version = models.IntegerField(default=0)
    tester = models.CharField(max_length=20)
    tester_version = models.CharField(max_length=10)
    as_origin = models.ForeignKey(AS, related_name='as_origin', default=0)
    as_destination = models.ForeignKey(AS, related_name='as_destination', default=0)
    user_agent = models.CharField(max_length=200, default='')
    url = models.CharField(max_length=2000, default='')
    objects = ResultsManager()

    def __unicode__(self):
        return "%s -> %s | %s/%s/%s/%s | %s | %s v.%s" % (
            self.country_origin, self.country_destination, self.min_rtt, self.ave_rtt, self.max_rtt, self.dev_rtt,
            self.date_test.strftime('%d/%m/%Y %H:%M'), self.tester, self.tester_version)

    def set_date_time(self, date, time):
        self.date_test = date + " " + time

    def get_as_origin(self):
        return AS.object.get_as_by_ip(self.ip_origin)

    def get_as_destination(self):
        return AS.object.get_as_by_ip(self.ip_destination)

    def set_data_test(self, tag, text):
        # if(tag == 'version'):
        # self.version = text
        # if(tag == 'local_country'):
        # self.country_origin = text
        if (tag == 'destination_ip'):
            self.ip_destination = text
        if (tag == 'origin_ip'):
            self.ip_origin = text
        if (tag == 'testtype'):
            self.testype = text
        if (tag == 'number_probes'):
            self.number_probes = text
        if (tag == 'min_rtt'):
            self.min_rtt = text
        if (tag == 'max_rtt'):
            self.max_rtt = text
        if (tag == 'ave_rtt'):
            self.ave_rtt = text
        if (tag == 'dev_rtt'):
            self.dev_rtt = text
        if (tag == 'median_rtt'):
            self.median_rtt = text
        if (tag == 'packet_loss'):
            self.packet_loss = text
        if (tag == 'median_rtt'):
            self.median_rtt = text
        if (tag == 'ip_version'):
            self.ip_version = text
        if (tag == 'tester'):
            self.tester = text
        if (tag == 'tester_version'):
            self.tester_version = text


class TracerouteResultManager(models.Manager):
    def clean(self):
        return TracerouteResult.objects.all().exclude(output__isnull=True).exclude(output__exact='')


class TracerouteResult(Results):
    output = models.TextField(max_length=2000, default='')
    objects = TracerouteResultManager()

    def save(self, *args, **kwargs):
        from geoip2.errors import AddressNotFoundError

        reader = geoip2.database.Reader(settings.GEOIP_DATABASE)
        try:
            if self.ip_origin is not None:
                self.country_origin = reader.city(self.ip_origin).country.iso_code  # TODO llevar a Result
            if self.ip_destination is not None:
                self.country_destination = reader.city(self.ip_destination).country.iso_code  # TODO llevar a Result
        except AddressNotFoundError as e:
            pass

        super(TracerouteResult, self).save(*args, **kwargs)

    def __str__(self):
        return self.pretty_print()

    def pretty_print(self):
        from geoip2.errors import AddressNotFoundError

        reader = geoip2.database.Reader(settings.GEOIP_DATABASE)

        tr = self.parse()
        if tr is None:
            return ""

        try:
            destination = str(reader.city(tr.dest_ip).country.iso_code)
        except AddressNotFoundError as e:
            destination = '?'
        try:
            origin = str(reader.city(self.ip_origin).country.iso_code)
        except AddressNotFoundError as e:
            origin = '?'

        hops = []
        n = len(tr.hops)
        for h in tr.hops:
            rtts = []
            [rtts.append(p.rtt) for p in h.probes if p.rtt is not None]
            m = len(rtts)
            if m > 0:
                hops.append("%.2f" % (sum(rtts) / m))
            else:
                hops.append("%.2f" % (0.0))
        return self.output  # "%s --> %s (%s %s hops) %s" % (self.ip_origin, tr.dest_ip, hops, n, self.date_test.strftime("%d/%m/%Y"))

    def parse(self):
        try:
            if self.output is not "":
                return trparse.loads(self.output)
            return None
        except Exception:
            return None


class RipeAtlasResult(Results):
    probe_id = models.IntegerField(null=False)
    measurement_id = models.IntegerField(null=False)
    type = CharField(max_length=100)
    oneoff = models.BooleanField(default=False)


class RipeAtlasPingResult(RipeAtlasResult):
    def is_valid(self):

        if self.min_rtt > 0 and self.max_rtt > 0 and self.ave_rtt > 0:
            pass
        else:
            return False

        ccs = Country.objects.get_region_countrycodes()
        return self.country_origin in ccs and self.country_destination in ccs

    def merge(self, ripeAtlasPingResult):
        """
        Used for merging multiple results, Useful if we don't want to crwod our database
        :param ripeAtlasPingResult:
        :return:
        """
        res = RipeAtlasPingResult(
            min_rtt=min(self.rtt_min, self.rtt_min),
            max_rtt=max(self.rtt_max, self.rtt_max),
            ave_rtt=(self.rtt_average + self.rtt_average) / 2.0,
            median_rtt=0,  # it's not possible to combine (unless we merge the samples...) #TODO store the result samples
            number_probes=self.packets_sent + self.packet_loss,
            packet_loss=self.packet_loss + self.packet_loss
        )
        return res


class RipeAtlasTracerouteResult(RipeAtlasResult):
    pass


class RipeAtlasMeasurement(models.Model):
    measurement_id = models.IntegerField(null=False)
    running = models.BooleanField(default=True)
    type = CharField(max_length=100)


class TestPointManager(models.Manager):
    def get_ipv4(self):
        cursor = connection.cursor()
        return TestPoint.objects.exclude(ip_address__contains=':')

    def get_ipv6(self):
        cursor = connection.cursor()
        return TestPoint.objects.filter(ip_address__contains=':')


class TestPoint(models.Model):
    # testpointid is automatically inserted as Django identifier
    description = models.TextField(default='')
    testtype = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=2)
    enabled = models.BooleanField(default=False)
    date_created = models.DateTimeField('test date', default=datetime.now(), null=True)
    url = models.TextField(null=True)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    objects = TestPointManager()

    def __unicode__(self):
        return self.ip_address


class Images(models.Model):
    size = models.IntegerField(null=True)  # Bytes size
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    type = models.TextField()
    timeout = models.IntegerField(null=True)
    online = models.BooleanField(default=True)
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Images_in_TestPoints(models.Model):
    testPoint = models.ForeignKey(TestPoint)
    image = models.ForeignKey(Images)
    local_path = models.TextField()

    def __unicode__(self):
        return self.local_path


class OfflineReport(models.Model):
    ip_address = models.GenericIPAddressField()
    date_reported = models.DateTimeField('report date')
    report_count = models.IntegerField(null=True)

    def __unicode__(self):
        return self.ip_address


class Configs(models.Model):
    config_name = models.TextField()
    config_value = models.TextField()
    config_description = models.TextField()

    def __unicode__(self):
        return self.config_value


class Params(models.Model):
    config_name = models.TextField()
    config_value = models.TextField()

    def __unicode__(self):
        return self.config_value


class ActiveTokens(models.Model):
    token_value = CharField(max_length=100)
    token_expiration = models.DateTimeField('expiration daytime')
    testpoint = models.ForeignKey(TestPoint)


class Notification(models.Model):
    title = models.TextField(default='')
    text = models.TextField(default='')
    date_created = models.DateTimeField(default=datetime.now())

    def expiration_date(self):
        return self.date_created + datetime.timedelta(days=7)


class Alert(Notification):
    # Yellow
    pass


class Success(Notification):
    # Green
    pass


class Error(Notification):
    # Red
    pass


class ChartManager(models.Manager):
    url = settings.CHARTS_URL + "/hist/code"

    def javascriptChart(self, cc1, divId, date_from, date_to, cc2=None, bidirectional=True):
        rtts = self.filterQuerySet(Results.objects.javascript(), cc1=cc1, cc2=cc2, date_from=date_from, date_to=date_to, bidirectional=bidirectional)

        data = dict(data=json.dumps([list(rtts)]),
                    divId=divId,
                    labels=json.dumps(['%s latency' % cc1]),
                    colors=json.dumps(['orange']))
        return requests.post(self.url, data=data).text

    def appletChart(self, cc1, divId, date_from, date_to, cc2=None, bidirectional=True):
        rtts = self.filterQuerySet(Results.objects.applet(), cc1=cc1, cc2=cc2, date_from=date_from, date_to=date_to, bidirectional=bidirectional)

        data = dict(data=json.dumps([list(rtts)]),
                    divId=divId,
                    labels=json.dumps(['%s latency' % cc1]),
                    colors=json.dumps(['orange']))
        return requests.post(self.url, data=data).text

    def asyncChart(self, data, cc1, divId, date_from, date_to, labels, colors, cc2=None, bidirectional=True):
        from django.template import Context
        from django.template.loader import get_template

        t = get_template("panels/async_chart.panel.html")
        ctx = Context({
            'divId':divId,
            'data':data,
            'labels':labels,
            'colors':colors
        })
        return t.render(ctx)


    def filterQuerySet(self, queryset, cc1, date_from, date_to, cc2=None, bidirectional=True):
        """
        :param queryset:
        :param cc1:
        :param cc2:
        :param year:
        :return:
        """

        if cc2 is None:
            # one country
            queryset = queryset.filter(
                Q(country_origin=cc1) | Q(country_destination=cc1)
            )
        else:
            # two countries
            if bidirectional:
                queryset = queryset.filter(
                    Q(country_origin=cc1) & Q(country_destination=cc2) \
                    | Q(country_origin=cc2) & Q(country_destination=cc1)
                )
            else:
                queryset = queryset.filter(
                    Q(country_origin=cc1) & Q(country_destination=cc2))

        return queryset.filter(Q(date_test__gte=date_from) & Q(date_test__lte=date_to)) \
            .values_list('ave_rtt', flat=True)


class Chart(models.Model):
    objects = ChartManager()
    pass