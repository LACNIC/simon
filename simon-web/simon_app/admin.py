from simon_app.models import *
from django.contrib import admin


class ResultsAdmin(admin.ModelAdmin):
    fields = ()
    readonly_fields = ('as_origin', 'as_destination')
    list_display = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'ave_rtt', 'dev_rtt', 'date_short', 'protocol']
    ordering = ['-date_test', 'country_origin', 'country_destination']
    search_fields = ['country_origin', 'country_destination', 'as_origin', 'as_destination']

    # list_filter = ('enabled',)

    class Media:
        js = (
            # '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            # 'http://code.jquery.com/jquery-migrate-1.2.1.js',
            # 'simon_app/admin/js/jquery-adapt.js'
        )

class TestPointAdmin(admin.ModelAdmin):

    def enable(modeladmin, request, queryset):
        queryset.update(enabled=True)
    enable.short_description = "Habilitar punto de testing"

    def disable(modeladmin, request, queryset):
        queryset.update(enabled=False)
    enable.short_description = "Deshabilitar punto de testing"

    list_display = ['country', 'ip_address', 'autnum', 'city', 'date_short', 'enabled']
    ordering = ['-date_created', 'enabled']
    actions = [enable, disable]
    search_fields = ['country']

class RipeAtlasProbeAdmin(admin.ModelAdmin):
    list_display = ['country_code', 'asn_v4', 'asn_v6', 'prefix_v4', 'prefix_v6']
    search_fields = ['country_code']


admin.site.register(Results, ResultsAdmin)

admin.site.register(TestPoint, TestPointAdmin)
admin.site.register(Configs)

admin.site.register(Params)

admin.site.register(ProbeApiPingResult, ResultsAdmin)
admin.site.register(SpeedtestTestPoint, TestPointAdmin)
admin.site.register(RipeAtlasPingResult, ResultsAdmin)

admin.site.register(RipeAtlasProbe, RipeAtlasProbeAdmin)