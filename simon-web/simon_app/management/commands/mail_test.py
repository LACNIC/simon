from simon_app.mailing import send_mail_test


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_mail_test(subject="Mail Test")