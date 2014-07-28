from django.db import models, connection
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey


class Region(models.Model):
	name = models.CharField(max_length=80)
	numcode = models.IntegerField(null=True)
	
	def __unicode__(self):
		return self.printable_name
	
class Country(models.Model):
	iso = models.CharField(max_length=2)
	name = models.CharField(max_length=80)
	printable_name = models.CharField(max_length=80)
	iso3 = models.CharField(max_length=3, null=True, blank=True)
	numcode = models.IntegerField(null=True)
	region = models.ForeignKey(Region)
	
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
	enabled = models.BooleanField()
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
	online = models.BooleanField()
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
