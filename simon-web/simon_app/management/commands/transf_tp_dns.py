
from simon_app.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cc', type=str)
        parser.add_argument('af', choices=['v4', 'v6'])

    def handle(self, *args, **options):
        # First arg is country code, second arg is ip version: v4 or v6

        cc = options['cc']
        af = options['af']
        version = ""

        if af == "v4":
            version = "."
        elif af == "v6":
            version = ":"

        tps = SpeedtestTestPoint.objects.filter(country=cc.upper(), ip_address__contains=version, enabled=True)

        for tp in tps:
            print tp.ip_address
