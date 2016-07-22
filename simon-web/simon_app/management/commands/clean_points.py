from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from sys import stdout
from simon_app.decorators import chatty_command

__author__ = 'agustin'


class Command(BaseCommand):

    @chatty_command(command="Clean Test Points")
    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.filter(enabled=True)
        N = len(tps)
        disabled = []
        for i, tp in enumerate(tps):
            stdout.write("\r%.2f%%" % (100.0 * i / N))
            stdout.flush()

            tp.check_point()

        return "The following points have been disabled %s" % (disabled)