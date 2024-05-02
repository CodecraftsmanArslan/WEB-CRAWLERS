"""Import required library"""
import traceback,sys,time, requests
from bs4 import BeautifulSoup
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV
from selenium.webdriver.common.by import By


meta_data = {
    'SOURCE' :'Agjencia e Regjistrimit të Bizneseve Kosovo (ARBK)',
    'COUNTRY' : 'Kosovo',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://arbk.rks-gov.net/page.aspx?id=2,1", 
                        "Source Description": "The Agjencia e Regjistrimit të Bizneseve Kosovo (ARBK) serves as the central authority for business registration and regulation in Kosovo. Its primary role is to facilitate the establishment and operation of businesses by providing efficient and transparent registration services."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://arbk.rks-gov.net/page.aspx?id=2,1'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Kosovo Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
START_ID = int(arguments[1]) if len(arguments)>1 else 1

kosovo_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  kosovo_crawler.get_requests_helper()
seasion = kosovo_crawler.get_requests_session()
selenium_helper = kosovo_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=False,Nopecha=False, timeout=200)

driver.get('https://arbk.rks-gov.net/TableSearch')
time.sleep(5)

search_id_number = driver.find_elements(By.CLASS_NAME,'mantine-gszoqu')[1]
search_id_number.send_keys('810363292')

click_search = driver.find_element(By.CLASS_NAME,'mantine-UnstyledButton-root')
click_search.click()
time.sleep(10)
search_table = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div[2]/div/div/table/tbody/tr/td[1]')
search_table.click()
input()