from simon_app.models import *
from django.contrib import admin


class ResultsAdmin(admin.ModelAdmin):
    fields = ()
    readonly_fields = ('as_origin', 'as_destination')

    class Media:
        js = (
            # '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            # 'http://code.jquery.com/jquery-migrate-1.2.1.js',
            # 'simon_app/admin/js/jquery-adapt.js'
        )


admin.site.register(Country)
# admin.site.register(ThroughputResults)
admin.site.register(Results, ResultsAdmin)
admin.site.register(RipeAtlasPingResult)
# admin.site.register(RipeAtlasMeasurement)
admin.site.register(RipeAtlasResult)
admin.site.register(TracerouteResult)

admin.site.register(TestPoint)
# admin.site.register(Images)
# admin.site.register(Images_in_TestPoints)
admin.site.register(OfflineReport)
admin.site.register(Configs)
admin.site.register(AS)

admin.site.register(Params)

# admin.site.register(Notification)
# admin.site.register(Alert)
# admin.site.register(Error)
# admin.site.register(Success)

admin.site.register(ProbeApiPingResult)
admin.site.register(SpeedtestTestPoint)

admin.site.register(RipeAtlasProbe)