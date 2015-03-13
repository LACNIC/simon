# -*- encoding: utf-8 -*-

from django.http import HttpResponse
from models import IpRequestQuery
import datetime

def get_ip(request, return_type='json', jsonpcallback=''):
    ip = request.META.get('REMOTE_ADDR')
    
    ipRequest = IpRequestQuery()
    ipRequest.ip_address = ip
    ipRequest.date_request = datetime.datetime.now()
    ipRequest.save()
    
    if return_type == 'json':
        response = "{ \"ip\": \""+ ip +"\" }"
        return HttpResponse(response, content_type="application/json")
    
    if return_type == 'xml':
        response = "<?xml version=\"1.0\"?>\n"
        response += "<ip>"+ ip +"</ip>"
        return HttpResponse(response, content_type="application/xml")
    
    if return_type == 'text':
        return HttpResponse(ip, content_type="text/plain")
    
    if return_type == 'jsonp':
        if request.GET.get('callback') != None: jsonpcallback = request.GET.get('callback')
        response = jsonpcallback + "({ \"ip\": \""+ ip +"\" })"
        return HttpResponse(response, content_type="application/json")