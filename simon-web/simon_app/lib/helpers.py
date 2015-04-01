from simon_project import settings
from django.template import RequestContext

#
def simon_processor(request):
    return {
        'APP_VERSION': settings.APP_VERSION,
        'DATE_UPDATED': settings.DATE_UPDATED,
        'URL_PFX': settings.URL_PFX
    }
#

# 
def getContext(request=None):
    
#    c = Context({
#        'MOUNT_POINT': settings.MOUNT_POINT,
#        'URL_PFX': settings.URL_PFX,
#        'APP_VERSION': settings.APP_VERSION,
#        'APP_ENABLED': settings.APP_ENABLED
#    })
    
    c = RequestContext(request, processors=[simon_processor])

#    if request!=None:
#        ip_info = iptoasn(request.META['REMOTE_ADDR'])
#        asn_info = asninfo(ip_info['asn'])
#        c['coninfo'] = contest.lib.addr.getConInfo(request)
#        c['whois_cc'] = ip_info['cc']
#        c['whois_asn'] = ip_info['asn']
#        c['whois_org'] = asn_info['org']
#        c['isLogged'] = contest.lib.login.isLogged(request)
#        c['session'] = request.session
#        c['msg'] = 'None'
    
    return c;
#