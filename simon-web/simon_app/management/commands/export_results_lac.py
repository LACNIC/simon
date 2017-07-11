import pytz
from _export_results import export
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, ProbeApiPingResult, Results


class Command(BaseCommand):
    """
        Command to export LAC Region Connectivity results to the world
        """

    def handle(self, *args, **options):
        comments = []

        ccs = Country.objects.get_lacnic_countrycodes()
        start = datetime(year=2016, month=01, day=01)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )
        export(sms, 'results-lac-connectivity')  # .json

        js = Results.objects.javascript().filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )
        export(js, 'results-lac-connectivity-js')  # .json
