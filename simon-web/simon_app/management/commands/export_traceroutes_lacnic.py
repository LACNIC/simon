import datetime
import pytz
from _export_traces import export_traces
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, TracerouteResult, TracerouteHop


class Command(BaseCommand):
    """
    Command to export Africa Connectivity traceroutes to the world
    """

    def handle(self, *args, **options):
        comments = []

        ccs = Country.objects.get_lacnic_countrycodes()
        start = datetime(year=2016, month=01, day=01)

        trs = TracerouteResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            traceroutehop__date_test__gt=start
        )

        export_traces(trs, 'results-lacnic-connectivity-traces')
