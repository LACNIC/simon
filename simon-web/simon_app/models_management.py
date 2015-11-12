__author__ = 'agustin'
from django.db import models
from datetime import datetime

class CommandAudit(models.Model):
    command = models.CharField(max_length=100)
    description = models.TextField(max_length=10240, default="Everything OK")
    date = models.DateTimeField(default=datetime.now())
    status = models.BooleanField(default=True) # status of the command that has been just ran