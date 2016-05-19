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
    enable.short_description = "Habilitar punto de prueba"

    def disable(modeladmin, request, queryset):
        queryset.update(enabled=False)
    disable.short_description = "Deshabilitar punto de prueba"

    def check_point(modeladmin, request, queryset):
        for q in queryset:
            q.check_point()
    check_point.short_description = "Chequear punto de prueba"

    list_display = ['country', 'ip_address', 'autnum', 'city', 'date_short', 'enabled']
    # list_filter = ['country', 'ip_version']
    list_filter = ('country', )
    ordering = ['-date_created', 'enabled']
    actions = [enable, disable, check_point]
    search_fields = ['country']

class RipeAtlasProbeAdmin(admin.ModelAdmin):
    list_display = ['country_code', 'asn_v4', 'asn_v6', 'prefix_v4', 'prefix_v6']
    search_fields = ['country_code']

class ConfigsAdmin(admin.ModelAdmin):
    def enable(modeladmin, request, queryset):
        queryset.update(config_value="1")

    def disable(modeladmin, request, queryset):
        queryset.update(config_value="0")
    list_display = ['config_name', 'config_value', 'config_description']
    actions = [enable, disable]

from django.contrib.admin.views.main import ChangeList
class InactiveUsersView(ChangeList):
    """
        This view displays the list of inactive users
    """
    def __init__(self, *args, **kwargs):
        super(InactiveUsersView, self).__init__(*args, **kwargs)
        self.list_display = ('description')

    def get_queryset(self, request):
        qs = super(InactiveUsersView, self).get_queryset(request)
        # filter inactive and admin users
        return qs.filter(is_staff=False, is_active=False, is_superuser=False)

class RipeAtlasTokenAdmin(admin.ModelAdmin):
    pass

class RipeAtlasTokenListAdmin(admin.ModelAdmin):
    pass
     # def save_model(self, request, obj, form, change):
     #     print obj
     #     tokens = self.token_list.split(sep="\n")
     #     for token in tokens:
     #         print token
     #         rat = RipeAtlasToken(token=token)
     #         rat.save()

admin.site.register(Comment)

admin.site.register(Results, ResultsAdmin)

admin.site.register(TestPoint, TestPointAdmin)
admin.site.register(Configs, ConfigsAdmin)

admin.site.register(ProbeApiPingResult, ResultsAdmin)
admin.site.register(SpeedtestTestPoint, TestPointAdmin)
admin.site.register(RipeAtlasPingResult, ResultsAdmin)

admin.site.register(RipeAtlasProbe, RipeAtlasProbeAdmin)

admin.site.register(RipeAtlasToken, RipeAtlasTokenAdmin)
admin.site.register(RipeAtlasTokenList, RipeAtlasTokenListAdmin)