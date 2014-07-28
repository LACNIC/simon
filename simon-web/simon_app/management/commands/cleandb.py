from django.core.management.base import BaseCommand
from simon_app.models import Results

class Command(BaseCommand):

    def handle(self, *args, **options):
        rs = Results.objects.all()
        for r in rs:
            if r.ave_rtt > 900 or r.ave_rtt < 2:
                print r.ave_rtt
                r.delete()
