from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

selenium = '/Users/agustin/Desktop/selenium/'

desired_cap = {'browser': 'Chrome', 'browser_version': '32.0', 'os': 'Windows', 'os_version': 'XP', 'resolution': '1024x768'}

desired_cap['browserstack.tunnel'] = True
desired_cap['browserstack.debug'] = True

driver = webdriver.Remote(command_executor='http://desarrolloenlacn:4y2eYr1zgpHmH9mzq7Vp@hub.browserstack.com:80/wd/hub', desired_capabilities=desired_cap)



driver.get('http://localhost:8000/d3')

for i in range(150):
    cuerpo = driver.find_element_by_id('cuerpo')
    data = cuerpo.get_attribute("innerHTML")
    
    filename = '%s%s%s%s%s.txt' % (selenium, desired_cap['os'], desired_cap['os_version'], desired_cap['browser'], desired_cap['browser_version'])
    f = open(filename, 'w')
    data = str(data).replace('<BR>', '\n')
    data = str(data).replace('<br>', '\n')
    f.write(data)
    
    print '%.2f' % (100 * i / 150.0)
    sleep(80)

driver.quit()