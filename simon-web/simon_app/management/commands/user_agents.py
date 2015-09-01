from django.core.management.base import BaseCommand
import datetime
from simon_app.models import Results


class Command(BaseCommand):
    def handle(self, *args, **options):

        now = datetime.datetime.now()
        results = Results.objects.javascript()
        for r in results:
            if r.user_agent != '':
                print r.user_agent

