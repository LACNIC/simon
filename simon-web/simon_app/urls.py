__author__ = 'agustin'

from django.conf.urls import patterns, include, url
import simon_project.settings as settings
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = patterns('',

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


                       url(r'^$', 'simon_app.views.home', name='home'),

                       url(r'^prueba/$', 'simon_app.views.prueba'),

                       url(r'^objectives/$', 'simon_app.views.objectives'),
                       url(r'^participate/$', 'simon_app.views.participate'),
                       url(r'^thanks/$', 'simon_app.views.thanks'),

                       url(r'^reports/$', 'simon_app.views.reports'),
                       url(r'^results/$', 'simon_app.views.home'),
                       url(r'^results/form$', 'simon_app.views.form'),

                       url(r'^feedback$', 'simon_app.views.feedbackForm'),

                       url(r'^results/([A-Z]{2})/([46])/([0-9]{4})/([0-9]{1,2})/(Applet|JavaScript)/([0-9]{1})$', 'simon_app.views.tables'),  # /(\bntp\b|\bicmp_echo\b|\btcp_web\b|\btco_connection\b)
                       # /(\bntp\b|\bicmp_echo\b|\btcp_web\b|\btco_connection\b)
                       url(r'^results/tables/$', 'simon_app.views.tables'),
                       url(r'^applet/$', 'simon_app.views.applet'),
                       # url(r'^runjavascript/$', 'simon_app.views.javascript_run'),

                       # url(r'^postxmlresult/(?P<type>\blatency\b|\bthroughput\b)', 'simon_app.views.post_xml_result', name='postxmlresult'),
                       url(r'^postxmlresult/$', 'simon_app.views.post_xml_result', name='postxmlresult'),  # Applet
                       url(r'^post/traceroute/$', 'simon_app.views.post_traceroute', name='post_traceroute'),  # Traceroute Donation Program
                       url(r'^postxmlresult/latency/$', 'simon_app.views.post_xml_result', name='postxmlresult'),
                       url(r'^postxmlresult/offline/$', 'simon_app.views.post_offline_testpoints'),

                       url(r'^web_points/$', 'simon_app.views.web_points', {'amount': 1, 'ip_version': 4}),  # JSONP callback
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

                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/files' % (settings.STATIC_ROOT)}),

                       url(r'^charts/$', 'simon_app.views.charts_reports'),

                       url(r'^country_latency_chart/([A-Z]{2})$', 'simon_app.views.country_latency_chart'),
                       url(r'^country_latency_chart/([0-9]{1,3})$', 'simon_app.views.country_latency_chart'),
                       url(r'^region_latency_chart$', 'simon_app.views.region_latency_chart'),
                       url(r'^inner_latency_chart$', 'simon_app.views.inner_latency_chart'),
                       url(r'^servers_locations_maps$', 'simon_app.views.servers_locations_maps'),

                       # Traceroute
                       url(r'^traceroute/$', 'simon_app.views.traceroute'),
                       url(r'^traceroute/curl/$', 'simon_app.views.traceroute_curl'),

                       # Articles
                       url(r'^articles/$', 'simon_app.views.articles'),

                       # RIPE Atlas indicators
                       url(r'^atlas/$', 'simon_app.views.atlas')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.autodiscover()
