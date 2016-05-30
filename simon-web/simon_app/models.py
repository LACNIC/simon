from django.db.models import Q
from django.db import models, connection
from django.db.models.fields import CharField, IntegerField
from django.db.models.fields.related import ForeignKey
from datetime import datetime, timedelta
import trparse
import simon_project.settings as settings
import geoip2
import json, requests
from django.contrib import admin

from models_management import *  # External models definitions


class Region(models.Model):
    name = models.CharField(max_length=80)
    numcode = models.IntegerField(null=True)

    def __unicode__(self):
        return self.printable_name


class CountryManager(models.Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(self, *args, **kwargs)
        except Exception as e:
            return None

    def get_region_countries(self):
        return Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3))

    def get_region_countrycodes(self):
        return self.get_region_countries().values_list('iso', flat=True)

    def get_countries_with_no_testpoints(self):
        return self.get_region_countries().exclude(iso__in=TestPoint.objects.values_list('country', flat=True))

    def get_countries_with_testpoints(self):
        return self.get_region_countries().filter(iso__in=TestPoint.objects.values_list('country', flat=True))

    def get_countries_with_speedtest_testpoints(self):
        return self.get_region_countries().filter(iso__in=SpeedtestTestPoint.objects.values_list('country', flat=True))

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
            return AS.objects.filter(pfx_length=0).filter(asn=0)[0]


class AS(models.Model):
    asn = models.IntegerField(default=0)
    network = models.GenericIPAddressField(null=True, blank=True)
    pfx_length = models.IntegerField(default=0)
    date_updated = models.DateTimeField(null=True)
    regional = models.NullBooleanField(null=True)

    objects = ASManager()

    def __unicode__(self):
        return "ASN %s" % (self.asn)

    class Meta:
        verbose_name = 'Sistema Autonomo'
        verbose_name_plural = 'Sistemas Autonomos'


