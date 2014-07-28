from django.core.management.base import BaseCommand
import datetime
from simon_app.functions import *
from simon_app.models import Results

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        with open(args[0]) as f:
            
            country_origin = ""
            
            for line in f.readlines():
                
                origin = line.split()[0]
                destination = line.split()[1]
                
                if country_origin == "" : country_origin = whoIs(origin)['country']

                rtt = int(float(line.split()[2]))
                time = datetime.datetime.fromtimestamp(int(line.split()[3]))
                
                if inLACNICResources(origin) and inLACNICResources(destination):
                    country_destination = whoIs(destination)['country']
                    res = Results(\
                                  date_test=time,\
                                  version=0,\
                                  ip_origin=origin,\
                                  ip_destination=destination,\
                                  testype="traceroute",\
                                  number_probes=1,\
                                  min_rtt=rtt,\
                                  max_rtt=rtt,\
                                  ave_rtt=rtt,\
                                  dev_rtt=rtt,\
                                  median_rtt=rtt,\
                                  packet_loss=0,\
                                  country_origin=country_origin,\
                                  country_destination=country_destination,\
                                  ip_version=4,\
                                  tester="caida",\
                                  tester_version=1\
                                  )
                    res.save()