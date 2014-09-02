from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import simon_project.settings as settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'simon_app.views.home', name='home'),
    # url(r'^simon_project/', include('simon_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^objectives/$', 'simon_app.views.objectives'),
    url(r'^participate/$', 'simon_app.views.participate'),
    url(r'^thanks/$', 'simon_app.views.thanks'),
    
    url(r'^reports/$', 'simon_app.views.reports'),
    url(r'^results/$', 'simon_app.views.home'),
    url(r'^results/form$', 'simon_app.views.form'),
    url(r'^results/throughputform$', 'simon_app.views.throughput_form'),
        
    url(r'^results/([A-Z]{2})/([46])/([0-9]{4})/([0-9]{1,2})/(Applet|JavaScript)/([0-9]{1})$', 'simon_app.views.tables'),  # /(\bntp\b|\bicmp_echo\b|\btcp_web\b|\btco_connection\b)
    url(r'^throughputresults/([A-Z]{2})/([46])/([0-9]{4})/([0-9]{1,2})/(JavaScript)/([0-9]{1})$', 'simon_app.views.throughput_tables'),  # /(\bntp\b|\bicmp_echo\b|\btcp_web\b|\btco_connection\b)
    url(r'^results/tables/$', 'simon_app.views.tables'),
    url(r'^applet/$', 'simon_app.views.applet'),
    url(r'^runapplet/$', 'simon_app.views.applet_run'),
    url(r'^runjavascript/$', 'simon_app.views.javascript_run'),
    
    # url(r'^postxmlresult/(?P<type>\blatency\b|\bthroughput\b)', 'simon_app.views.post_xml_result', name='postxmlresult'),
    url(r'^postxmlresult$', 'simon_app.views.post_xml_result', name='postxmlresult'),  # Applet
    url(r'^postxmlresult/latency$', 'simon_app.views.post_xml_result', name='postxmlresult'),
    url(r'^postxmlresult/throughput$', 'simon_app.views.post_xml_throughput_result'),
    url(r'^postxmlresult/offline$', 'simon_app.views.post_offline_testpoints'),
    
    url(r'^web_points/$', 'simon_app.views.web_points', {'amount': 0}),  # JSONP callback
    url(r'^web_points/(?P<amount>\d+)/$', 'simon_app.views.web_points', {'ip_version': 4}),
    url(r'^web_points/(?P<amount>\d+)/(?P<ip_version>\d+)/$', 'simon_app.views.web_points'),
    url(r'^ntp_points$', 'simon_app.views.ntp_points'),
    url(r'^web_configs/$', 'simon_app.views.web_configs'),
    url(r'^lab/$', 'simon_app.views.lab'),
    url(r'^getCountry/$', 'simon_app.views.getCountry'),
    
    url(r'^addnewwebpointform$', 'simon_app.views.add_new_webpoint_form'),
    url(r'^addnewntppointform$', 'simon_app.views.add_new_ntppoint_form'),
    url(r'^addnewwebpoint$', 'simon_app.views.add_new_webpoint'),
    url(r'^addnewntppoint$', 'simon_app.views.add_new_ntppoint'),
    
    url(r'^removetestpoint/([0-9A-Za-z]{%s})$' % (str(settings.TOKEN_LENGTH)), 'simon_app.views.remove_testpoint'),
    
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/files' % (settings.STATIC_ROOT)}),
    
    url(r'^charts/$', 'simon_app.views.charts_reports'),
    url(r'^charts_bandwidth/$', 'simon_app.views.charts_reports_bandwidth'),
    
    
    url(r'^country_latency_chart/([A-Z]{2})$', 'simon_app.views.country_latency_chart'),
    url(r'^country_latency_chart/([0-9]{1,3})$', 'simon_app.views.country_latency_chart'),
    url(r'^region_latency_chart$', 'simon_app.views.region_latency_chart'),
    url(r'^inner_latency_chart$', 'simon_app.views.inner_latency_chart'),
    url(r'^servers_locations_maps$', 'simon_app.views.servers_locations_maps'),
    url(r'^region_throughput_chart$', 'simon_app.views.region_throughput_chart'),
    url(r'^throughput_by_country_chart$', 'simon_app.views.throughput_by_country_chart'),
    
    ##############
    # TRACEROUTE #
    ##############
    
    url(r'^traceroute/$', 'simon_app.views.traceroute'),
    
    ############
    # ARTICLES #
    ############

    url(r'^articles/$', 'simon_app.views.articles'),

    #######
    # API #
    #######
    
    url(r'^api$', 'simon_app.views.api'),
    
    url(r'^api/latency/autnum/(?P<asn_origin>[0-9]+)/(?P<asn_destination>[0-9]+)/$', 'simon_app.api_views.ases'),
    
    # optional arguments: ip_version, year, month (2^4 = 16 combinations)
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<year>[0-9]{4})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<ip_version>[46])$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})/(?P<year>[0-9]{4})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<country>[A-Z]{2})$', 'simon_app.views.latency'),
    
    url(r'^api/latency/(?P<ip_version>[46])/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<ip_version>[46])/(?P<year>[0-9]{4})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<ip_version>[46])$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<ip_version>[46])/(?P<month>[0-9]{1,2})$', 'simon_app.views.latency'),
    url(r'^api/latency/(?P<year>[0-9]{4})$', 'simon_app.views.latency'),
    url(r'^api/latency$', 'simon_app.views.latency'),
    
    # optional arguments: ip_version, year, month (2^4 = 16 combinations)
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<year>[0-9]{4})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<ip_version>[46])$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<ip_version>[46])/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})/(?P<year>[0-9]{4})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<country>[A-Z]{2})$', 'simon_app.views.throughput'),
    
    url(r'^api/throughput/(?P<ip_version>[46])/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<ip_version>[46])/(?P<year>[0-9]{4})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<ip_version>[46])$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<ip_version>[46])/(?P<month>[0-9]{1,2})$', 'simon_app.views.throughput'),
    url(r'^api/throughput/(?P<year>[0-9]{4})$', 'simon_app.views.throughput'),
    url(r'^api/throughput$', 'simon_app.views.throughput'),
    
)
