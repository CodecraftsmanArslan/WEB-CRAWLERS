"""Import required library"""
import time, sys
import traceback
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from deep_translator import GoogleTranslator
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

import os
from dotenv import load_dotenv
load_dotenv()

"""Global Variables"""

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 80000001
ENV =  {
            'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')            
        }

meta_data = {
    'SOURCE' :'Registro Único del Contribuyente (RUC)',
    'COUNTRY' : 'Paraguay',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ruc.com.py/", 
                        "Source Description": "Registro Único del Contribuyente (Unique Taxpayer Registry) in Paraguay, It is a unique identification number assigned to individuals and businesses for tax purposes by the tax authority of Paraguay, known as the Subsecretaría de Estado de Tributación (SET)."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.ruc.com.py/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Paraguay official registry"
}

    
paraguay_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  paraguay_crawler.get_requests_helper()
selenium_helper = paraguay_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=True,Nopecha=False)
wait = WebDriverWait(driver, 10) 


start_number = PAGE
end_number = 80133321
try:
    driver.get('https://www.ruc.com.py/')
    number = start_number
    while number < end_number:
        try:
            print("Searching for:",str(number))
            search_field = wait.until(EC.presence_of_element_located((By.ID, 'txt_buscar')))
            search_field.send_keys(str(number))
            time.sleep(2)
            search_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div/div[1]/button')
            search_button.click()
            time.sleep(5)
            search_field.clear()
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            time.sleep(5)
            tr = tbody.find_element(By.TAG_NAME, 'tr')
            registration_number = tr.find_element(By.TAG_NAME, 'td').text
            NAME = tr.find_elements(By.TAG_NAME, 'td')[1].text
            OBJ={
              "name":NAME,
              "registration_number":registration_number
            }
            OBJ =  paraguay_crawler.prepare_data_object(OBJ)
            ENTITY_ID = paraguay_crawler.generate_entity_id(OBJ['registration_number'])
            BIRTH_INCORPORATION_DATE =''
            ROW = paraguay_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            paraguay_crawler.insert_record(ROW)

            number += 1
        except Exception as e:
            print("An error occurred:", str(e))
            break
              
    paraguay_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    paraguay_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    paraguay_crawler.db_log(log_data)           