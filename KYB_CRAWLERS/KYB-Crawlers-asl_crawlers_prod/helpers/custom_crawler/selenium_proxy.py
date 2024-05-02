import zipfile
import pathlib

def get_proxy_file(PROXY_HOST:str, PROXY_PORT:int,PROXY_USER:str,PROXY_PASS:str):
    manifest_json = """
                    {
                        "version": "1.0.0",
                        "manifest_version": 2,
                        "name": "Chrome Proxy",
                        "permissions": [
                                            "Proxy",
                                            "Tabs",
                                            "unlimitedStorage",
                                            "Storage",
                                            "<all_urls>",
                                            "webRequest",
                                            "webRequestBlocking"
                                        ],
                        "background": {
                            "scripts": ["background.js"]
                            },
                        "Minimum_chrome_version":"76.0.0"
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
                            bypassList: ["foobar.com"]
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

    pluginfile = f'{pathlib.Path(__file__).parent.resolve()}/{PROXY_HOST}-proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return pluginfile