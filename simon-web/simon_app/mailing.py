__author__ = 'agustin'

from django.template import Context
from django.core.mail import EmailMessage
from django.template.loader import get_template
from time import sleep
from django.contrib.auth.models import User


def send_mail_new_probes_found(subject="Nuevas probes", ctx={}, from_email="agustin@lacnic.net"):
    users = User.objects.filter(groups__name='mailing_new_probe')
    recipient_list = [u.email for u in users]

    send_mail(subject=subject, ctx=ctx, template_filename="emails/new_probe.html", from_email=from_email,
              recipient_list=recipient_list)


def send_mail_on_command_failed(subject="Command failed to run", command="[command]", from_email="agustin@lacnic.net"):
    ctx = {'command': command}
    send_mail(subject=subject, ctx=ctx, template_filename="emails/command_failed.html", from_email=from_email,
              recipient_list=["agustin@lacnic.net"])


def send_mail(subject="", template_filename="emails/pretty.html", ctx={}, from_email="agustin@lacnic.net",
              recipient_list=["agustin@lacnic.net"]):
    message = get_template(template_filename).render(Context(ctx))
    subject = "[simon] %s" % (subject)  # add the 'simon' tag to mail subject
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
        except Exception as e:
            print "Trying to send message %s" % (subject)
            print "Exception: %s" % (e)
            count += 1
        finally:
            sleep(30)