class ResultsManager(models.Manager):
    def clean(self):
        return Results.objects.filter(ave_rtt__lte=800).filter(ave_rtt__gt=0)

    def applet(self):
        return Results.objects.clean().filter(tester='Applet')

    def javascript(self):
        return Results.objects.clean().filter(tester='JavaScript')

    def probeapi(self):
        return ProbeApiPingResult.objects.filter(ave_rtt__lte=800).filter(ave_rtt__gt=0)

    def ripe_atlas(self):
        return RipeAtlasPingResult.objects.filter(ave_rtt__lte=800).filter(ave_rtt__gt=0)

    def inner(self, tester, months):
        """
            Returns the inner latency for all the countries
        :param tester: the tester that performed the measurements
        :param months: how many months you want to consider
        :return: QuerySet?
        """
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("SELECT country_destination, AVG(min_rtt), AVG(ave_rtt), AVG(max_rtt), COUNT(*) "
                       "FROM simon_app_results "
                       "WHERE country_origin = country_destination "
                       "AND tester='%s' "
                       "AND date_test > now() - interval '%s months' "
                       "GROUP BY country_destination" % (tester, months))
        return cursor.fetchall()

    def ipv4(self):
        return Results.objects.clean().filter(ip_version='4')

    def ipv6(self):
        return Results.objects.clean().filter(ip_version='6')

    def ipv6_penetration_timeline(self, date=datetime.now(), months=2):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("SELECT date_trunc('day', date_test), SUM(case when ip_version=4 then 1 else 0 end) AS v4 , SUM(case when ip_version=6 then 1 else 0 end) AS v6 " \
                       "FROM simon_app_results " \
                       "WHERE date_test > date '%s' - interval '%s months' " \
                       "AND date_test < now() " \
                       "GROUP BY 1 " \
                       "ORDER BY 1; " % (date, months))
        return cursor.fetchall()

    def get_results_timeline(self):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("SELECT date_trunc('day', date_test), SUM(case when testype='tcp_web' then 1 else 0 end) AS http , SUM(case when testype='ping' then 1 else 0 end) AS icmp " \
                       "FROM simon_app_results " \
                       "WHERE date_test > now() - interval '2 months' " \
                       "AND date_test < now() " \
                       "GROUP BY 1 " \
                       "ORDER BY 1; ")

        return cursor.fetchall()

    def results_matrix_cc(self, date=datetime.now(), months=12, tester="probeapi", ip_version=4):
        from django.db import connection

        date_string = date#.strftime("%Y-%d-%m %H:%M:%S")

        cursor = connection.cursor()
        cursor.execute("SELECT country_origin, country_destination, AVG(min_rtt), AVG(ave_rtt), AVG(max_rtt), COUNT(*) "
                       "FROM "
                       "("
                       "SELECT * FROM simon_app_results "
                       "WHERE ave_rtt > 5 "
                       "AND ave_rtt < 800 "
                       "AND dev_rtt < 0.9 * ave_rtt"
                       ") AS results "
                       "WHERE country_origin IN (select iso FROM simon_app_country WHERE region_id=3) AND country_destination IN (select iso FROM simon_app_country WHERE region_id=3) "
                       "AND tester='%s' "
                       "AND date_test > date '%s' - interval '%s months' "
                       "AND date_test < date '%s' "
                       "AND ip_version=%s"
                       "GROUP BY country_origin, country_destination "
                       "ORDER BY country_origin;" % (tester, date, months, date, ip_version))
        return cursor.fetchall()

    def results_matrix_as(self, date=datetime.now(), months=12, tester="JavaScript", ip_version=4):
        from django.db import connection

        date_string = date

        cursor = connection.cursor()
        cursor.execute("SELECT as_origin, as_destination, AVG(min_rtt), AVG(ave_rtt), AVG(max_rtt), COUNT(*) "
                       "FROM "
                       "("
                       "SELECT * FROM simon_app_results "
                       "WHERE ave_rtt > 5 "
                       "AND ave_rtt < 800 "
                       "AND dev_rtt < 0.9 * ave_rtt"
                       ") AS results "
                       "WHERE country_origin IN (select iso FROM simon_app_country WHERE region_id=3) AND country_destination IN (select iso FROM simon_app_country WHERE region_id=3) "
                       "AND tester='%s' "
                       "AND date_test > date '%s' - interval '%s months' "
                       "AND date_test < date '%s' "
                       "AND ip_version=%s"
                       "GROUP BY as_origin, as_destination "
                       "ORDER BY as_origin;" % (tester, date, months, date, ip_version))
        return cursor.fetchall()

    def get_yearly_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(365))

    def get_weekly_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(7))

    def get_daily_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(1))

    def get_hourly_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(hours=1))

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
        return Results.objects.filter(Q(as_origin=asn_origin) & Q(as_destination=asn_destination))

    def get_results_by_as(self, as_number):
        from itertools import chain

        return list(chain(self.get_results_by_as_origin(as_number), self.get_results_by_as_destination(as_number)))


class Results(models.Model):
    date_test = models.DateTimeField('test date', default=datetime.now())
    version = models.IntegerField(null=True, default=0)
    ip_origin = models.GenericIPAddressField(null=True)
    ip_destination = models.GenericIPAddressField(null=True)
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
    as_origin = models.IntegerField(null=True)
    as_destination = models.IntegerField(null=True)
    user_agent = models.CharField(max_length=2000, default='')
    url = models.CharField(max_length=2083, default='', null=True)
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

    def protocol(self):
        if self.tester == 'Applet' and self.testype == 'tcp_web':
            return "TCP"
        elif self.tester == 'JavaScript' and self.testype == 'tcp_web':
            return "HTTP"
        elif self.tester == 'Applet' and self.testype == 'ntp':
            return "NTP"
        elif self.tester == 'probeapi' and self.testype == 'ping':
            return "ICMP"

    def date_short(self):
        return self.date_test.strftime("%x")

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'

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


