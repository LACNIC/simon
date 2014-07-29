from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cemd.views.home', name='home'),
    # url(r'^cemd/', include('cemd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    url(r'^getip/$', 'cemd_app.views.get_ip', name='Get IP Address'),
    url(r'^getip/(?P<return_type>json|xml|text)/$', 'cemd_app.views.get_ip', name='Get IP Address with mime type'),
    url(r'^getip/(?P<return_type>jsonp)/(?P<jsonpcallback>\w+)/$', 'cemd_app.views.get_ip', name='Get IP Address with jsonp mime type'),
    url(r'^getip/(?P<return_type>jsonp)/$', 'cemd_app.views.get_ip', name='Get IP Address with jsonp mime type'),
)
