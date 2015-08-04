from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException


def build_config(browser, os):
    os_ = os.copy()
    os_.update(browser)
    os_['browserstack.tunnel'] = True
    os_['browserstack.debug'] = True
    return os_

def build_browser(browser_name, version):
    return dict(
        browser=browser_name,
        browser_version=version
    )

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


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

ie6 = dict(
    browser='IE',
    browser_version='6'
)

ie7 = dict(
    browser='IE',
    browser_version='7'
)

ie8 = dict(
    browser='IE',
    browser_version='8'
)

ie9 = dict(
    browser='IE',
    browser_version='9'
)

ie10 = dict(
    browser='IE',
    browser_version='10'
)

ie11 = dict(
    browser='IE',
    browser_version='11'
)

browsers = [chrome, firefox, ie6, ie7, ie8, ie9, ie10, ie11]

# OSes
windows7 = dict(
    os='Windows',
    os_version='7'
)

windows8 = dict(
    os='Windows',
    os_version='8'
)

windows_xp = dict(
    os='Windows',
    os_version='XP'
)

osx = dict(
    os='OS X',
    os_version='Yosemite'
)

oss = [windows7, windows8, windows_xp, osx]


# Build configs

configs = []

# for browser in [ie6, ie7]:
# configs.append(build_config(browser, windows_xp))
# for browser in [ie8, ie9, ie10, ie11]:
# configs.append(build_config(browser, windows7))
# for browser in [ie10]:
# configs.append(build_config(browser, windows8))

for os in oss:
    configs.append(build_config(chrome, os))

# for version in range(33, 43):
#     browser = build_browser('Chrome', version)
#     configs.append(build_config(browser, osx))

# browser = build_browser('IE', 10)
# configs.append(build_config(browser, windows8))



for config in configs:
    try:
        driver = webdriver.Remote(command_executor=credentials,
                                  desired_capabilities=config)
        try:
            driver.get(url)

            wait = WebDriverWait(driver, 1200)
            element = wait.until(EC.text_to_be_present_in_element((By.ID, 'output'), ','))

            config['data'] = [driver.find_element_by_id("output").text]
            print config

        except TimeoutException:
            continue

        finally:
            driver.quit()
    finally:
        driver.quit()
        sleep(20)