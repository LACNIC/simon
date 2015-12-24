__author__ = 'agustin'
import random
from simon_app.management.commands.tweet import *
from simon_app.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        import random

        rs = Results.objects.get_daily_results()

        if len(rs) == 0:
            exit(1)

        r = random.choice(rs)
        # 2-sigma is roughly equal to 95% confidence interval
        text = "Resultado de hoy %s --> %s %s ms (+-%s ms, via %s protocol)" % (r.country_origin, r.country_destination, r.ave_rtt, 2 * r.dev_rtt, r.protocol())

        tweet(text)