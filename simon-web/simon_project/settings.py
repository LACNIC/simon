# Django settings for simon_project project.
import os
import socket
import passwords
from datadog import initialize
from datetime import datetime
import passwords
from subprocess import check_output

PROJECT_ROOT = os.path.abspath(os.path.pardir)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Passwords stored in env. variables or passwords.py file
# Env. variable syntax: SIMON_<variable>
try:
    DBNAME = os.environ.get("SIMON_%s" % 'DBNAME', passwords.DBNAME)
    DBUSER = os.environ.get("SIMON_%s" % 'DBUSER', passwords.DBUSER)
    DBPASSWORD = os.environ.get("SIMON_%s" % 'DBPASSWORD', passwords.DBPASSWORD)
    DBHOST = os.environ.get("SIMON_%s" % 'DBHOST', passwords.DBHOST)
    DBPORT = os.environ.get("SIMON_%s" % 'DBPORT', passwords.DBPORT)
    KONG_API_KEY = os.environ.get("SIMON_%s" % 'KONG_API_KEY', passwords.KONG_API_KEY)
except ImportError:
    DBNAME = ""
    DBUSER = ""
    DBPASSWORD = ""
    DBHOST = ""
    DBPORT = ""

ADMINS = (
    ('Agustin Formoso', 'agustin@lacnic.net')
)

PROBEAPI_ENDPOINT = "https://kong.speedcheckerapi.com:8443/ProbeAPIService/Probes.svc"

NEWRELIC = ""

datadog_options = {
    'api_key': '3474b64f0a78ff2319d54dec840bf75f',
    'app_key': '25a9d930c341034cbde1a450089346da395263d0'
}
initialize(**datadog_options)

DEBUG = True
HOSTNAME = socket.gethostname()
if 'simon' in HOSTNAME:
    DEBUG = False
    SIMON_URL = 'https://simon.lacnic.net'  # *no* trailing slash
    CHARTS_URL = "https://charts.dev.lacnic.net"  # *no* trailing slash
    LOGS = "/var/log/apache2/simon/production.log"
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '127.0.0.1:8000', '.lacnic.net', '*']
    CORS_ORIGIN_WHITELIST = (
        'simon.lacnic.net',
        'labs.lacnic.net',
        'natmeter.labs.lacnic.net',
        'warp.lacnic.net',
        'lacnic.net',
        '127.0.0.1:8000',
        'monitor.dev.lacnic.net',
        'natmeter.labs.lacnic.net'
    )
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken',
        'Access-Control-Allow-Origin'
    )
    DATADOG_DEFAULT_TAGS = ['env:prod', 'app:simon']
else:
    # Developer mode
    DEBUG = True
    SIMON_URL = "http://127.0.0.1:8000"
    # CHARTS_URL = "http://127.0.0.1:8001"
    CHARTS_URL = "https://charts.dev.lacnic.net"
    LOGS = PROJECT_ROOT + "/logs/debug.log"
    CORS_ORIGIN_ALLOW_ALL = True
    DATADOG_DEFAULT_TAGS = ['env:dev', 'app:simon']

MANAGERS = ADMINS

# application version
APP_VERSION = "1.4"
import requests, json

# r = requests.get("https://api.github.com/repos/LACNIC/simon/commits").text
DATE_UPDATED = ""  # json.loads(r)[0]["commit"]["author"]["date"]
LATEST_COMMIT = ""  # json.loads(r)[0]["sha"]

PROJECT_ROOT = os.path.abspath(os.path.pardir)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

v6_URL = ''
v4_URL = ''
# LACNIC's resources
v4resources = ["177.0.0.0/8", "179.0.0.0/8", "181.0.0.0/8", "186.0.0.0/8", "187.0.0.0/8", "189.0.0.0/8", "190.0.0.0/8",
               "191.0.0.0/8", "200.0.0.0/8", "201.0.0.0/8"]
