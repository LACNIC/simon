
from django.views.static import serve
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
import simon_project.settings as settings

import simon_app.views

urlpatterns = [

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


                       url(r'^$', simon_app.views.home, name='home'),  # Home

                       url(r'^about/$', simon_app.views.about, name='about'),
                       url(r'^applet/$', simon_app.views.applet, name='applet'),
                       url(r'^articles/$', simon_app.views.articles, name='articles'),  # Articles
                       url(r'^atlas/$', simon_app.views.atlas, name='atlas'),  # RIPE Atlas
                       url(r'^country_latency_chart/([A-Z]{2})/$', simon_app.views.country_latency_chart, name='country_latency_chart'),
                       url(r'^country_latency_chart/([0-9]{1,3})/$', simon_app.views.country_latency_chart, name='country_latency_chart'),
                       url(r'^getCountry/$', simon_app.views.getCountry, name='getCountry'),
                       url(r'^inner_latency_chart/$', simon_app.views.inner_latency_chart, name='inner_latency_chart'),
                       url(r'^lab/$', simon_app.views.lab, name='lab'),
                       url(r'^media/(?P<path>.*)/$', serve,
                           {'document_root': '%s/files' % (settings.STATIC_ROOT)}, name='media'),
                       url(r'^ntp_points/$', simon_app.views.ntp_points, name='ntp_points'),
                       url(r'^objectives/$', simon_app.views.objectives, name='objectives'),
                       url(r'^participate/$', simon_app.views.participate, name='participate'),
                       url(r'^postxmlresult/$', simon_app.views.post_xml_result, name='postxmlresult'),  # Applet
                       url(r'^postxmlresult/latency/$', simon_app.views.post_xml_result, name='postxmlresult'),
                       url(r'^postxmlresult/offline/$', simon_app.views.post_offline_testpoints, name='post_offline_testpoints'),
                       url(r'^prueba/$', simon_app.views.prueba, name='prueba'),
                       url(r'^region_latency_chart$', simon_app.views.region_latency_chart, name='region_latency_chart'),
                       url(r'^reports/country/$', simon_app.views.reports, name='reports'),
                       url(r'^reports/region/$', simon_app.views.charts, name='charts'),
                       url(r'^servers_locations_maps/$', simon_app.views.servers_locations_maps, name='servers_locations_maps'),
                       url(r'^speedtest/$', simon_app.views.speedtest, name='speedtest'),
                       url(r'^thanks/$', simon_app.views.thanks, name='thanks'),
                       url(r'^v6/performance/$', simon_app.views.v6perf, name='v6perf'),
                       url(r'^v6/adoption/$', simon_app.views.v6adoption, name='v6adoption'),
                       url(r'^web_configs/$', simon_app.views.web_configs, name='web_configs'),
                       url(r'^web_points/$', simon_app.views.web_points, name='web_points'),
                       ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Traceroute
# url(r'^post/traceroute/$', 'simon_app.views.post_traceroute', name='post_traceroute'),  # Traceroute Donation Program
# url(r'^traceroute/$', 'simon_app.views.traceroute'),
# url(r'^traceroute/curl/$', 'simon_app.views.traceroute_curl'),

admin.autodiscover()
