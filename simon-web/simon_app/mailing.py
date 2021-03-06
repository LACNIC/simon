from django.template import Context
from django.core.mail import EmailMessage
from django.template.loader import get_template
from time import sleep
from django.contrib.auth.models import User
from simon_project.settings import DEBUG
import logging




def send_mail_new_probes_found(subject="Nuevas probes", ctx={}, from_email="agustin@lacnic.net"):
    users = User.objects.filter(groups__name='mailing_new_probe')
    recipient_list = [u.email for u in users]

    send_mail(subject=subject, ctx=ctx, template_filename="emails/new_probe.html", from_email=from_email,
              recipient_list=recipient_list)


def send_mail_new_points_found(subject="Nuevos puntos", ctx={}, from_email="agustin@lacnic.net"):
    users = User.objects.filter(groups__name='mailing_new_points')
    recipient_list = [u.email for u in users]

    send_mail(subject=subject, ctx=ctx, template_filename="emails/new_points.html", from_email=from_email,
              recipient_list=recipient_list)


def send_mail_point_offline(subject="Punto dado de baja", ctx={}, from_email="agustin@lacnic.net"):
    users = User.objects.filter(groups__name='mailing_new_points')
    recipient_list = [u.email for u in users]

    send_mail(subject=subject, ctx=ctx, template_filename="emails/offline.html", from_email=from_email,
              recipient_list=recipient_list)


def send_mail_on_command_failed(subject="Command failed to run", command="[command]", from_email="agustin@lacnic.net"):
    ctx = {'command': command}
    send_mail(subject=subject, ctx=ctx, template_filename="emails/command_failed.html", from_email=from_email,
              recipient_list=["agustin@lacnic.net"])


def send_mail_test(subject="Testing the mailing system", command="[command]", from_email="agustin@lacnic.net"):
    ctx = {'command': command}
    send_mail(subject=subject, ctx=ctx, template_filename="emails/test.html", from_email=from_email,
              recipient_list=["agustin@lacnic.net"])


def send_mail(subject="", template_filename="emails/pretty.html", ctx={}, from_email="agustin@lacnic.net",
              recipient_list=["agustin@lacnic.net"]):
    if DEBUG:
        recipient_list = ["agustin@lacnic.net"]

    logger = logging.getLogger(__name__)
    logger.info("Sending email [%s]" % (subject))

    message = get_template(template_filename).render(ctx)
    subject = "[simon] %s" % (subject)  # add the 'simon' tag to mail subject
    msg = EmailMessage(subject=subject, body=message, from_email=from_email, to=recipient_list)
    msg.content_subtype = 'html'

    MAX_COUNT = 3
    sent = False
    count = 0
    while not sent or count < MAX_COUNT:
        try:
            msg.send()
            sent = True
            return
        except Exception as e:
            logger.error("Error sending email [%s]" % (subject))
            logger.error("Exception: %s" % (e))
            count += 1
        finally:
            sleep(30)
