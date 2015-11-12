from simon_app.mailing import send_mail

__author__ = 'agustin'
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_mail(subject="Mail Test")