from simon_app.models import *
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin import SimpleListFilter
from datetime import datetime, timedelta



class SimonAdmin(admin.ModelAdmin):
    pass


class SimonReadOnlyAdmin(SimonAdmin):
    """
        Generic admin covering admin-wide
    """

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class ResultsAdmin(SimonReadOnlyAdmin):
    fields = ()
    list_display = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'ave_rtt', 'dev_rtt',
                    'date_short', 'protocol', 'ip_origin', 'ip_destination']
    ordering = ['-date_test', 'country_origin', 'country_destination']
    search_fields = ['country_origin', 'country_destination', 'as_origin', 'as_destination']

    class Media:
        js = (
            # '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            # 'http://code.jquery.com/jquery-migrate-1.2.1.js',
            # 'simon_app/admin/js/jquery-adapt.js'
        )


class ProbaeApiPingResultAdmin(ResultsAdmin):

    list_display = ResultsAdmin.list_display + ['probeapi_probe_id']


class ProbeapiTracerouteResultAdmin(SimonReadOnlyAdmin):
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    list_display = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'hop_count',
                    'country_count', 'as_count']
    search_fields = ['country_origin', 'country_destination', 'as_origin', 'as_destination']


class TracerouteHopAdmin(SimonReadOnlyAdmin):
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    list_display = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'ip_origin',
                    'ip_destination', 'ave_rtt', 'dev_rtt', 'date_short', 'protocol', 'hop_number']
    search_fields = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'ip_origin',
                     'ip_destination']


class TestPointAdmin(SimonReadOnlyAdmin):
    """
        Admin in charge of TestPoint administrative operations
    """

    def enable(self, request, queryset):
        queryset.update(enabled=True)

    enable.short_description = "Habilitar punto de prueba"

    def disable(self, request, queryset):
        queryset.update(enabled=False)

    disable.short_description = "Deshabilitar punto de prueba"

    def check_point(self, request, queryset):
        for q in queryset:
            q.check_point(protocol="http")

    check_point.short_description = "Chequear punto de prueba (HTTP)"

    def check_point_https(self, request, queryset):
        for q in queryset:
            q.check_point(protocol="https")

    check_point.short_description = "Chequear punto de prueba (HTTPS)"

    list_display = ['country', 'ip_address', 'autnum', 'city', 'date_short', 'enabled']
    list_filter = ('country',)
    ordering = ['-date_created', 'enabled']
    actions = [enable, disable, check_point]
    search_fields = ['country', 'ip_address', 'city']


class SpeedtestTestPointListFilter(SimpleListFilter):
    pass


class SpeedtestTestPointAdmin(TestPointAdmin):
    list_display = TestPointAdmin.list_display + ['has_https_support']


class RipeAtlasProbeAdmin(SimonReadOnlyAdmin):
    list_display = ['country_code', 'asn_v4', 'asn_v6', 'prefix_v4', 'prefix_v6']
    search_fields = ['country_code']


class ConfigsAdmin(admin.ModelAdmin):
    def enable(modeladmin, request, queryset):
        queryset.update(config_value="1")

    def disable(modeladmin, request, queryset):
        queryset.update(config_value="0")

    list_display = ['config_name', 'config_value', 'config_description']
    actions = [enable, disable]


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


class CommandAuditAdmin(SimonReadOnlyAdmin):
    list_display = ['command', 'date', 'status']


class ProbeApiAuditAdmin(CommandAuditAdmin):

    rate = .001
    list_display = ['command', 'date', 'status', 'this', 'week', 'month', 'billed']

    def this(self, obj):
        return obj.count

    this.short_description = "Results count"

    def week(self, obj):
        a_week_ago = obj.date - timedelta(days=7)
        audits = ProbeApiAudit.objects.filter(date__gt=a_week_ago).filter(date__lte=obj.date)
        count = 0
        for audit in audits:
            count += audit.count
        return count

    week.short_description = "Week count"

    def month(self, obj):
        a_month_ago = obj.date - timedelta(days=30)
        audits = ProbeApiAudit.objects.filter(date__gt=a_month_ago).filter(date__lte=obj.date)
        count = 0
        for audit in audits:
            count += audit.count
        return count

    month.short_description = "Month count"

    def billed(self, obj):
        return "%.0f EUR" % float(self.month(obj)*self.rate*10)  # 10 pings per result

    billed.short_description = "Expected invoice"


class ASAdmin(SimonReadOnlyAdmin):
    list_display = ['asn', 'network', 'pfx_length', 'date_updated', 'regional']
    search_fields = ['asn', 'network']


class HttpsCheckAdmin(SimonReadOnlyAdmin):
    list_display = ['date', 'status', 'test_point']


class CountryInline(admin.TabularInline):
    model = Country
    extra = 1
    raw_id_fields = ["region"]


class CountryAdmin(SimonReadOnlyAdmin):
    list_display = ['printable_name', 'iso']


class RegionAdmin(SimonAdmin):
    list_display = ['name', 'numcode', 'count']
    inlines = [
        CountryInline,
    ]

    def count(self, region):
        return ','.join(list(Country.objects.filter(region=region).values_list('iso', flat=True)))

class V6PerfAdmin(SimonReadOnlyAdmin):
    list_display = ['country', 'diff', 'dualstack', 'v6_rate', 'date', 'time_window']
    pass

class ProbeApiRequestAdmin(SimonAdmin):
    list_display = ['date_1', 'date_2', 'test_type', 'count', 'stage_collected']

    def count(self, obj):
        try:
            sources = json.loads(obj.test_settings).get("Sources")
        except:
            sources = []
        if sources:
            return len(sources)
        else:
            return 0

