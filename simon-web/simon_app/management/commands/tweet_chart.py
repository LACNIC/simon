__author__ = 'agustin'
from django.core.management.base import BaseCommand
from simon_app.models import *
from scipy.stats import gaussian_kde
import numpy as np
from simon_app.decorators import timed


class Command(BaseCommand):
    @timed(name="Tweeting chart")
    def handle(self, *args, **options):
        import twitter, random
        from simon_project import passwords as passwords

        import matplotlib
        # Force matplotlib to not use any Xwindows backend.
        matplotlib.use('Agg')

        from matplotlib import pyplot as plt

        week = Results.objects.get_weekly_results().exclude(country_origin="", country_destination="")
        ccs = Country.objects.get_lacnic_countrycodes()
        week = [w for w in week if w.country_origin in ccs and w.country_destination in ccs]
        origin = random.choice(week).country_origin
        fixed_origin = week.filter(Q(country_origin=origin))
        destination = random.choice(fixed_origin).country_destination
        rs = week.filter(Q(country_origin=origin) & Q(country_destination=destination)).values_list('ave_rtt',
                                                                                                    flat=True)

        if len(rs) <= 1:
            exit(1)

        kde = gaussian_kde(rs)
        xs = np.arange(0, 800, .1)
        kde.covariance_factor = lambda: .25
        kde._compute_covariance()
        ys = kde(xs)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        plt.xlabel("RTT latency (ms)")
        title = "Results from %s to %s" % (origin, destination)
        plt.title(title)
        line, = ax.plot(xs, ys, antialiased=True, color="orange")
        ax.fill_between(xs, ys, alpha=.5, zorder=5, antialiased=True, color="orange")

        ax.legend(["%s samples (last 7 days)" % (len(rs))])
        image = settings.STATIC_ROOT + "/tmp.png"
        plt.savefig(image)

        api = twitter.Api(
            consumer_key=passwords.TWITTER['consumer_key'],
            consumer_secret=passwords.TWITTER['consumer_secret'],
            access_token_key=passwords.TWITTER['access_token'],
            access_token_secret=passwords.TWITTER['access_token_secret']
        )

        with open(image) as image:
            api.PostMedia(title, media=image)
