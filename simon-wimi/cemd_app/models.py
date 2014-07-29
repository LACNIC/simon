from django.db import models

class IpRequestQuery(models.Model):
    ip_address = models.GenericIPAddressField()
    date_request = models.DateTimeField('request date')
    
    def __unicode__(self):
        return self.ip_address
