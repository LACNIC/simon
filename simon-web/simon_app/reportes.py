# -*- coding: utf-8 -*-

#File that defines the non-persistent classes
from __future__ import division
import doctest

# import django_tables as tables
from django import forms
from simon_app.models import Country, Results, ThroughputResults, Images
#date picker
from django.contrib.admin import widgets
from django.forms.fields import ChoiceField
from datetime import tzinfo, timedelta
from django.db.models import Q


# class ResultsTable(tables.MemoryTable):
# 	#date_test = tables.Column(verbose_name="Test date")
# 	#version = tables.Column(verbose_name="Version")
# 	#ip_origin = tables.Column(verbose_name="Origin IP")
# 	#ip_destination = tables.Column(verbose_name="Destination IP")
# 	#testype = tablesao.Column(verbose_name="Test type")
# 	#Number of probes to a specific country
# 	number_probes = tables.Column(verbose_name="Number of probes", name="num_probes", data="num_probes")
# 	min_rtt = tables.Column(verbose_name="Min. RTT (ms)", name="min_rtt", data="min_rtt")
# 	max_rtt = tables.Column(verbose_name="Max. RTT (ms)", name="max_rtt", data="max_rtt")
# 	ave_rtt = tables.Column(verbose_name="Avge. RTT (ms)", name="ave_rtt", data="ave_rtt")
# 	dev_rtt = tables.Column(verbose_name="RTT Deviation (ms)", name="dev_rtt", data="dev_rtt")
# 	median_rtt = tables.Column(verbose_name="Avge. Median RTT (ms)", name="median_rtt", data="median_rtt")
# 	packet_loss = tables.Column(verbose_name="Packet loss", name="packet_loss", data="packet_loss")
# 
# 	country_destination = tables.Column(verbose_name="Destination country (code)", name="country_destination", data="country_destination")
# 	#Fields that appear on advanced search results
# 	ip_version = tables.Column(verbose_name="IP version", visible=False, name="ip_version", data="ip_version")
# 	tester = tables.Column(verbose_name="Tester name", visible=False, name="tester", data="tester")
# 	tester_version = tables.Column(verbose_name="Tester version", visible=False, name="tester_version", data="tester_version")
# 
# 	def __unicode__(self):
# 		return self.ip_origin
# 	
# class ThroughputResultsTable(tables.MemoryTable):
# 	time = tables.Column(verbose_name="Avge. time (ms)", visible=False, name="ave_time", data="ave_time")
# 	size = tables.Column(verbose_name="Avge. size (Bytes)", visible=False, name="ave_size", data="ave_size")
# 	number_probes = tables.Column(verbose_name="Number of probes", name="number_probes", data="number_probes")
# 	ave_thput = tables.Column(verbose_name="Avge. Throughput", name="ave_thput", data="ave_thput")
# 	std_dev = tables.Column(verbose_name="Std. Deviation", name="std_dev", data="std_dev")
# 	country_destination = tables.Column(verbose_name="Destination country (code)", name="country_destination", data="country_destination")
# 	#Fields that appear on advanced search results
# 	ip_version = tables.Column(verbose_name="IP version", visible=False, name="ip_version", data="ip_version")
# 	tester = tables.Column(verbose_name="Tester name", visible=False, name="tester", data="tester")
# 	tester_version = tables.Column(verbose_name="Tester version", visible=False, name="tester_version", data="tester_version")
# 	
# 	def __unicode__(self):
# 		return self.country_destination
	
import datetime
import re
class ResultsForm(forms.Form):
	countries = Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).values('iso', 'printable_name').order_by('printable_name')
	countries_list = []

	for country in countries:
		register = []
		register.append(country['iso'])
		register.append(country['printable_name'])
		countries_list.append(register)
	countries = ChoiceField(countries_list, label='País')
	
	testers_list = []
	testers_rs = Results.objects.all().distinct().values_list('tester', 'tester_version')
	for tester in testers_rs:
		register = []
		tester_name = str(tester[0])
		tester_version = re.sub('\s', '', str(tester[1]))
		
		if tester_name != "" and tester_version != "":
			tester_print_name = tester_name + " v" + tester_version
			tester_value = str(tester_name + "/" + tester_version)
			register.append(tester_value)
			register.append(tester_print_name)
			testers_list.append(register)
	tester = ChoiceField(testers_list, label='Medidor')
	
	#test_type = forms.ModelChoiceField(queryset=Results.objects.all().values_list('testype', flat=True).distinct(), label='Test type', initial='')
	ip_version = forms.ModelChoiceField(queryset=Results.objects.all().values_list('ip_version', flat=True).distinct(), label='Versión de protocolo IP', initial='')
	
	oldest_year = Results.objects.all().order_by('date_test').values_list('date_test', flat=True).distinct()[0].year
	current_year = datetime.datetime.now().year
	year = forms.ChoiceField(choices=((str(x), x) for x in range(int(oldest_year), int(current_year) + 1)), label='Año desde')
	month = forms.ChoiceField(choices=((str(x), x) for x in range(1, 12 + 1)), label='Mes desde')
	
