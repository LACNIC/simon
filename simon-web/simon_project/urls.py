# from django.conf.urls import patterns, include, url
# from django.contrib import admin
#
# admin.autodiscover()
#
# urlpatterns = patterns('',
#
#                 url(r'api/', include('simon_app.urls_api')),
#                 url(r'apiv2/', include('simon_app.views_apiv2')),
#                 url(r'admin/', include(admin.site.urls)),
#
#                 # Common urls
#                 url(r'', include('simon_app.urls'))
#                 )
#
# from django.conf.urls import patterns, include, url
# from django.contrib import admin

from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urls = [
                # Common urls
                url(r'', include('simon_app.urls'))
                ]

urlpatterns = [
                       url(r'', include(urls)),
                       url(r'admin/', include(admin.site.urls)),
                       url(r'api/', include('simon_app.urls_api'))
                       ]
