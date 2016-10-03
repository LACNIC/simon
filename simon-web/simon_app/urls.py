__author__ = 'agustin'
from django.conf.urls import patterns, url
from django.contrib import admin
from django.conf.urls.static import static
import simon_project.settings as settings

urlpatterns = patterns('',

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


                       url(r'^$', 'simon_app.views.home', name='home'),  # Home

                       url(r'^about/$', 'simon_app.views.about'),
                       url(r'^applet/$', 'simon_app.views.applet'),
                       url(r'^articles/$', 'simon_app.views.articles'),  # Articles
                       url(r'^atlas/$', 'simon_app.views.atlas'),  # RIPE Atlas
                       url(r'^country_latency_chart/([A-Z]{2})/$', 'simon_app.views.country_latency_chart'),
                       url(r'^country_latency_chart/([0-9]{1,3})/$', 'simon_app.views.country_latency_chart'),
                       url(r'^feedback/$', 'simon_app.views.feedbackForm'),
                       url(r'^getCountry/$', 'simon_app.views.getCountry'),
                       url(r'^inner_latency_chart/$', 'simon_app.views.inner_latency_chart'),
                       url(r'^lab/$', 'simon_app.views.lab'),
                       url(r'^media/(?P<path>.*)/$', 'django.views.static.serve',
                           {'document_root': '%s/files' % (settings.STATIC_ROOT)}),
                       url(r'^ntp_points/$', 'simon_app.views.ntp_points'),
                       url(r'^objectives/$', 'simon_app.views.objectives'),
                       url(r'^participate/$', 'simon_app.views.participate'),
                       url(r'^postxmlresult/$', 'simon_app.views.post_xml_result', name='postxmlresult'),  # Applet
                       url(r'^postxmlresult/latency/$', 'simon_app.views.post_xml_result', name='postxmlresult'),
                       url(r'^postxmlresult/offline/$', 'simon_app.views.post_offline_testpoints'),
                       url(r'^prueba/$', 'simon_app.views.prueba'),
                       url(r'^region_latency_chart$', 'simon_app.views.region_latency_chart'),
                       url(r'^reports/country/$', 'simon_app.views.reports'),
                       url(r'^reports/region/$', 'simon_app.views.charts'),
                       url(r'^servers_locations_maps/$', 'simon_app.views.servers_locations_maps'),
                       url(r'^speedtest/$', 'simon_app.views.speedtest'),
                       url(r'^thanks/$', 'simon_app.views.thanks'),
                       url(r'^v6/perf/$', 'simon_app.views.v6perf', name='v6perf'),
                       url(r'^v6/adoption/$', 'simon_app.views.v6perf', name='v6perf'),
                       url(r'^web_configs/$', 'simon_app.views.web_configs'),
                       url(r'^web_points/$', 'simon_app.views.web_points'),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Traceroute
# url(r'^post/traceroute/$', 'simon_app.views.post_traceroute', name='post_traceroute'),  # Traceroute Donation Program
# url(r'^traceroute/$', 'simon_app.views.traceroute'),
# url(r'^traceroute/curl/$', 'simon_app.views.traceroute_curl'),

admin.autodiscover()
