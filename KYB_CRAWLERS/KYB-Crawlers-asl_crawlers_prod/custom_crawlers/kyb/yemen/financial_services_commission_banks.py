"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import pandas as pd
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from deep_translator import GoogleTranslator

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def create(record_, source_type, entity_type, country, category, url, name, description):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
        
        print("Stored record\n")
        crawlers_functions.db_connection(query)
    else:
        print("Something went wrong")

def googleTranslator(record_):
    """Description: This method is used to translate any language to english. It take name as input and return the translated name
    @param record_:
    @return: translated_record
    """
    if record_:
        try:
            translated = GoogleTranslator(source='auto', target='en')
            translated_record = translated.translate(record_)
            return translated_record.replace("'","''").replace('\"',"")
        except:
            return translated_record
    return ""

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''

    # preparing summary dictionary object
    meta_detail = dict()
    meta_detail["aliases"] = record['aliases'].replace("'", "''")
    meta_detail["head_office_branch"] = record['head_office_branch'].replace("'", "''") if 'head_office_branch' in record  else ""
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['name'].replace("'", "''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custome_crawlers.kyb.financial_services_commission_bank",
        "country_name": "Yemen",
        "company_fetched_data_status": "",
        "address_details": [record["address_detail"]],
        "meta_detail": meta_detail
    }

    return data_obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''

    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f"{record['name']}{record['street']}{url_}financial_service_commission_bank")) # entity_id
    data_for_db.append(name) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')
    
    return data_for_db

def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts'
         # Set up the Selenium WebDriver (assuming you have the appropriate driver executable in your system PATH)
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # Load the webpage
        driver.get(url)
        # Find the button element
        button = driver.find_element(By.XPATH,"/html/body/form/section/section[2]/div/div/div/div[1]/div/div[3]/div/div/div[1]/details/summary/div/h4")  # Replace 'your_button_id' with the actual ID of the button
        time.sleep(3)
        # Click the button
        button.click()
        # Get the page source after the button clicks
        html_content = driver.page_source
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        complaint_table = soup.find('table', id='ComplaintSubject')
        rows = complaint_table.find_all('tr')
        for row in rows[1:]:
            item = {}
            tds = row.find_all('td')
            aliases = tds[0].text.strip()
            name_ = googleTranslator(aliases)
            head_office_branch = googleTranslator(tds[1].text.strip())
            district = googleTranslator(tds[2].text.strip())
            region = googleTranslator(tds[3].text.strip())
            street = googleTranslator(tds[4].text.strip())
            address_detail = {
                "type": "address_details",
                "description": "",
                "address": "",
                "meta_details": { "street": street, "district": district, "region": region}
            }
            item['name'] = name_
            item['aliases'] = aliases
            item['head_office_branch'] = head_office_branch
            item['address_detail'] = address_detail
            item['street'] = street
            print(item)
            DATA_SIZE += 1
            create(item, source_type, entity_type, country, category, url, name, description)

        payment = soup.find('table', id='payment')
        rows = payment.find_all('tr')
        for row in rows[1:]:
            item = {}
            tds = row.find_all('td')
            aliases = tds[0].text.strip()
            name_ = googleTranslator(aliases)
            district = googleTranslator(tds[1].text.strip())
            region = googleTranslator(tds[2].text.strip())
            street = googleTranslator(tds[3].text.strip())
            address_detail = {
                "type": "address_details",
                "description": "",
                "address": "",
                "meta_details": { "street": street, "district": district, "region": region}
            }
            item['name'] = name_
            item['aliases'] = aliases
            item['address_detail'] = address_detail
            item['street'] = street
            print(item)
            DATA_SIZE += 1
            create(item, source_type, entity_type, country, category, url, name, description)

        # Close the Selenium WebDriver
        driver.quit()

        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: CSV Crawler for Yemen
    '''
    countries = "Yemen"
    entity_type = " Company/Organisation"
    category =  "Financial Services"
    name = "Central Bank of Yemen"
    description = "The Central Bank of Yemen (CBY) is the central monetary authority and the highest financial institution in Yemen. Its primary responsibility is to implement and regulate monetary and credit policies to maintain price stability and support the overall economic stability of the country."
    source_type = "HTML"
    url = 'https://www.centralbank.gov.ye/Home/banks'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
