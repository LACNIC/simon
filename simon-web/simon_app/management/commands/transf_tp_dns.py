
from simon_app.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # First arg is country code, second arg is ip version: v4 or v6

        cc = args[0]
        af = args[1]
        version = ""

        if af == "v4":
            version = "."
        elif af == "v6":
            version = ":"

        tps = SpeedtestTestPoint.objects.filter(country=cc.upper(), ip_address__contains=version, enabled=True)

        for tp in tps:
            print tp.ip_address
