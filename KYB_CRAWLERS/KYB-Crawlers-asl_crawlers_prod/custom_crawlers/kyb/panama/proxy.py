import zipfile

# 2.56.119.93
# 5074
# tkhxadjd
# j2v7232i1iyg
PROXY_HOST = 'proxy.crawlera.com'  # rotating proxy or host
PROXY_PORT = 8011 # port
PROXY_USER = '44f6d73f85da47dea6cefe15706e51c8' # username
PROXY_PASS = '' # password

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


pluginfile = 'panama/proxy_auth_plugin.zip'


def get_proxy_file():
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return pluginfile


import requests
def get_requests(url):
    status_code = -1
    try:
        res = requests.get(url)
        status_code = res.status_code
    except:
        status_code = -1

    while(res.status_code!=200):
        try:
            res = requests.get(url)
            status_code = res.status_code
        except:
            status_code = -1
        sleep(10)

    return res;
