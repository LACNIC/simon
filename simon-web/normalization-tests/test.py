__author__ = 'agustin'

import sys, json

from selenium import webdriver
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

json_name = sys.argv[1]
credentials = 'http://desarrolloenlacn:4y2eYr1zgpHmH9mzq7Vp@hub.browserstack.com:80/wd/hub'
url = 'http://localhost:8000/prueba/'

with open(json_name, "r") as f:
    obj = json.loads(f.read())

instance_config = obj[int(sys.argv[2])]
print "Test " + sys.argv[2] + " started"

# ------------------------------------------------------#
# Mention any other capabilities required in the test
config = {}
config["browserstack.debug"] = "true"
config["build"] = "parallel tests"

# ------------------------------------------------------#

config = dict(config.items() + instance_config.items())

#------------------------------------------------------#
# THE TEST TO BE RUN PARALLELY GOES HERE

try:

    print config
    driver = webdriver.Remote(command_executor=credentials,
                              desired_capabilities=config)
    driver.get(url)

    wait = WebDriverWait(driver, 1200)
    element = wait.until(EC.text_to_be_present_in_element((By.ID, 'output'), ','))

    config['data'] = [driver.find_element_by_id("output").text]
    print config

except TimeoutException:
    pass

finally:
    driver.quit()
    # sleep(20)

    #------------------------------------------------------#