__author__ = 'agustin'

from django.template import Context
from django.core.mail import EmailMessage
from django.template.loader import get_template
from time import sleep

def send_mail(subject="", ctx={}):

    from_email = "agustin@lacnic.net"
    recipient_list = [from_email]

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
