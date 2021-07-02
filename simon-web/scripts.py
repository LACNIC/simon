#!/usr/bin/python

from __future__ import print_function
from __future__ import absolute_import
import os
from .simon_app.functions import whoIs
from .simon_app.models import TestPoint, Results, Country
from geopy import geocoders
from __future__ import division #float division
import math
os.environ['DJANGO_SETTINGS_MODULE'] = "simon_project.settings"
from xml.dom.minidom import parseString
from time import gmtime, strftime
from urlparse import urlparse
from netaddr import IPAddress, IPNetwork, AddrFormatError
import socket
from . import simon_project.settings as settings
from urllib2 import urlopen
from lxml import etree

def db_cleaning():
	"""
	Script that cleans the Results table with the following criteria
		- remove negative results
		- remove high-end and low-end results (above or below 2 sigma)
	"""
	
	test_points = TestPoint.objects.all()
	deleted_registers = 0
	for test_point in test_points:
		test_point_results = Results.objects.filter(ip_destination = test_point.ip_address).values('ave_rtt', 'number_probes', 'dev_rtt')
		count = sum(test_point_results.values_list('number_probes',flat=True))
		test_point_avg = 0 #Grand Mean
		test_point_dev = 0 #overall Standard Deviation
		essg = [] #Group Error Sum of Squares
		
		#Grand Mean calculation
		for result in test_point_results:
			avg = result['ave_rtt']
			num_probes = result['number_probes']
			dev = result['dev_rtt']
					
			test_point_avg += (avg * num_probes) / count		
			
			essg.append(pow(dev, 2) * (num_probes - 1))
		ess = sum(essg)
		
		#Once the Grand Mean is calculated we proceed to calculate the overall Standard Deviation
		#http://www.burtonsys.com/climate/composite_standard_deviations.html
		gss = [] #Group Sum of Squares
		for result in test_point_results:
			avg = result['ave_rtt']
			num_probes = result['number_probes']
			
			gss.append( pow((avg - test_point_avg), 2) * num_probes )
			
		tgss = sum(gss) #Total Group Sum of Squares
		gv = (ess + tgss) / (count - 1) #Grand Variance
		test_point_dev = math.sqrt(gv)
		
		#With Average and Standard Deviation the results can be cleaned...
		
		test_point_results = Results.objects.filter(ip_destination = test_point.ip_address)
		for result in test_point_results:
			max = result.max_rtt
			min = result.min_rtt
			avg = result.ave_rtt
			RADIUS = 2*test_point_dev
			
			#Delete non-positive results
			if avg < 0:
				result.delete()
			
			#Delete high-end or low-end registers
			if max < (test_point_avg - RADIUS):
				result.delete()
				deleted_registers += 1
			if min > (test_point_avg + RADIUS):
				result.delete()
				deleted_registers += 1
	
	print(str(deleted_registers)+' registers deleted')

def write_web_testpoints():
	"""
	Script that reads the speedtest.net's servers XML file and writes the TestPoints in the database
	LACNIC
	May 2014
	"""
	
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	
	
	#Read the XML XMLfile
	XMLfile = urlopen('http://www.speedtest.net/speedtest-servers.php')
	data = XMLfile.read()
	XMLfile.close()
	timeFormat = "%Y-%m-%d %H:%M:%S"
	
	
	#Add new registers in the Test Points table
	servers = etree.fromstring(str(data))[0]
	for server in servers:
		#Get the IP address and match it against LACNIC resources
		long_url = server.get('url')
		url = urlparse(long_url)[1]
# 		print str(long_url)
		
		country = server.get('cc').upper()
		city = server.get('name')
		latitude = server.get('lat')
		longitude = server.get('lon')
		description = server.get('sponsor')
		testtype = 'tcp_web'
		enabled = True
		date_created = strftime(timeFormat, gmtime())
		
		try:
			#could be done with DNSpython
			ok = False
			nuevos = []
			
			for ip_address in socket.getaddrinfo(url, 80, 0, 0, socket.SOL_TCP):
				ip_address = IPAddress(ip_address[4][0])
				
				try:
					TestPoint.objects.get(ip_address=str(ip_address))
				except TestPoint.DoesNotExist:
					# Si es nuevo...
					
					if ip_address.version == 4:
						for resource in settings.v4resources:
							if ip_address in IPNetwork(resource):
								ok = True
					elif ip_address.version == 6:
						for resource in settings.v6resources:
							if ip_address in IPNetwork(resource):
								ok = True
					if ok is True:
						tp = TestPoint(description=description, testtype=testtype, ip_address=str(ip_address), country=country, enabled=enabled, date_created=date_created, url=long_url, city=city, latitude=latitude, longitude=longitude)
						print(OKGREEN + str(ip_address) + ENDC)
						tp.save()
						nuevos.append(tp)
					else:
						print("%s" % str(ip_address))
			if len(nuevos) > 0:
				print("The following Test Points have been added:")
			for tp in nuevos:
				print(OKGREEN + str(tp.ip_address) + ENDC)
		
		#DNS and IP format exceptions
		except NXDOMAIN:
			print('The query name does not exist. URL: ' + url)
		except AddrFormatError:
			print('Address Format Error')
		except socket.gaierror:
			print("No address associated with hostname")



os.environ['DJANGO_SETTINGS_MODULE'] = "simon_project.settings"

def city_to_testpoint():
	"""
		Script that inserts corresponding city to the different ip addresses in testpoint table.
		Done to avoid delays when loading charts 
	"""
	for ip_address in TestPoint.objects.all().values_list('ip_address', flat=True):
		print(' Processing %s' % ip_address)
		try:
			city = whoIs(ip_address)['entities'][0]['vcardArray'][1][2][3][3]
			testpoint = TestPoint.objects.get(ip_address=ip_address)
			testpoint.city = city
			testpoint.save()
		except TypeError:
			print('Error when getting %s city.' % ip_address)

def city_to_testpoint2():
	for t in TestPoint.objects.all():
		print(' Processing ') 
		try:
			city = whoIs(t.ip_address)['entities'][0]['vcardArray'][1][2][3][3]
			t.city = city
			t.save()
		except TypeError:
			print('Error when getting %s city.' % t.ip_address)

def city2latLong():
	"""
	Saves latitude and Longitude to each test point
	"""
	g = geocoders.GoogleV3()
	for tp in TestPoint.objects.all():
		if tp.latitude is None and tp.longitude is None:
			try:
				place, (lat, lng) = g.geocode("%s, %s" % (str(tp.city), str(tp.description)))
				tp.latitude = lat
				tp.longitude = lng
				tp.save()
			except UnicodeEncodeError:
				print('Error unicode')
			except TypeError:
				print('Type error')

def rtts():
	from datetime import datetime
	f = open('/Users/agustin/Dropbox/LACNIC/simon/stats/mediciones/cableado/tcp', 'r')
	lines = f.readlines()
	f.close()
	
	anterior = datetime.strptime("16 May 2014", "%d %b %Y")
	for line in lines:
		time = datetime.strptime(line.split(' ')[0], "%H:%M:%S.%f")
		delta = time - anterior
		print(delta.microseconds / 1000)
		anterior = time

def clean():
	f = open('/Users/agustin/Dropbox/LACNIC/simon/stats/mediciones/cableado/tcp2', 'r')
	lines = f.readlines()
	f.close()
	for line in lines:
		rtt = float(line)
		if rtt < 500 and rtt > 100:
			print(rtt)

# rtts()
clean()