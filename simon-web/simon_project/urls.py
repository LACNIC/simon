from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urls = patterns('',

                # API urls
                url(r'api/', include('simon_app.urls_api')),

                url(r'apiv2/', include('simon_app.views_apiv2')),

                # Common urls
                url(r'', include('simon_app.urls'))
                )

# The /simon tree root in Apache
urlpatterns = patterns('',
                       url(r'', include(urls)),

                       # Uncomment the next line to enable the admin:
                       url(r'admin/', include(admin.site.urls)),
)
