__author__ = 'agustin'

from django.template import Context
from django.core.mail import EmailMessage
from django.template.loader import get_template
from time import sleep
from django.contrib.auth.models import User, Group

def send_mail(subject="", ctx={}):

    from_email = "agustin@lacnic.net"
    users = User.objects.filter(groups__name='mailing_new_probe')
    recipient_list = [u.email for u in users]

    message = get_template('emails/new_probe.html').render(Context(ctx))
    msg = EmailMessage(subject=subject, body=message, from_email=from_email, to=recipient_list)
    msg.content_subtype = 'html'

    MAX_COUNT = 12
    sent = False
    count = 0
    while not sent or count < MAX_COUNT:
        try:
            msg.send()
            sent = True
            return
        except:
            print "Trying to send message %s" % (subject)
            count += 1
        finally:
            sleep(30)
