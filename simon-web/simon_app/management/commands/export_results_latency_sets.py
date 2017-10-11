from _export_results import export
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from simon_app.models import ProbeApiPingResult
from simon_app.decorators import timed_command, mem_comsumption


class Command(BaseCommand):
    """
        Command to export LAC Region Connectivity results to the world
        """

    command = "Export Results Latency Sets LACNIC"

    @timed_command(name=command)
    @mem_comsumption(name=command)
    def handle(self, *args, **options):

        ccs = ["UY", "PE"]
        tps = ["uy-mvd-as28000.anchors.atlas.ripe.net", "191.240.3.46", "187.157.254.5"]

        start = datetime(year=2017, month=10, day=11)
        sms = ProbeApiPingResult.objects.filter(
            Q(country_origin__in=ccs)
        ).filter(
            date_test__gte=start,
            url__in=tps
        ).values_list('pk', flat=True)
        print sms
        export([], 'results-lac-latency_set', pks=set(sms))  # .json
