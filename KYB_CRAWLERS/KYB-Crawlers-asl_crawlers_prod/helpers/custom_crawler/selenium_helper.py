from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re, time, os
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from SlackNotifyKYB import SlackNotifier
from selenium.webdriver.chrome.service import Service
from selenium_proxy import get_proxy_file

load_dotenv()
notify:SlackNotifier=None
def create_driver(headless=True, window_size='1920,1080',timeout:float=30, user_agent=None, Nopecha=False,proxy=False, proxy_server=None):
    """
    Description: Creates a Selenium web driver instance with the specified configurations.
    @params:
    - headless (bool): Whether to run the browser in headless mode (default: True).
    - window_size (str): Window size in the format 'width,height' (default: '1920,1080').
    - timeout (float): Maximum time (in seconds) the driver should wait for elements to load (default: 30 seconds).
    - user_agent (str): User agent string to use for the browser (default: None).
    - Nopecha (bool): Whether to use NopeCHA extension for CAPTCHA solving (default: False).
    - proxy (bool): Whether to use a proxy server (default: False).
    - proxy_server (str): Proxy server details in the format 'host:port:user:password' (default: None).
    @return:
    - webdriver.Chrome: Chrome web driver instance with the specified configurations.
    """
    global notify
    pattern = r'^\d{3,4},\d{3,4}$'
    if user_agent is None or user_agent is True:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    
    # Configure the Selenium driver 
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-gpu')
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--dns-server=8.8.8.8")
    
    if proxy and proxy_server:
        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = proxy_server.split(':')
        PROXY_SERVER = f'{PROXY_HOST}:{PROXY_PORT}'
        options.add_argument('--proxy-server=%s' % PROXY_SERVER)
        # options.add_extension(get_proxy_file(PROXY_HOST=PROXY_HOST,PROXY_PORT=PROXY_PORT,PROXY_USER=PROXY_USER,PROXY_PASS=PROXY_PASS))
    if headless:
        options.add_argument('--headless')

    if window_size and re.match(pattern, window_size):
        options.add_argument(f'--window-size={window_size}')
    
    if user_agent and type(user_agent) == str:
        options.add_argument(f'--user-agent={user_agent}')
    
    if Nopecha:
        NOPECHA_KEY0='sub_1NdSf9CRwBwvt6ptQYIIto4Z'
        NOPECHA_KEY1='sub_1NDMOICRwBwvt6ptRRsxMdmU'
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--no-zygote')
        options.add_argument('--log-level=3')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-breakpad')

        print("Downloading NopeCHA crx extension file.")
        # Download the latest NopeCHA crx extension file.
        with open('ext.crx', 'wb') as f:
            f.write(requests.get('https://nopecha.com/f/ext.crx').content)
        options.add_extension('ext.crx')
        print('Open webdriver')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service,options=options)
        # Start the driver.
        time.sleep(5)
        # Set the subscription key for the extension by visiting this URL.
        print("Setting subscription key")
        driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY0}")
        # Go to any page with a CAPTCHA and the extension will automatically solve it.
        time.sleep(5)
        driver.set_page_load_timeout(timeout)
        return driver
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,options=options)
    driver.set_page_load_timeout(timeout)
    return driver


def wait_for_captcha_to_be_solved(browser):
    """
    Waits for the reCAPTCHA challenge to be solved in the given browser instance.
    @param:
    - browser (webdriver.Chrome): Chrome web driver instance with the reCAPTCHA challenge.
    @return:
    - webdriver.Chrome: Chrome web driver instance after successfully solving the reCAPTCHA challenge.
    """
    global notify
    while True:
        try:
            iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            browser.switch_to.frame(iframe_element)
            wait = WebDriverWait(browser, 10000)
            print('trying to resolve captcha')
            checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
            print("Captcha has been Solved")
            # Switch back to the default content
            browser.switch_to.default_content()
            return browser
        except:
            print('captcha solution timeout error, retrying...')

def setup_notify(notifier_obj:SlackNotifier):
    """
    Sets up the global notification object for sending notifications to Slack.
    @param:
    - notifier_obj (SlackNotifier): Instance of the SlackNotifier class for sending notifications.
    @return:
    - None
    """
    global notify
    notify = notifier_obj

def create_seleniumwire_driver(headless=True, window_size='1920,1080', user_agent=None, Nopecha=False,proxy=False, proxy_server=None):
    """
    Description: Creates a Selenium web driver instance with SeleniumWire support and the specified configurations.
    @params:
    - headless (bool): Whether to run the browser in headless mode (default: True).
    - window_size (str): Window size in the format 'width,height' (default: '1920,1080').
    - user_agent (str): User agent string to use for the browser (default: None).
    - Nopecha (bool): Whether to use NopeCHA extension for CAPTCHA solving (default: False).
    - proxy (bool): Whether to use a proxy server (default: False).
    - proxy_server (str): Proxy server details in the format 'host:port' (default: None).
    @return:
    - webdriver.Chrome: Chrome web driver instance with SeleniumWire support and the specified configurations.
    """
    global notify
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    service = ChromeService(executable_path=ChromeDriverManager().install())
    if user_agent is None or user_agent is True:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    # Configure the Selenium driver 
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-gpu')
    options.add_argument(f'--window-size={window_size}')
    options.add_argument('--ignore-certificate-errors')
    options_seleniumWire = {}
    if proxy and proxy_server:
        options_seleniumWire = {
            'proxy': {
                'http': f'http://{proxy_server}'
            }
        }
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(service=service,chrome_options=options,seleniumwire_options=options_seleniumWire)
    return driver
    
