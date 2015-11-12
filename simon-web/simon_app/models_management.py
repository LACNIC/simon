__author__ = 'agustin'
from django.db import models
from datetime import datetime

from django.core.management.base import BaseCommand

class CommandAudit(models.Model):
    command = models.CharField(max_length=100)
    date = models.DateTimeField(default=datetime.now())
    status = models.BooleanField(default=True) # status of the command that has been just ran