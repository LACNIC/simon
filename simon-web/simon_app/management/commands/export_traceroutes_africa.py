import datetime
import pytz
from _export_traces import export_traces
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import Country, TracerouteResult, TracerouteHop
from simon_app.decorators import timed_command, mem_comsumption

from optparse import make_option
from cProfile import Profile


class Command(BaseCommand):
    """
        Command to export Africa Connectivity traceroutes to the world
    """

    command = "Export Traces AFRICA"

    option_list = BaseCommand.option_list + (
        make_option('--profile',
                    default=False,
                    help='Show cProfile information'),
    )

    def handle(self, *args, **options):
        """
            Dummy handle... chooses to profile or not to profile
        :param args:
        :param options:
        :return:
        """

        if options.get('profile', False):
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)
            profiler.print_stats()
        else:
            self._handle(*args, **options)

    # @timed_command(name=command)
    # @mem_comsumption(name=command)
    def _handle(self, *args, **options):
        comments = []

        ccs = Country.objects.get_afrinic_countrycodes()
        start = datetime(year=2017, month=03, day=21)

        trs = TracerouteResult.objects.filter(
            Q(country_destination__in=ccs) & Q(country_origin__in=ccs)
        ).filter(
            traceroutehop__date_test__gt=start
        ).values_list('pk', flat=True)

        export_traces(trs, 'results-africa-connectivity-traces', pks=set(trs))

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

