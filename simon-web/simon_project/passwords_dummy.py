EMAIL_USE_TLS = True

# EMAIL_HOST = 'mail.lacnic.net.uy'
# EMAIL_PORT = 993
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# SERVER_EMAIL = '@lacnic.net'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '@gmail.com'
EMAIL_HOST_PASSWORD = ''
SERVER_EMAIL = '@gmail.com'

DEFAULT_FROM_EMAIL = "@lacnic.net"

DBNAME = 'simon'
DBUSER = 'postgres'
DBPASSWORD = 'postgres'
DBHOST = '127.0.0.1'
DBPORT = '5432'

PROBEAPI = ""
KONG_API_KEY = ""
IMPORTIO_API_KEY = ""

TWITTER = {
           'consumer_key' : '',
           'consumer_secret' : '',
           'access_token' : '',
           'access_token_secret' : ''
           }
