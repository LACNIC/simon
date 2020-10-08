from django.db import models
from datetime import datetime
import pytz




def now():
    return datetime.now(tz=pytz.timezone('America/Montevideo'))


class CommandAudit(models.Model):
    """
        Class in charge of general command auditing
    """

    command = models.CharField(max_length=100)
    description = models.TextField(max_length=10240, default="Everything OK")
    date = models.DateTimeField(default=now)
    status = models.BooleanField(default=True)  # status of the command that has been just ran


class ProbeApiAudit(CommandAudit):
    """
        Class in charge of auditing ProbeAPI's experiments
    """
    count = models.IntegerField(
        default=0,
        verbose_name="Result count",
        help_text="Amount of results stored in the DB."
    )
