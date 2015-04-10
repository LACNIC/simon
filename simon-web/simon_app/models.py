from django.db.models import Q
from django.db import models, connection
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from datetime import datetime, timedelta
import trparse
import simon_project.settings as settings


class Region(models.Model):
    name = models.CharField(max_length=80)
    numcode = models.IntegerField(null=True)

    def __unicode__(self):
        return self.printable_name


class CountryManager(models.Manager):
    def get_region_countries(self):
        return Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3))

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
        # 		cc_without_testpoints = Country.objects.get_countries_with_no_testpoints().values_list('iso', flat=True)
        # 		cc_without = list(set(cc_all) - set(set(cc_without_testpoints)) - set(cc_with))
        # 		n  = len(cc_without)

        # in case i'm asking for more than i can
        # 		if amount > n:
        # 			amount = n

        # 		if n > 0:
        # 			print 'without'
        # 			return cc_without[:amount]

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
        #if(tag == 'local_country'):
        #    self.country_origin = text
        if (tag == 'destination_ip'):
            self.ip_destination = text
        if (tag == 'testtype'):
            self.testype = text
        #		if(tag == 'number_probes'):
        #			self.number_probes = text
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
# 				return autsys

class AS(models.Model):
    asn = models.IntegerField()
    network = models.GenericIPAddressField()
    pfx_length = models.IntegerField()
    objects = ASManager()

    def __unicode__(self):
        return "ASN %s" % (self.asn)


from itertools import chain


class ResultsManager(models.Manager):
    def get_weekly_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(7))

    def get_daily_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(1))

    def get_hourly_results(self):
        return Results.objects.filter(date_test__gt=datetime.now() - timedelta(1.0 / 24))

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
        # 		return Results.objects.filter(Q(as_destination__asn=asn_origin) & Q(as_origin__asn=asn_destination))

        res = []
        for as_origin in AS.objects.filter(asn=asn_origin):  # asns list
            for as_destination in AS.objects.filter(asn=asn_destination):  # asns list
                if Results.objects.filter(
                                Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)).count() > 0:
                    res.extend(
                        Results.objects.filter(Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)))
        return res

    def get_results_by_as(self, as_number):
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
        #if(tag == 'version'):
        #    self.version = text
        #if(tag == 'local_country'):
        #    self.country_origin = text
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


class TracerouteResult(Results):
    output = models.TextField(max_length=2000, default='')

    def pretty_print(self):
        import geoip2

        reader = geoip2.database.Reader("%s/%s" % (settings.STATIC_ROOT, "geolocation/GeoLite2-City.mmdb"))

        tr = self.parse()
        res = str(reader.city(self.ip_origin).country.iso_code)
        for h in tr.hops:
            rtts = []
            ip = ""
            for p in h.probes:
                if p.rtt is None: continue
                if p.ip is None: continue
                ip = p.ip
                rtts.append(float(p.rtt))

            if ip is None:
                cc = "? "
            else:
                cc = reader.city(ip).country.iso_code

            flecha = " --%.1f--> " % (sum(rtts) / len(rtts))
            res = "%s%s%s" % (res, flecha, cc)

        return res

    def parse(self):
        return trparse.loads(self.output)


# class WebResult(Results):
# url = models.CharField(max_length=2000, default='')

class TestPointManager(models.Manager):
    def get_ipv4(self):
        cursor = connection.cursor()
        return TestPoint.objects.exclude(ip_address__contains=':')

    def get_ipv6(self):
        cursor = connection.cursor()
        return TestPoint.objects.filter(ip_address__contains=':')


class TestPoint(models.Model):
    #testpointid is automatically inserted as Django identifier
    description = models.TextField()
    testtype = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=2)
    enabled = models.BooleanField(default=False)
    date_created = models.DateTimeField('test date')
    url = models.TextField(null=True)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
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
