"""
WSGI config for simon_project project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os, sys
sys.path.append('/opt/django/simon/simon-web')
sys.path.append('/Users/agustin/git/simon/simon-web/simon_project')

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simon_project.settings")
os.environ['DJANGO_SETTINGS_MODULE'] = 'simon_project.settings'

from simon_project.settings import NEWRELIC
import newrelic.agent
newrelic.agent.initialize(NEWRELIC)


# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

