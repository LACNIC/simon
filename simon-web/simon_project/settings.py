# Django settings for simon_project project.
import os
import socket
import passwords
from datetime import datetime

# Passwords stored in env. variables or passwords.py file
# Env. variable syntax: SIMON_<>
DBNAME = os.environ.get("SIMON_%s" % 'DBNAME', passwords.DBNAME)
DBUSER = os.environ.get("SIMON_%s" % 'DBUSER', passwords.DBUSER)
DBPASSWORD = os.environ.get("SIMON_%s" % 'DBPASSWORD', passwords.DBPASSWORD)
DBHOST = os.environ.get("SIMON_%s" % 'DBHOST', passwords.DBHOST)
DBPORT = os.environ.get("SIMON_%s" % 'DBPORT', passwords.DBPORT)

ADMINS = (
#           ('Carlos Martinez', 'carlos@lacnic.net'),
)

MANAGERS = ADMINS

# application version
APP_VERSION = "1.4"
DATE_UPDATED = "Tue Jul 29 12:35:34 UYT 2014"

PROJECT_ROOT = os.path.abspath(os.path.pardir)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

SIMON_URL = ''
v6_URL = ''
v4_URL = ''
# LACNIC's resources
v4resources = ["177.0.0.0/8", "179.0.0.0/8", "181.0.0.0/8", "186.0.0.0/8", "187.0.0.0/8", "189.0.0.0/8", "190.0.0.0/8", "191.0.0.0/8", "200.0.0.0/8", "201.0.0.0/8"]
v6resources = ["2001:1200::/23", "2800:0000::/12"]

# Admin's email address
# Offline test points, new WEB points and new NTP points will be anounced here
EMAIL_HOST = passwords.EMAIL_HOST
EMAIL_PORT = passwords.EMAIL_PORT
EMAIL_HOST_USER = passwords.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = passwords.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = passwords.EMAIL_USE_TLS
DEFAULT_FROM_EMAIL = passwords.DEFAULT_FROM_EMAIL
SERVER_EMAIL = passwords.SERVER_EMAIL

TESTPOINT_OFFLINE_OCCURRENCES = 3  # number of times a test point is allowed to be reported offline before an alarm is triggered
TOKEN_TIMEOUT = 60  # in minutes
TOKEN_LENGTH = 32  # number of digits for the token

# Queries to do when retrieveing statistical data.
# For biga data sets, raw queries are faster than Django-level filters.
TABLES_QUERY = 'SELECT MIN(min_rtt), MAX(max_rtt), AVG(ave_rtt), AVG(dev_rtt), SUM(number_probes), AVG(median_rtt), SUM(packet_loss) FROM simon_app_results WHERE (country_origin=%s) AND (country_destination=%s) AND (ip_version=%s) AND (date_test BETWEEN %s AND NOW()) AND (tester=%s) AND (tester_version=%s) AND (number_probes IS NOT NULL)'  # AND (testype=%s) 
THROUGHPUT_TABLES_QUERY = 'SELECT AVG(time), AVG(size), COUNT(*), SUM(size), SUM(time), STDDEV(size / time ) FROM simon_app_throughputresults WHERE (((country_origin=%s) AND (country_destination=%s)) OR((country_origin=%s) AND (country_destination=%s))) AND (ip_version=%s) AND (tester=%s) AND (tester_version=%s) AND (time > 0)'  # division by zero# AND (testype=%s)
MATRIX_TABLES_QUERY = 'SELECT AVG(ave_rtt) FROM simon_app_results WHERE (country_origin=%s)'  # Asymmetrical results

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Montevideo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/simon_app/static' % (PROJECT_ROOT)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Path to the geolocation files
GEOIP_PATH = '%s/geolocation' % (STATIC_ROOT)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ('js', '%s/../simon-javascript' % (PROJECT_ROOT)),
    ('.', '%s/../simon-applet/jar' % (PROJECT_ROOT))
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4dpg)uw43y9qt!0d28adewe%zfkc))k)e35=4rirn*+xe##z9z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'simon_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'simon_project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # "/home/agustinf/Escritorio/simon_project/simon_app/templates"
#     ("simon_app/templates")
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'simon_app',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
#    'filters': {
#        'require_debug_false': {
#            '()': 'django.utils.log.RequireDebugFalse'
#        }
#    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            # 'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': DBNAME,  # Or path to database file if using sqlite3.
            'USER': DBUSER,  # Not used with sqlite3.
            'PASSWORD': DBPASSWORD,  # Not used with sqlite3.
            'HOST': DBHOST,  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': DBPORT,  # Set to empty string for default. Not used with sqlite3.
        }
    }

HOSTNAME = socket.gethostname()
if HOSTNAME == 'mvuy3-labs':
    DEBUG = False
    URL_PFX = '/simon'
    UNSUBSCRIBE_TESTPOINT_URL = '%s/removetestpoint' % SIMON_URL
    ADMINS = (
          ('LACNIC Labs', 'labs@lacnic.net'),
#           ('Carlos Martinez', 'carlos@lacnic.net'),
    )
    SIMON_URL = 'http://simon.labs.lacnic.net%s' % URL_PFX
    v4_URL = 'http://simon.v4.labs.lacnic.net/cemd/getip/jsonp'
    v6_URL = 'http://simon.v6.labs.lacnic.net/cemd/getip/jsonp'
else:
    # Developer mode
    DEBUG = True
    URL_PFX = ''
    UNSUBSCRIBE_TESTPOINT_URL = '/removetestpoint'
#     MEDIA_ROOT = '/Users/agustin/Desktop'
    SIMON_URL = 'http://192.168.1.106'
    v4_URL = 'http://simon.v4.labs.lacnic.net/cemd/getip/jsonp'
    v6_URL = 'http://simon.v6.labs.lacnic.net/cemd/getip/jsonp'
TEMPLATE_DEBUG = DEBUG