class ThroughputResultsForm(forms.Form):
	countries = Country.objects.all().values('iso', 'printable_name').order_by('printable_name')
	countries_list = []

	for country in countries:
		register = []
		register.append(country['iso'])
		register.append(country['printable_name'])
		countries_list.append(register)
	countries = ChoiceField(countries_list, label='Country')
	
	testers_list = []
	testers_rs = ThroughputResults.objects.all().distinct().values_list('tester', 'tester_version')
	for tester in testers_rs:
		register = []
		tester_name = str(tester[0])
		tester_version = re.sub('\s', '', str(tester[1]))
		
		if tester_name != "" and tester_version != "":
			tester_print_name = tester_name + " v" + tester_version
			tester_value = str(tester_name + "/" + tester_version)
			register.append(tester_value)
			register.append(tester_print_name)
			testers_list.append(register)
	tester = ChoiceField(testers_list, label='Tester')
	
	#test_type = forms.ModelChoiceField(queryset=ThroughputResults.objects.all().values_list('testype', flat=True).distinct(), label='Test type', initial='')
	ip_version = forms.ModelChoiceField(queryset=ThroughputResults.objects.all().values_list('ip_version', flat=True).distinct(), label='IP version', initial='')
	
	oldest_year = ThroughputResults.objects.all().order_by('date_test').values_list('date_test', flat=True).distinct()# [0].year
	oldest_year = 2012
	current_year = datetime.datetime.now().year
	year = forms.ChoiceField(choices=((str(x), x) for x in range(int(oldest_year), int(current_year) + 1)), label='Year since')
	month = forms.ChoiceField(choices=((str(x), x) for x in range(1, 12 + 1)), label='Month since')

class MyImageModelMultipleChoiceField(forms.ModelMultipleChoiceField):
	def label_from_instance(self, obj):
		return "%s Bytes" % (obj.size)
class MyCountryModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return "%s" % (obj.printable_name)
class AddNewWebPointForm(forms.Form):
	organization = forms.CharField(label = 'Nombre de la Organización')
	email = forms.EmailField(label = 'Correo de contacto')
	country = MyCountryModelChoiceField(queryset=Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)), widget=forms.Select(), label='País donde está el servidor')
	server_url = forms.URLField(label='Server URL', initial='www.')
	images_path = forms.CharField(label='Path hasta el directorio de las imagenes', initial='/simon')
	
	db_images = Images.objects.all()
#	images = MyImageModelMultipleChoiceField(queryset=db_images, widget=forms.CheckboxSelectMultiple(), label='Select the images to serve (size in Bytes)', initial=[image for image in db_images])
#	images = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))

#	description = forms.CharField(widget=forms.Textarea)

	bandwidth = forms.CharField(label='Ancho de Banda de subida')
	BANDWIDTHS = [
#				('14 Kbps', '14 Kbps'),
#				('56 Kbps', '56 Kbps'),
#				('64 Kbps', '64 Kbps'),
#				('128 Kbps', '128 Kbps'),
#				('256 Kbps', '256 Kbps'),
#				('512 Kbps', '512 Kbps'),
				('1 Mbps', '1 Mbps'),
				('2 Mbps', '2 Mbps'),
				('4 Mbps', '4 Mbps'),
				('8 Mbps', '8 Mbps'),
				('16 Mbps', '16 Mbps'),
				('30 Mbps', '30 Mbps'),
				('45 Mbps', '45 Mbps'),
				('60 Mbps', '60 Mbps'),
				('100 Mbps', '100 Mbps'),
				('1 Gbps', '1 Gbps'),
				]
	UNITS = [
			('Mbps', 'Mbps'),
			('Gbps', 'Gbps')]
	unit = forms.ChoiceField(choices=UNITS, label='Unidad del ancho de banda')
	
class AddNewNtpPointForm(forms.Form):
	organization = forms.CharField(label = 'Nombre de la Organización')
	email = forms.EmailField(label = 'Correo de contacto')
	country = MyCountryModelChoiceField(queryset=Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)), widget=forms.Select(), label='País donde está el servidor')
	server_url = forms.CharField(label='Server URL')
#	images_path = forms.CharField(label='Path to the images directory')

class CountryDropdownForm(forms.Form):
	country = MyCountryModelChoiceField(queryset=Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name'), widget=forms.Select(), label='País que desea inspeccionar la latencia', empty_label=None)

class GMTUY(tzinfo):
	def utcoffset(self, dt):
		return timedelta(hours=-3)
	def tzname(self, dt):
		return "GMT -3: Uruguay"
	def dst(self, dt):
		return timedelta(0)
	
class UploadFileForm(forms.Form):
	file = forms.FileField(label="Archivo con logs de traceroute", required=False)

class YearField(forms.ChoiceField):
	year = range(2009, datetime.datetime.now().year + 1)
	
class ReportForm(forms.Form):
	country = MyCountryModelChoiceField(queryset=Country.objects.filter(Q(region_id=1) | Q(region_id=2) | Q(region_id=3)).order_by('printable_name'), widget=forms.Select(), label='País que desea inspeccionar la latencia', empty_label=None)
	years = range(2009, datetime.datetime.now().year + 1)
	year = forms.ChoiceField(choices = zip(years, years))
	