from simon_project import settings
from simon_app.models import *
from django.template import RequestContext
from simon_app.forms import *

#
def simon_processor(request):

    # print "Referer: %s" % request.META['HTTP_REFERER']

    return {
        'APP_VERSION': settings.APP_VERSION,
        'DATE_UPDATED': settings.DATE_UPDATED,
        'URL_PFX': settings.URL_PFX,
        'HOURLY' : len(Results.objects.get_hourly_results()),
        'DAILY' : len(Results.objects.get_daily_results()),
        'WEEKLY' : len(Results.objects.get_weekly_results()),
        'feedbackform' : FeedbackForm(),
        'CHARTS_URL' : settings.CHARTS_URL
    }
#

# 
def getContext(request=None):

    return RequestContext(request, processors=[simon_processor])