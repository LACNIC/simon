__author__ = 'agustin'
from django.core.management.base import BaseCommand
from simon_app.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        import twitter, random
        from simon_project import passwords as passwords

        rs = Results.objects.get_daily_results().exclude(country_origin="", country_destination="")

        if len(rs) == 0:
            exit(1)

        r = rs[random.randint(0, len(rs) - 1)]
        # 2-sigma is roughly equal to 95% confidence interval
        text = "Daily result %s --> %s %s ms (+-%s ms)" % (r.country_origin, r.country_destination, r.ave_rtt, 2 * r.dev_rtt)

        api = twitter.Api(
            consumer_key=passwords.TWITTER['consumer_key'],
            consumer_secret=passwords.TWITTER['consumer_secret'],
            access_token_key=passwords.TWITTER['access_token'],
            access_token_secret=passwords.TWITTER['access_token_secret']
        )
        api.PostUpdate(text)