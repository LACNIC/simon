__author__ = 'agustin'

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

# for os in oss:
#     configs.append(build_config(chrome, os))

# for version in range(33, 43):
#     browser = build_browser('Chrome', version)
#     configs.append(build_config(browser, osx))

# browser = build_browser('IE', 10)
# configs.append(build_config(browser, windows8))

browser = build_browser('Chrome', 44)
configs.append(build_config(browser, osx))

import json


with open("browsers.json", "w") as f:
    f.write(json.dumps(configs))
    f.close()

print "Built %.0f configurations" % (len(configs))