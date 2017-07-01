import pytz
from _export_results import export
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, ProbeApiPingResult


class Command(BaseCommand):
    """
    Command to export Africa Connectivity results to the world
    """

    def handle(self, *args, **options):
        comments = []

        now = datetime.now().replace(second=0, microsecond=0)
        uy = pytz.timezone('America/Montevideo')
        now = uy.localize(now)
        comments.append(["# Data exported at %s (%s)." % (now, now.tzinfo)])

        ccs = Country.objects.get_afrinic_countrycodes()
        start = datetime(year=2017, month=03, day=21)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )

        export(sms, 'results-africa-connectivity')  # .json