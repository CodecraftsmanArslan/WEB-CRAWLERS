import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
import requests

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Ohio Secretary of State, Business Services Division',
    'COUNTRY': 'Ohio',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://businesssearch.ohiosos.gov/",
                      "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL': ' https://businesssearch.ohiosos.gov/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Ohio Official Registry",
}

Ohio_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = Ohio_crawler.get_selenium_helper()

options = uc.ChromeOptions()
# options.add_argument("user-data-dir=/Users/mohsin.raza/Library/Application Support/Google/Chrome/Profile 2")
options.add_argument(f'--proxy-server=http://69.58.9.219:7289')
# options.add_argument('--headless=true')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = uc.Chrome(version_main=114, options=options)
action = ActionChains(driver)


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments)>1 else 0

def pagination():
    if start_num > 1:
        for i in range(start_num-1):
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//li[@class="paginate_button page-item next"]/a'))
                )
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(10)
                else:
                    continue  
            except Exception as e:
                print("Error:", str(e))


time.sleep(10)
product = []



def crawl():
    for char in range(ord('a'), ord('z') + 1):
        print(f"Searching for '{chr(char)}'")
        driver.get("https://businesssearch.ohiosos.gov/")
        time.sleep(8)
        search_field = driver.find_element(By.ID, "bSearch")
        search_field.clear()
        search_field = driver.find_element(By.ID, "bSearch")
        action.move_to_element(search_field)
        action.click()
        action.perform()

        time.sleep(1)

        action.send_keys(chr(char)+"__" )
        action.send_keys(Keys.RETURN)
        action.perform()
        time.sleep(1)

        # Find and clear the previous search input
        search_button = driver.find_element(By.XPATH, '//div/input[@title="Search for all current business names"]')
        search_button.click()

        pagination()
        time.sleep(10)
        get_data()

def get_data():
   
    exp,loc="",""

    time.sleep(15)
    while True:
        d = driver.find_elements(By.XPATH, "//tbody//tr")
        
        for result in d:
            entity = result.find_element(By.XPATH, './/td[1]').text
            na = result.find_element(By.XPATH, './/td[2]').text
            typ = result.find_element(By.XPATH, './/td[3]').text
            fill = result.find_element(By.XPATH, './/td[4]').text
            formatted_date = fill.replace("/", "-")
            exp = result.find_element(By.XPATH, './/td[5]').text.replace("-","").replace("/","-") if exp is not None else ""
            stat = result.find_element(By.XPATH, './/td[6]').text
            loc = result.find_element(By.XPATH, './/td[7]').text.replace("--","") if loc is not None else ""
            sta = result.find_element(By.XPATH, './/td[9]').text
            time.sleep(5)
            base_url="https://businesssearch.ohiosos.gov?=businessDetails/"
            url = f"{base_url}{entity}"      
            driver.get(url)
            time.sleep(10)


            addresses = []
            data=dict()

            for i in range(1, 6):
                xpath = f'//div[@id="agentContent"]//p[{i}]'
                try:
                    address = driver.find_element(By.XPATH, xpath).text
                    addresses.append(address)
                except:
                    addresses.append("")

            # Store the address values in the dictionary

            data["designation"]="registered_agent"
            data["name"] = addresses[0]
            data["address"] = f"{addresses[1]} {addresses[2]}"
            data["meta_detail"] = {
                "date": addresses[3].replace("/","-"),
                "status": addresses[4]
            }


            filling_type = driver.find_element(By.XPATH, '//table[@id="filingsModal-table"]//tr//td[1]').text
            Date_of_Filing = driver.find_element(By.XPATH, '//table[@id="filingsModal-table"]//tr//td[2]').text.replace("/","-")
            Document_ID = driver.find_element(By.XPATH, '//table[@id="filingsModal-table"]//tr//td[3]').text
            Image_link = driver.find_element(By.XPATH, '//table[@id="filingsModal-table"]//tr//td[4]//a').get_attribute("href")
                
          

            OBJ = {
                "registration_number": entity,
                "name": na,
                "status": stat,
                "type": formatted_date,
                "inactive_date": exp,
                "addresses_detail": [
                    {
                    "type": "general_address",
                    "address": loc
                    }
                ],
                "people_detail":[data],
                "fillings_detail":[
                        {
                        "filing_type": filling_type,
                        "date": Date_of_Filing,
                        "filing_code": Document_ID,
                        "file_url": Image_link
                        }
                    ]
            }
           
            OBJ =  Ohio_crawler.prepare_data_object(OBJ)
            ENTITY_ID = Ohio_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = Ohio_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            Ohio_crawler.insert_record(ROW)
            driver.back()
            time.sleep(5)

        page_number = 1  # Initialize the page number

     
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@class="paginate_button page-item next"]/a'))
            )
            if next_button.is_enabled():
                print(f"Clicking Page {page_number}")
                next_button.click()
                time.sleep(10)
                page_number += 1  # Increment the page number
            else:
                print("No Next Page Button Found or Not Enabled")
                break  
        except Exception as e:
            print("Error:", str(e))


try:
    crawl()
    Ohio_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Ohio_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Ohio_crawler.db_log(log_data)


