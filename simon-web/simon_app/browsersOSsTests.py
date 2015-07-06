from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Load configs
# conne = []
for os in oss:
    for browser in browsers:

        os_ = os.copy()
        os_.update(browser)

        os_['browserstack.tunnel'] = True
        os_['browserstack.debug'] = True
        driver = webdriver.Remote(command_executor=credentials,
                                  desired_capabilities=os_)
        try:
            driver.get(url)

            wait = WebDriverWait(driver, 1200)
            element = wait.until(EC.text_to_be_present_in_element((By.ID, 'output'), ','))

            print os_
            print driver.find_element_by_id("output").text
        finally:
            driver.quit()
            sleep(20)