v6resources = ["2001:1200::/23", "2800:0000::/12"]
asns = ['278', '676', '1251', '1292', '1296', '1797', '1831', '1840', '1916', '2146', '2277', '2549', '2638', '2708',
        '2715', '2716', '2739', '2904', '3132', '3141', '3449', '3454', '3484', '3487', '3496', '3548', '3551', '3556',
        '3596', '3597', '3603', '3631', '3632', '3636', '3640', '3790', '3816', '3905', '3968', '4141', '4209', '4230',
        '4242', '4244', '4270', '4387', '4493', '4535', '4914', '4926', '4944', '4964', '4967', '4995', '5005', '5633',
        '5639', '5648', '5692', '5708', '5722', '5745', '5772', '6057', '6063', '6065', '6084', '6121', '6125', '6133',
        '6135', '6147', '6193', '6240', '6306', '6332', '6342', '6400', '6429', '6458', '6471', '6487', '6495', '6503',
        '6505', '6535', '6543', '6545', '6568', '6590', '6927', '6945', '6957', '7002', '7004', '7005', '7038', '7048',
        '7049', '7056', '7063', '7080', '7087', '7120', '7125', '7137', '7149', '7157', '7162', '7167', '7173', '7184',
        '7195', '7199', '7236', '7298', '7303', '7313', '7315', '7325', '7340', '7365', '7399', '7408', '7417', '7418',
        '7437', '7438', '7465', '7727', '7738', '7803', '7890', '7906', '7908', '7927', '7934', '7953', '7965', '7974',
        '7980', '7984', '7993', '7994', '7995', '7997', '8007', '8024', '8026', '8048', '8053', '8054', '8055', '8056',
        '8065', '8066', '8096', '8140', '8141', '8151', '8163', '8167', '8178', '10269', '10277', '10285', '10293',
        '10299', '10318', '10362', '10391', '10412', '10417', '10420', '10429', '10436', '10452', '10454', '10463',
        '10476', '10479', '10481', '10495', '10502', '10531', '10560', '10569', '10586', '10600', '10605', '10606',
        '10617', '10620', '10624', '10630', '10640', '10670', '10671', '10688', '10691', '10697', '10704', '10706',
        '10715', '10733', '10757', '10778', '10785', '10795', '10824', '10834', '10841', '10847', '10875', '10881',
        '10895', '10897', '10906', '10938', '10954', '10964', '10983', '10986', '10992', '11008', '11014', '11058',
        '11063', '11081', '11083', '11087', '11097', '11136', '11172', '11193', '11237', '11242', '11256', '11271',
        '11284', '11295', '11311', '11315', '11335', '11338', '11340', '11356', '11373', '11390', '11392', '11411',
        '11415', '11419', '11431', '11432', '11451', '11497', '11498', '11514', '11519', '11556', '11562', '11571',
        '11581', '11585', '11592', '11599', '11617', '11642', '11644', '11664', '11673', '11677', '11694', '11706',
        '11750', '11751', '11752', '11786', '11801', '11802', '11815', '11816', '11830', '11835', '11844', '11888',
        '11896', '11921', '11947', '11960', '11993', '12034', '12066', '12127', '12135', '12136', '12140', '12146',
        '12150', '12248', '12252', '12264', '13316', '13318', '13353', '13357', '13381', '13424', '13440', '13459',
        '13474', '13489', '13495', '13514', '13521', '13522', '13544', '13579', '13584', '13585', '13591', '13643',
        '13679', '13682', '13761', '13774', '13835', '13874', '13878', '13914', '13929', '13934', '13935', '13936',
        '13991', '13999', '14000', '14026', '14030', '14069', '14080', '14084', '14087', '14111', '14117', '14122',
        '14178', '14179', '14187', '14204', '14231', '14232', '14234', '14249', '14259', '14282', '14285', '14286',
        '14316', '14318', '14339', '14346', '14377', '14420', '14457', '14463', '14522', '14535', '14553', '14560',
        '14571', '14624', '14650', '14664', '14674', '14708', '14709', '14723', '14754', '14759', '14769', '14795',
        '14840', '14845', '14867', '14868', '14886', '14966', '14970', '15034', '15064', '15066', '15075', '15078',
        '15107', '15125', '15151', '15180', '15201', '15208', '15236', '15241', '15252', '15256', '15274', '15311',
        '16397', '16418', '16471', '16528', '16531', '16592', '16594', '16596', '16607', '16629', '16663', '16685',
        '16689', '16701', '16712', '16732', '16735', '16736', '16742', '16762', '16772', '16780', '16814', '16847',
        '16849', '16874', '16885', '16891', '16906', '16911', '16960', '16973', '16975', '16990', '17069', '17072',
        '17079', '17086', '17108', '17126', '17147', '17182', '17205', '17208', '17222', '17249', '17250', '17255',
        '17257', '17287', '17376', '17379', '17399', '17401', '18449', '18455', '18466', '18479', '18492', '18496',
        '18532', '18547', '18576', '18579', '18592', '18644', '18667', '18678', '18734', '18739', '18782', '18809',
        '18822', '18836', '18840', '18846', '18869', '18881', '18941', '18998', '19033', '19037', '19038', '19064',
        '19077', '19089', '19109', '19114', '19169', '19180', '19182', '19192', '19196', '19200', '19228', '19244',
        '19259', '19278', '19315', '19332', '19338', '19361', '19373', '19411', '19422', '19429', '19447', '19519',
        '19553', '19582', '19583', '19611', '19632', '19688', '19723', '19731', '19763', '19767', '19863', '19873',
        '19889', '19960', '19978', '19990', '20002', '20015', '20032', '20043', '20044', '20106', '20116', '20117',
        '20121', '20142', '20173', '20191', '20207', '20244', '20255', '20256', '20266', '20297', '20299', '20305',
        '20312', '20321', '20345', '20361', '20363', '20418', '21506', '21520', '21571', '21574', '21575', '21578',
        '21590', '21599', '21603', '21612', '21614', '21674', '21692', '21741', '21753', '21756', '21765', '21768',
        '21824', '21826', '21838', '21862', '21883', '21888', '21911', '21980', '22010', '22011', '22047', '22055',
        '22080', '22085', '22092', '22122', '22128', '22129', '22133', '22148', '22177', '22185', '22227', '22250',
        '22305', '22313', '22341', '22356', '22368', '22371', '22381', '22382', '22407', '22411', '22431', '22453',
        '22501', '22508', '22515', '22529', '22541', '22548', '22566', '22628', '22661', '22678', '22689', '22698',
        '22699', '22706', '22724', '22726', '22745', '22798', '22819', '22833', '22860', '22869', '22876', '22882',
        '22884', '22889', '22894', '22908', '22924', '22927', '22975', '23002', '23007', '23020', '23031', '23074',
        '23091', '23105', '23106', '23128', '23140', '23201', '23202', '23216', '23243', '23246', '23289', '23353',
        '23360', '23382', '23383', '23416', '23487', '23488', '23495', '23541', '25607', '25620', '25701', '25705',
        '25718', '25812', '25832', '25927', '25933', '25998', '26048', '26061', '26090', '26104', '26105', '26107',
        '26118', '26119', '26136', '26162', '26173', '26194', '26210', '26218', '26317', '26418', '26426', '26434',
        '26505', '26592', '26593', '26594', '26595', '26596', '26598', '26599', '26600', '26601', '26602', '26603',
        '26604', '26605', '26606', '26607', '26608', '26609', '26610', '26611', '26612', '26613', '26614', '26615',
        '26616', '26617', '26618', '26619', '26620', '26621', '26622', '26623', '27648', '27649', '27650', '27651',
        '27652', '27653', '27654', '27655', '27656', '27658', '27659', '27660', '27661', '27662', '27663', '27664',
        '27665', '27666', '27667', '27668', '27669', '27670', '27671', '27672', '27673', '27674', '27675', '27676',
        '27677', '27678', '27679', '27680', '27681', '27682', '27683', '27684', '27686', '27687', '27688', '27689',
        '27690', '27691', '27692', '27693', '27694', '27695', '27696', '27697', '27698', '27699', '27700', '27701',
        '27702', '27704', '27705', '27706', '27708', '27709', '27710', '27711', '27712', '27713', '27714', '27715',
        '27716', '27717', '27718', '27719', '27720', '27721', '27723', '27724', '27725', '27726', '27727', '27728',
        '27729', '27730', '27731', '27732', '27733', '27734', '27735', '27736', '27737', '27738', '27739', '27740',
        '27741', '27742', '27744', '27745', '27746', '27747', '27748', '27749', '27750', '27751', '27752', '27753',
        '27754', '27755', '27756', '27757', '27758', '27759', '27760', '27761', '27762', '27763', '27764', '27765',
        '27766', '27767', '27768', '27769', '27770', '27771', '27773', '27774', '27775', '27776', '27777', '27778',
        '27779', '27780', '27781', '27782', '27783', '27784', '27785', '27786', '27787', '27788', '27789', '27790',
        '27791', '27792', '27793', '27794', '27795', '27796', '27797', '27798', '27799', '27800', '27802', '27803',
        '27804', '27805', '27806', '27807', '27808', '27809', '27810', '27811', '27812', '27813', '27814', '27816',
        '27817', '27818', '27819', '27820', '27822', '27823', '27824', '27825', '27826', '27827', '27828', '27830',
        '27831', '27832', '27833', '27834', '27835', '27836', '27837', '27838', '27839', '27841', '27842', '27843',
        '27844', '27845', '27847', '27848', '27850', '27851', '27852', '27853', '27854', '27855', '27856', '27858',
        '27859', '27860', '27862', '27864', '27865', '27866', '27867', '27868', '27870', '27871', '27872', '27873',
        '27874', '27875', '27876', '27877', '27879', '27880', '27881', '27882', '27883', '27884', '27885', '27886',
        '27887', '27888', '27889', '27890', '27891', '27892', '27893', '27894', '27895', '27896', '27897', '27898',
        '27899', '27900', '27901', '27902', '27903', '27904', '27905', '27907', '27908', '27909', '27910', '27911',
        '27912', '27913', '27914', '27915', '27916', '27917', '27918', '27919', '27920', '27921', '27922', '27923',
        '27924', '27925', '27926', '27927', '27928', '27929', '27930', '27931', '27932', '27933', '27934', '27935',
        '27936', '27937', '27938', '27939', '27940', '27941', '27942', '27943', '27944', '27945', '27946', '27947',
        '27948', '27949', '27950', '27951', '27952', '27953', '27954', '27955', '27956', '27957', '27958', '27959',
        '27960', '27961', '27962', '27963', '27964', '27965', '27966', '27967', '27968', '27969', '27970', '27971',
        '27972', '27973', '27974', '27975', '27976', '27977', '27978', '27979', '27980', '27981', '27983', '27984',
        '27986', '27987', '27988', '27989', '27990', '27991', '27992', '27993', '27994', '27995', '27996', '27997',
        '27998', '27999', '28000', '28001', '28002', '28005', '28006', '28007', '28008', '28009', '28011', '28012',
        '28013', '28015', '28017', '28018', '28019', '28020', '28021', '28022', '28023', '28024', '28025', '28026',
        '28027', '28028', '28029', '28030', '28031', '28032', '28033', '28034', '28035', '28036', '28037', '28038',
        '28039', '28040', '28041', '28043', '28044', '28045', '28046', '28047', '28048', '28049', '28050', '28051',
        '28052', '28053', '28054', '28055', '28056', '28058', '28059', '28060', '28061', '28062', '28063', '28064',
        '28065', '28066', '28067', '28068', '28069', '28070', '28071', '28072', '28073', '28074', '28075', '28076',
        '28077', '28078', '28079', '28080', '28081', '28082', '28083', '28084', '28085', '28086', '28087', '28088',
        '28089', '28091', '28092', '28093', '28094', '28095', '28096', '28097', '28098', '28099', '28100', '28101',
        '28102', '28103', '28104', '28105', '28106', '28107', '28108', '28109', '28110', '28111', '28112', '28113',
        '28114', '28115', '28116', '28117', '28118', '28119', '28120', '28121', '28122', '28123', '28124', '28125',
        '28126', '28127', '28128', '28129', '28130', '28131', '28132', '28133', '28134', '28135', '28136', '28137',
        '28138', '28139', '28140', '28141', '28142', '28143', '28144', '28145', '28146', '28148', '28149', '28150',
        '28151', '28152', '28153', '28154', '28155', '28156', '28157', '28158', '28159', '28160', '28161', '28162',
        '28163', '28164', '28165', '28166', '28167', '28168', '28169', '28170', '28171', '28172', '28173', '28174',
        '28175', '28176', '28177', '28178', '28180', '28181', '28182', '28183', '28184', '28185', '28186', '28187',
        '28188', '28189', '28190', '28191', '28192', '28193', '28194', '28195', '28196', '28197', '28198', '28199',
        '28200', '28201', '28202', '28203', '28204', '28205', '28206', '28207', '28208', '28209', '28210', '28211',
        '28212', '28213', '28214', '28215', '28216', '28217', '28218', '28219', '28220', '28222', '2822']


