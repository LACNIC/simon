import pytz
from _export_results import export
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, ProbeApiPingResult, Results
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):
    """
        Command to export LAC Region Connectivity results to the world
        """

    command = "Export Results LAC"

    # @timed_command(name=command)
    # @mem_comsumption(name=command)
    def handle(self, *args, **options):
        comments = []

        ccs = Country.objects.get_lacnic_countrycodes()
        start = datetime(year=2016, month=01, day=01)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        ).values_list('pk', flat=True)
        export([], 'results-lac-connectivity', pks=set(sms))  # .json

        js = Results.objects.javascript().filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )  # .values_list('pk', flat=True)  # can't do pks yet
        export(js, 'results-lac-connectivity-js')  # .json

        # Results for 2015
        start = datetime(year=2015, month=01, day=01)
        end = datetime(year=2016, month=12, day=31)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start,
            date_test__lte=end
        ).values_list('pk', flat=True)
        export([], 'results-lac-connectivity-2015', pks=set(sms))  # .json
