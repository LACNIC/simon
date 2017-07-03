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

        ccs = Country.objects.get_afrinic_countrycodes()
        start = datetime(year=2017, month=03, day=21)

        sms = ProbeApiPingResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start
        )

        export(sms, 'results-africa-connectivity')  # .json

        # top 28
        top28 = ['jumia.com.ng', 'konga.com', 'bidorbuy.co.za', 'fnb.co.za', 'gtbank.com', 'absa.co.za',
                 'standardbank.co.za', 'almasryalyoum.com', 'elkhabar.com', 'vanguardngr.com', 'news24.com',
                 'punchng.com', 'iol.co.za', 'ghanaweb.com', 'nairaland.com', 'supersport.com', 'alwafd.org',
                 'iroking.com']

        trs_top28 = ProbeApiPingResult.objects.filter(
            Q(country_origin__in=ccs) & Q(url__in=top28)
        ).filter(
            date_test__gte=start
        )

        export(trs_top28, 'results-africa-connectivity-top28')
