from simon_app.models import Country, ThroughputResults, Results, ResultsManager, TestPoint, Images, Images_in_TestPoints, OfflineReport, Configs, AS
from django.contrib import admin

class ResultsAdmin(admin.ModelAdmin):
    fields = ()
    readonly_fields = ('as_origin', 'as_destination')
    
admin.site.register(Country)
admin.site.register(ThroughputResults)
admin.site.register(Results, ResultsAdmin)
admin.site.register(TestPoint)
admin.site.register(Images)
admin.site.register(Images_in_TestPoints)
admin.site.register(OfflineReport)
admin.site.register(Configs)
admin.site.register(AS)