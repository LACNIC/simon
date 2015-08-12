__author__ = 'agustin'

import sys, json

from selenium import webdriver
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
import datetime

json_name = sys.argv[1]
credentials = 'http://desarrolloenlacn:4y2eYr1zgpHmH9mzq7Vp@hub.browserstack.com:80/wd/hub'
url = 'http://localhost:8000/prueba/'
timeout = 1000

with open(json_name, "r") as f:
    obj = json.loads(f.read())

instance_config = obj[int(sys.argv[2])]

# ------------------------------------------------------#
# Mention any other capabilities required in the test
build = "Chrome on Windows 7 %s" % (datetime.datetime.now().strftime("%x"))

config = {}
config["browserstack.debug"] = "true"
config["build"] = build
config["date"] = str(datetime.datetime.now())

# ------------------------------------------------------#

config = dict(config.items() + instance_config.items())

#------------------------------------------------------#
# THE TEST TO BE RUN PARALLELY GOES HERE

try:

    # print config["os"], config["os_version"], config["browser"], config["browser_version"], config["date"]

    driver = webdriver.Remote(command_executor=credentials,
                              desired_capabilities=config)
    driver.get(url)

    wait = WebDriverWait(driver, 1200)
    element = wait.until(EC.text_to_be_present_in_element((By.ID, 'output'), ','))

    config["data"] = eval("list([%s])" % driver.find_element_by_id("output").text)
    config["ipv4Address"] = driver.find_element_by_id("ipv4Address").text
    config["ipv6Address"] = driver.find_element_by_id("ipv6Address").text

    print config

except Exception as e:
    print e

finally:
    driver.quit()

    filename = "results-%s.json" % (build)

    try:
        f = open(filename, "a+")
        f.write(json.dumps(config))

    finally:
        f.close()
#------------------------------------------------------#