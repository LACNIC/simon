from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings

admin.autodiscover()

urls = patterns('',

                # API urls
                url(r'api/', include('simon_app.urls_api')),

                # Common urls
                url(r'', include('simon_app.urls'))
)

# The /simon tree root in Apache
urlpatterns = patterns('',
                       # Home site
                       url(r'^$', 'simon_app.views.home', name='home'),
                       url(r'', include(urls)),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
)
