from django.db.models import Q
from django.db import models, connection
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from netaddr import IPAddress, IPNetwork
from datetime import datetime

class Region(models.Model):
	name = models.CharField(max_length=80)
	numcode = models.IntegerField(null=True)
	
	def __unicode__(self):
		return self.printable_name

class CountryManager(models.Manager):
	# TERMINAR
	"""
	
	"""
	def get_with_points(self):
		return Country.objects.raw('SELECT * FROM simon_app_country WHERE iso IN (SELECT country\
																				  FROM simon_app_testpoint\
																				  GROUP BY country; )\
									ORDER BY RAND() LIMIT 1 ')
	
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
		#if(tag == 'version'):
		#    self.version = text
		#if(tag == 'local_country'):
		#    self.country_origin = text
		if(tag == 'destination_ip'):
			self.ip_destination = text
		if(tag == 'testtype'):
			self.testype = text
#		if(tag == 'number_probes'):
#			self.number_probes = text
		if(tag == 'size'):
			self.size = text
		if(tag == 'time'):
			self.time = text
		if(tag == 'ip_version'):
			self.ip_version = text
		if(tag == 'tester'):
			self.tester = text
		if(tag == 'tester_version'):
			self.tester_version = text

class ASManager(models.Manager):
	
	def get_as_by_ip(self, ip_address):
		try:
			return AS.objects.raw('SELECT * FROM simon_app_as where network >>= inet \'%s\' ORDER BY pfx_length DESC LIMIT 1' % ip_address)[0]
		except IndexError:
			return AS.objects.get(id=1)# 0.0.0.0/0
# 		for autsys in AS.objects.order_by('-pfx_length'):
# 			if IPAddress(ip_address) in IPNetwork(autsys.network):
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
	
	def get_results_by_as_origin(self, as_number):
		res = []
		for asn in AS.objects.filter(asn=as_number):# asns list
			res.append(Results.objects.filter(as_origin_id=asn.id))
		return res
	
	def get_results_by_as_destination(self, as_number):
		res = []
		for asn in AS.objects.filter(asn=as_number):# asns list
			res.append(Results.objects.filter(as_destination_id=asn.id))
		return res
	
	def get_results_by_as_origin_and_destination(self, asn_origin, asn_destination):
# 		return Results.objects.filter(Q(as_destination__asn=asn_origin) & Q(as_origin__asn=asn_destination))
	
		res = []
		for as_origin in AS.objects.filter(asn=asn_origin):# asns list
			for as_destination in AS.objects.filter(asn=asn_destination):# asns list
				if Results.objects.filter(Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)).count() > 0:
					res.extend(Results.objects.filter(Q(as_destination_id=as_origin.id) & Q(as_origin_id=as_destination.id)))
		return res
	
	def get_results_by_as(self, as_number):
		return list(chain(self.get_results_by_as_origin(as_number), self.get_results_by_as_destination(as_number)))
	
class Results(models.Model):
	#id is automatically inserted as Django identifier
	date_test = models.DateTimeField('test date')
	version = models.IntegerField(null=True)
	ip_origin = models.GenericIPAddressField()
	ip_destination = models.GenericIPAddressField()
	testype = models.CharField(max_length=20)
	number_probes = models.IntegerField(null=True)
	min_rtt = models.IntegerField(null=True)
	max_rtt = models.IntegerField(null=True)
	ave_rtt = models.IntegerField(null=True)
	dev_rtt = models.IntegerField(null=True)
	median_rtt = models.IntegerField(null=True)
	packet_loss = models.IntegerField(null=True)
	country_origin = models.CharField(max_length=2)
	country_destination = models.CharField(max_length=2)
	ip_version = models.IntegerField()
	tester = models.CharField(max_length=20)
	tester_version = models.CharField(max_length=10)
	as_origin = models.ForeignKey(AS, related_name='as_origin', default=0)
	as_destination = models.ForeignKey(AS, related_name='as_destination', default=0)
	user_agent = models.CharField(max_length=200, default='')
	url = models.CharField(max_length=2000, default='')
	objects = ResultsManager()
	
	
	def __unicode__(self):
		return "%s -> %s | %s/%s/%s/%s | %s | %s v.%s" % (self.country_origin, self.country_destination, self.min_rtt, self.ave_rtt, self.max_rtt, self.dev_rtt, self.date_test.strftime('%d/%m/%Y %H:%M'), self.tester, self.tester_version)
	
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
		if(tag == 'destination_ip'):
			self.ip_destination = text
		if(tag == 'origin_ip'):
			self.ip_origin = text
		if(tag == 'testtype'):
			self.testype = text
		if(tag == 'number_probes'):
			self.number_probes = text
		if(tag == 'min_rtt'):
			self.min_rtt = text
		if(tag == 'max_rtt'):
			self.max_rtt = text
		if(tag == 'ave_rtt'):
			self.ave_rtt = text
		if(tag == 'dev_rtt'):
			self.dev_rtt = text
		if(tag == 'median_rtt'):
			self.median_rtt = text
		if(tag == 'packet_loss'):
			self.packet_loss = text
		if(tag == 'median_rtt'):
			self.median_rtt = text
		if(tag == 'ip_version'):
			self.ip_version = text
		if(tag == 'tester'):
			self.tester = text
		if(tag == 'tester_version'):
			self.tester_version = text

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
	size = models.IntegerField(null=True) # Bytes size
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