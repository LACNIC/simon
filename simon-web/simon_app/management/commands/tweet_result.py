__author__ = 'agustin'
from simon_app.management.commands.tweet import *
from simon_app.models import Results
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        import random

        rs = Results.objects.get_daily_results().exclude(country_origin="", country_destination="")

        if len(rs) == 0:
            exit(1)

        r = rs[random.randint(0, len(rs) - 1)]
        # 2-sigma is roughly equal to 95% confidence interval
        text = "Daily result %s --> %s %s ms (+-%s ms)" % (
        r.country_origin, r.country_destination, r.ave_rtt, 2 * r.dev_rtt)

        tweet(text)
