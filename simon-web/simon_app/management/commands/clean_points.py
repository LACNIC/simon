from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from simon_app.decorators import chatty_command

__author__ = 'agustin'


class Command(BaseCommand):

    @chatty_command(command="Clean Test Points")
    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.filter(enabled=True)
        N = len(tps)
        disabled = []
        for i, tp in enumerate(tps):
            try:
                tp.check_point()
            except Exception as e:
                print e
                continue

        return "The following points have been disabled %s" % (disabled)