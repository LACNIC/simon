from selenium import webdriver
from time import sleep
from simon_app.models import *

credentials = 'http://desarrolloenlacn:4y2eYr1zgpHmH9mzq7Vp@hub.browserstack.com:80/wd/hub'
url = 'http://localhost:8000/prueba/'

# Browsers
chrome = dict(
    browser='Chrome',
    browser_version='39'
)

firefox = dict(
    browser='Firefox',
    browser_version='35'
)

ie = dict(
    browser='IE',
    browser_version='11'
)

browsers = [chrome, firefox, ie]

# Windows 7
windows7 = dict(
    os='Windows',
    os_version='7'
)

# Load configs
configs = []
print browsers
for b in browsers:
    windows7.update(b)
    print windows7
    configs.append(windows7)

# Delete previous Results
rs = Results.objects.filter(ip_destination='200.3.14.147')
for r in rs:
    r.delete()

try:
    for config in configs:
        config['browserstack.tunnel'] = True
        config['browserstack.debug'] = True

        driver = webdriver.Remote(command_executor=credentials,
                                  desired_capabilities=config)
        driver.get(url)

        for time in [50, 50, 50]:
            driver.find_element_by_tag_name("body")
            sleep(time)  # 100 samples + connection time = 150 sec
except:
    pass
finally:
    driver.close()

# At his moment, results are stored in the database

print Results.objects.filter(ip_destination='200.3.14.147')