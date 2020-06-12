from simon_project import settings
from simon_app.models.models import Results
from django.template import *
from simon_app.forms import FeedbackForm


def simon_processor(request):
    return {
        'APP_VERSION': settings.APP_VERSION,
        'DATE_UPDATED': settings.DATE_UPDATED,
        'LATEST_COMMIT': settings.LATEST_COMMIT,
        'HOURLY': len(Results.objects.get_hourly_results()),
        'DAILY': len(Results.objects.get_daily_results()),
        'WEEKLY': len(Results.objects.get_weekly_results()),
        'feedbackform': FeedbackForm(),
        'CHARTS_URL': settings.CHARTS_URL
    }


def getContext(request=None):
    return {}
    # return RequestContext(request)