class ProbeApiPingResult(Results):
    def save(self, *args, **kwargs):
        self.tester = 'probeapi'
        self.version = 1
        self.tester_version = self.version
        self.testype = 'ping'

        super(ProbeApiPingResult, self).save(*args, **kwargs)  # Call the "real" save() method.

    class Meta:
        verbose_name = 'Resultado ProbeAPI'
        verbose_name_plural = 'Resultados ProbeAPI'


class TracerouteResultManager(models.Manager):
    def clean(self):
        return TracerouteResult.objects.all().exclude(output__isnull=True).exclude(output__exact='')


class TracerouteResult(models.Model):
    ip_origin = models.GenericIPAddressField(null=True)
    ip_destination = models.GenericIPAddressField(null=True)
    as_origin = models.IntegerField(null=True)
    as_destination = models.IntegerField(null=True)
    country_origin = models.CharField(max_length=2)
    country_destination = models.CharField(max_length=2)
    hop_count = models.IntegerField(default=0)

    output = models.TextField(max_length=2000, default='')
    objects = TracerouteResultManager()

    def save(self, *args, **kwargs):
        from geoip2.errors import AddressNotFoundError
        import geoip2.database

        reader = geoip2.database.Reader(settings.GEOIP_DATABASE)
        try:
            if self.ip_origin is not None:
                self.country_origin = reader.city(self.ip_origin).country.iso_code  # TODO llevar a Result
            if self.ip_destination is not None:
                self.country_destination = reader.city(self.ip_destination).country.iso_code  # TODO llevar a Result
        except AddressNotFoundError as e:
            pass

        super(TracerouteResult, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.traceroutehop_set.all()

    def pretty_print(self):
        from geoip2.errors import AddressNotFoundError
        import geoip2.database

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


class TracerouteHop(Results):
    traceroute_result = models.ForeignKey(TracerouteResult)

    def __str__(self):
        print "AS%s (%s) --> AS%s (%s)" % (self.as_origin, self.ip_origin, self.as_destination, self.ip_destination)


class RipeAtlasResult(Results):
    probe_id = models.IntegerField(null=False)
    measurement_id = models.IntegerField(null=False)
    type = CharField(max_length=100)
    oneoff = models.BooleanField(default=False)

class RipeAtlasProbeManager(models.Manager):

    def connected_now(self):
        return RipeAtlasProbe.objects.filter(ripeatlasprobestatus__status="Connected")

    def connected_now_region(self):
        connected_now = self.connected_now()
        ccs = Country.objects.get_region_countries().values_list('iso', flat=True)
        return [_c for _c in connected_now if _c.country_code in ccs]


class RipeAtlasProbe(models.Model):
    probe_id = models.IntegerField(null=True)
    country_code = models.CharField(max_length=2, null=True)
    asn_v4 = models.IntegerField(null=True)
    asn_v6 = models.IntegerField(null=True)
    prefix_v4 = models.GenericIPAddressField(null=True)
    prefix_v6 = models.GenericIPAddressField(null=True)

    objects = RipeAtlasProbeManager()

    def __unicode__(self):
        return self.country_code

    @property
    def latest_status(self):
        reverse_ = RipeAtlasProbeStatus.objects.filter(probe=self).order_by('date').reverse()[0]
        return reverse_

    @property
    def last_check(self):
        return self.latest_status.date

    def last_check_timedelta(self, t1):
        """
        :param now:
        :return: Time diff between latest check and t1
        """
        return t1 - self.last_check

    @property
    def time_since_last_check(self):
        """
        :param now:
        :return:
        """
        from simon_app.reportes import GMTUY
        from datetime import datetime, timedelta
        now = datetime.now(tz=GMTUY())
        td = self.last_check_timedelta(now)
        return td

    @property
    def time_since_last_check_pretty_print(self):
        """
        :param now:
        :return:
        """
        td = self.time_since_last_check
        if td.seconds > 3600:
            mins = "%.0f minutos" % ((td.seconds % 3600) / 60)
            horas = "%.0f %s" % (td.seconds / 3600, "horas" if td.seconds / 3600 > 1 else "hora")
            return "%s %s" % (horas, mins)
        elif td.seconds > 60:
            return "%.0f minutos" % (td.seconds / 60)
        else:
            return "%.0f segundos" % td.seconds

    class Meta:
        verbose_name = 'RIPE Atlas Probe'
        verbose_name_plural = 'RIPE Atlas Probes'


class RipeAtlasProbeStatusManager(models.Manager):
    def get_timeline(self):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("SELECT date_trunc('day', date), SUM(case when status='Connected' then 1 else 0 end) AS connected , SUM(case when status='Disconnected' then 1 else 0 end) AS disconnected , SUM(case when status='Abandoned' then 1 else 0 end) AS abandoned , SUM(case when status='Never Connected' then 1 else 0 end) AS never " \
                       "FROM simon_app_ripeatlasprobestatus " \
                       "WHERE date > now() - interval '2 months' " \
                       "AND date < now() " \
                       "GROUP BY 1 " \
                       "ORDER BY 1; ")

        return cursor.fetchall()

    def get_cron_frequencies(self):
        from django.db import connection

        cursor = connection.cursor()
        sql = "SELECT date_trunc('day', date), COUNT(*) AS count "\
        "FROM simon_app_ripeatlasprobestatus "\
        "WHERE date > now() - interval '2 months' "\
        "AND date < now() "\
        "AND probe_id = 648 "\
        "GROUP BY 1 "\
        "ORDER BY 1;"

        cursor.execute(sql)

        return cursor.fetchall()

class RipeAtlasProbeStatus(models.Model):
    probe = models.ForeignKey(RipeAtlasProbe)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, null=True)
    objects = RipeAtlasProbeStatusManager()

    def __unicode__(self):
        return self.status

    def isBeingMonitored(self):
        monitored = RipeAtlasMonitoredIds.objects.all().values_list('probe_id', flat=True)
        return self.probe.probe_id in monitored

    def save(self, *args, **kwargs):
        super(RipeAtlasProbeStatus, self).save(*args, **kwargs)


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
            median_rtt=0,
            # it's not possible to combine (unless we merge the samples...) #TODO store the result samples
            number_probes=self.packets_sent + self.packet_loss,
            packet_loss=self.packet_loss + self.packet_loss
        )
        return res

    class Meta:
        verbose_name = 'Resultado RIPE Atlas ICMP Ping'
        verbose_name_plural = 'Resultados RIPE Atlas ICMP Ping'


