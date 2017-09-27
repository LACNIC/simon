import datetime
import pytz
from _export_traces import export_traces
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, TracerouteResult, TracerouteHop
from simon_app.decorators import timed_command, mem_comsumption

class Command(BaseCommand):
    """
        Command to export LACNIC Connectivity traceroutes to the world
    """

    command = "Exporte Traceroutes LACNIC"

    @timed_command(name=command)
    @mem_comsumption(name=command)
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
