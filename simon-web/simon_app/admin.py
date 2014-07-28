from simon_app.models import Country, ThroughputResults, Results, TestPoint, Images, Images_in_TestPoints, OfflineReport, Configs, ActiveTokens
from django.contrib import admin

admin.site.register(Country)
admin.site.register(ThroughputResults)
admin.site.register(Results)
admin.site.register(TestPoint)
admin.site.register(Images)
admin.site.register(Images_in_TestPoints)
admin.site.register(OfflineReport)
admin.site.register(Configs)
admin.site.register(ActiveTokens)