class RipeAtlasTracerouteResult(RipeAtlasResult):
    pass


class RipeAtlasMeasurement(models.Model):
    measurement_id = models.IntegerField(null=False)
    running = models.BooleanField(default=True)
    type = CharField(max_length=100)


class TestPointManager(models.Manager):
    def get_ipv4(self):
        return TestPoint.objects.exclude(ip_address__contains=':')

    def get_ipv6(self):
        return TestPoint.objects.filter(ip_address__contains=':')


class TestPoint(models.Model):
    description = models.TextField(default='', null=True)
    testtype = models.CharField(max_length=20, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    country = models.CharField(max_length=2, null=True)
    enabled = models.BooleanField(default=False)
    date_created = models.DateTimeField('Date added', default=datetime.now(), null=True)
    url = models.TextField(null=True)
    city = models.CharField(max_length=100, null=True)
    latitude = models.FloatField(default=0.0, null=True)
    longitude = models.FloatField(default=0.0, null=True)
    objects = TestPointManager()

    def __unicode__(self):
        return self.ip_address

    def autnum(self):
        return AS.objects.get_as_by_ip(self.ip_address).asn

    def date_short(self):
        return self.date_created.strftime("%x")

    def make_request(self, protocol="http", timeout=5):
        """

        :param protocol:
        :param timeout:
        :return:
        """

        from requests import get
        from socket import gethostbyaddr

        try:

            if protocol == "https":
                endpoint = gethostbyaddr(self.ip_address)[0]
            else:
                endpoint = self.ip_address

            if ':' in self.ip_address:
                url = "%s://[%s]/" % (protocol, endpoint)
            else:
                url = "%s://%s/" % (protocol, endpoint)

            response = get(url, timeout=timeout)
            if response.status_code != 200:
                return False
            else:
                return True

        except Exception as e:
            print e
            return False

    def check_point(self, protocol="http", save=True, timeout=5):
        """
            Checks and enables / disables the test point
        :return:
        """
        did_fetch = self.make_request(protocol=protocol, timeout=timeout)
        if self.enabled != did_fetch:
            self.enabled = did_fetch
            if save:
                self.save()
        return self.enabled

    class Meta:
        verbose_name = 'Punto de prueba'
        verbose_name_plural = 'Puntos de prueba'


class SpeedtestTestPoint(TestPoint):
    speedtest_url = models.TextField(null=True)
    objects = TestPointManager()

    class Meta:
        verbose_name = 'Punto de prueba de Speedtest.com'
        verbose_name_plural = 'Puntos de prueba de Speedtest.com'


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

    class Meta:
        verbose_name = 'Configuracion'
        verbose_name_plural = 'Configuraciones'


class Params(models.Model):
    config_name = models.TextField()
    config_value = models.TextField()

    def __unicode__(self):
        return self.config_value

    class Meta:
        verbose_name = 'Parametro'
        verbose_name_plural = 'Parametros'


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

    def asyncChart(self, data, divId, labels, colors):
        from django.template import Context
        from django.template.loader import get_template

        t = get_template("panels/async_chart.panel.html")
        ctx = Context({
            'divId': divId,
            'data': data,
            'labels': labels,
            'colors': colors,
            'charts_url': settings.CHARTS_URL
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

        print queryset
        if cc2 is None:
            # one country against the region
            queryset = queryset.filter(
                Q(country_origin=cc1) | Q(country_destination=cc1)
            )
        else:
            # between two countries
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


class RipeAtlasTokenManager(models.Manager):
    # Nada
    pass


class RipeAtlasToken(models.Model):
    token = models.CharField(default='', max_length=100, verbose_name="Token de RIPE Atlas", null=False)
    probe = models.ForeignKey(RipeAtlasProbe, null=True)
    comments = models.TextField(default='', verbose_name="Comentarios", null=True)
    date_added = models.DateTimeField(default=datetime.now())

    objects = RipeAtlasTokenManager()


class RipeAtlasTokenList(models.Model):
    token_list = models.TextField(default='', verbose_name="Lista de Tokens separadas por saltos de linea")
    processed = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=datetime.now())

    def save(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        # if self.token_list is None or self.token_list == "":
        #     return

        token_list = super(RipeAtlasTokenList, self).save(*args, **kwargs)  # Call the "real" save() method.

        # Save all the tokens
        tokens = str(self.token_list).splitlines()
        for token in tokens:
            print token
            rat = RipeAtlasToken(token=token)
            rat.save()
        # Save the processed list
        return token_list


class RipeAtlasMonitoredIds(models.Model):
    probe_id = IntegerField()
    date = models.DateTimeField(default=datetime.now())


class CommentManager(models.Manager):
    pass


class Comment(models.Model):
    person = models.CharField(default="(No especificado)", max_length=200, null=True)
    comment = models.TextField(default='', null=False)
    date = models.DateTimeField(default=datetime.now())
    read = models.BooleanField(default=False)
    objects = CommentManager()

    def __str__(self):
        return "%s: %s" % (self.person, self.comment)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
