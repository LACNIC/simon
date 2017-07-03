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

        ccs = Country.objects.get_afrinic_countrycodes()
        start = datetime(year=2017, month=03, day=21)

        trs = TracerouteResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            traceroutehop__date_test__gt=start
        )

        export_traces(trs, 'results-africa-connectivity-traces')

        # top 28
        top28 = ['jumia.com.ng', 'konga.com', 'bidorbuy.co.za', 'fnb.co.za', 'gtbank.com', 'absa.co.za',
                 'standardbank.co.za', 'almasryalyoum.com', 'elkhabar.com', 'vanguardngr.com', 'news24.com',
                 'punchng.com', 'iol.co.za', 'ghanaweb.com', 'nairaland.com', 'supersport.com', 'alwafd.org',
                 'iroking.com']

        # TODO Django is not properly working with reverse filters

        # trs_top28 = TracerouteResult.objects.filter(
        #     country_origin__in=ccs
        # ).filter(
        #     # traceroutehop__url__in=top28
        # ).filter(
        #     traceroutehop__date_test__gt=start
        # )

        hops = TracerouteHop.objects.filter(
            url__in=top28
        )
        trs_top28 = [t.traceroute_result for t in hops]

        export_traces(trs_top28, 'results-africa-connectivity-traces-top28')