class ProbeApiFTPResults(SimonReadOnlyAdmin):
    # def get_readonly_fields(self, request, obj=None):
    #     return [f.name for f in self.model._meta.fields]

    list_display = ['batch', 'ip', 'command_name']
    # search_fields = ['country_origin', 'country_destination', 'as_origin', 'as_destination', 'ip_origin', 'ip_destination']

admin.site.register(ProbeApiFetchFromFTP, ProbeApiFTPResults)

class ProbeApiV3PingResultAdmin(SimonAdmin):
    list_display = ['cc_origin', 'cc_destination', 'as_origin', 'as_destination', 'ip_origin', 'ip_destination', 'ave_rtt', 'dev_rtt', 'packet_loss_percentage','hostname', 'ipv4_only', 'ipv6_only', 'error_msg','server_time']

    search_fields =['data__country_origin', 'data__country_destination']

    readonly_fields = ['get_results']
    fieldsets = [
        ('Ping info', {'fields': ['data', 'packet_loss_percentage']}),
        ('Metadata', {'fields': ['metadata', 'get_results']}),
    ]

    def cc_origin(self, obj):
        return obj.data.country_origin
    def cc_destination(self, obj):
        return obj.data.country_destination
    def as_origin(self, obj):
        return obj.data.as_origin
    def as_destination(self, obj):
        return obj.data.as_destination
    def ip_origin(self, obj):
        return obj.data.ip_origin
    def ip_destination(self, obj):
        return obj.data.ip_destination
    def ave_rtt(self, obj):
        return obj.data.ave_rtt
    def dev_rtt(self, obj):
        return obj.data.dev_rtt
    def hostname(self, obj):
        return obj.metadata.hostname
    def ipv4_only(self, obj):
        return obj.metadata.ipv4only
    def ipv6_only(self, obj):
        return obj.metadata.ipv6only
    def error_msg(self, obj):
        return obj.metadata.error_msg
    def server_time(self, obj):
        return obj.metadata.server_time


class ProbeApiV3TracerouteHopAdmin(SimonAdmin):
    list_display = ['cc_origin', 'cc_destination', 'as_origin', 'as_destination', 'ip_origin', 'ip_destination', 'ave_rtt', 'dev_rtt', 'error_msg', 'hop_number','hostname', 'ipv4_only', 'ipv6_only','server_time']

    readonly_fields = ['get_results']
    fieldsets = [
        ('Traceroute info', {'fields': ['data', 'hop_number', 'error_msg']}),
        ('Metadata', {'fields': ['traceroute', 'get_results']}),
    ]

    def cc_origin(self, obj):
        return obj.data.country_origin
    def cc_destination(self,obj):
        return obj.data.country_destination
    def as_origin(self,obj):
        return obj.data.as_origin
    def as_destination(self,obj):
        return obj.data.as_destination
    def ip_origin(self,obj):
        return obj.data.ip_origin
    def ip_destination(self,obj):
        return obj.data.ip_destination
    def ave_rtt(self,obj):
        return obj.data.ave_rtt
    def dev_rtt(self,obj):
        return obj.data.dev_rtt
    def hostname(self,obj):
        return obj.traceroute.hostname
    def ipv4_only(self,obj):
        return obj.traceroute.ipv4only
    def ipv6_only(self,obj):
        return obj.traceroute.ipv6only
    def server_time(self,obj):
        return obj.traceroute.server_time

class ProbeApiV3MetaDataAdmin(SimonAdmin):
    list_display = ['probeapi_probe_id', 'hostname', 'ipv4only', 'ipv6only', 'error_msg', 'server_time', 'time_diff']

class ProbeApiV3TracerouteAdmin(SimonAdmin):
    list_display = ['probeapi_probe_id', 'hostname', 'ipv4only', 'ipv6only', 'error_msg', 'server_time', 'time_diff']
    readonly_fields = ['get_results','get_command_name']
    fieldsets = [
        ('Traceroute info', {'fields': ['probeapi_probe_id', 'hostname', 'ipv4only', 'ipv6only', 'error_msg', 'server_time', 'time_diff']}),
        ('Command Result', {'fields': ['get_results']}),
        ('command Name', {'fields': ['get_command_name']})
    ]


admin.site.register(ProbeApiV3PingResult, ProbeApiV3PingResultAdmin)
admin.site.register(ProbeApiV3TracerouteHop, ProbeApiV3TracerouteHopAdmin)
admin.site.register(ProbeApiV3DataResult, ResultsAdmin)
admin.site.register(ProbeApiV3ResultMetaData, ProbeApiV3MetaDataAdmin)
admin.site.register(ProbeApiV3TracerouteResultMetaData, ProbeApiV3TracerouteAdmin)

admin.site.register(Results, ResultsAdmin)

admin.site.register(TestPoint, TestPointAdmin)
admin.site.register(Configs, ConfigsAdmin)

admin.site.register(ProbeApiPingResult, ProbaeApiPingResultAdmin)
admin.site.register(ProbeapiTracerouteResult, ProbeapiTracerouteResultAdmin)
admin.site.register(ProbeapiTracerouteHop, TracerouteHopAdmin)

admin.site.register(SpeedtestTestPoint, SpeedtestTestPointAdmin)

admin.site.register(RipeAtlasProbe, RipeAtlasProbeAdmin)

admin.site.register(CommandAudit, CommandAuditAdmin)
admin.site.register(ProbeApiAudit, ProbeApiAuditAdmin)

admin.site.register(AS, ASAdmin)

admin.site.register(HttpsCheck, HttpsCheckAdmin)

admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)

admin.site.register(V6Perf, V6PerfAdmin)
admin.site.register(ProbeApiRequest, ProbeApiRequestAdmin)
