__author__ = 'agustin'

from django.db import models
import datetime

class Notification(models.Model):
    title = models.TextField(default='')
    text = models.TextField(default='')
    date_created = models.DateTimeField(default=datetime.datetime.now())

    def expiration_date(self):
        return self.date_created + datetime.timedelta(days=7)

class Alert(Notification):
    # Yellow
    pass

class Success(Notification):
    # Green
    pass

class Error(Notification):
    # Red
    pass