# Admin's email address
# Offline test points, new WEB points and new NTP points will be anounced here
try:
    EMAIL_HOST = passwords.EMAIL_HOST
    EMAIL_PORT = passwords.EMAIL_PORT
    EMAIL_HOST_USER = passwords.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = passwords.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS = passwords.EMAIL_USE_TLS
    DEFAULT_FROM_EMAIL = passwords.DEFAULT_FROM_EMAIL
    SERVER_EMAIL = passwords.SERVER_EMAIL
except ImportError:
    EMAIL_HOST = ""
    EMAIL_PORT = ""
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_USE_TLS = ""
    DEFAULT_FROM_EMAIL = ""
    SERVER_EMAIL = ""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

TESTPOINT_OFFLINE_OCCURRENCES = 10  # number of times a test point is allowed to be reported offline before an alarm is triggered
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
LANGUAGE_CODE = 'es-uy'  # 'en-us'

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
GEOIP_DATABASE = '%s/%s' % (GEOIP_PATH, "GeoLite2-City.mmdb")

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ('simon_app/js', '%s/../simon-javascript' % (PROJECT_ROOT)),
    ('.', '%s/../simon-applet/jar' % (PROJECT_ROOT))
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4dpg)uw43y9qt!0d28adewe%zfkc))k)e35=4rirn*+xe##z9z'

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
#     # 'django.template.loaders.eggs.Loader',
# )

# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.contrib.auth.context_processors.auth",
#     "django.core.context_processors.debug",
#     "django.core.context_processors.i18n",
#     "django.core.context_processors.media",
#     "django.core.context_processors.static",
#     "django.core.context_processors.tz",
#     "django.contrib.messages.context_processors.messages",
#     "simon_app.lib.helpers.simon_processor"
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# MIDDLEWARE_CLASSES = (
#     'django.middleware.csrf.CsrfViewMiddleware',
#     # 'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     # Uncomment the next line for simple clickjacking protection:
#     # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
# )

ROOT_URLCONF = 'simon_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'simon_project.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # "sslserver",
    # 'ddtrace.contrib.django',
    'simon_app',
    'corsheaders',
    'django_extensions'
)

DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'simon'
    # 'TAGS': {'env': 'dev'},
}


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
class LoggingConstants():
    location = LOGS

    class DebugLevel():
        information = "INFO"
        warning = "WARN"
        error = "ERROR"
        critical = "CRITICAL"

    class Handlers():
        from logging import StreamHandler, FileHandler
        stream = StreamHandler.__module__ + "." + StreamHandler.__name__
        file = FileHandler.__module__ + "." + FileHandler.__name__


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': LoggingConstants.DebugLevel.information,
            'class': LoggingConstants.Handlers.stream
        },
        'file': {
            'level': LoggingConstants.DebugLevel.information,
            'class': LoggingConstants.Handlers.file,
            'filename': LoggingConstants.location,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DBNAME,
        'USER': DBUSER,
        'PASSWORD': DBPASSWORD,
        'HOST': DBHOST,
        'PORT': DBPORT
    }
}

PROTOCOLS = {
    'HTTP': 'JavaScript',
    'ICMP': 'probeapi',
    'NTP': 'Applet'
}
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
