"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
from langdetect import detect
from dotenv import load_dotenv
from selenium import webdriver
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from helpers.crawlers_helper_func import CrawlersFunctions

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

'''DRIVER CONFIGURATION'''
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def googleTranslator(record_):
    """Description: This method is used to translate any language to english. It take name as input and return the translated name
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'","").replace('\"',"").replace('\n',',')
        
    except:
        return record_

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @return dict
    '''
    # preparing meta_detail dictionary object
    meta_detail = dict()
   
    meta_detail['business_type'] = googleTranslator(record[1].replace("'",""))
    meta_detail['number_of_employees'] = record[-1].replace("'","''")
    meta_detail['company_information'] = googleTranslator(record[2].replace("'","''").replace("\n","''"))
    meta_detail['contact_information'] = record[3].replace("'","''").replace("\n","''")
    meta_detail['alias'] = record[0].replace("'","''")
    
    address_details = dict()
    address_details['type'] = "address_detail"
    address_details['description'] = ""
    address_details['address'] = ""
    address_details['meta_detail'] = {
        "jurisdiction":googleTranslator(record[4]),
        "street": googleTranslator(record[5]),
        "city":googleTranslator(record[6]),
        "locality":googleTranslator(record[-3]),
        "building":googleTranslator(record[-2])
    }
    # create data object dictionary containing all above dictionaries
    
    data_obj = {
        "name":googleTranslator(record[0].replace("'","")),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.iraq.iraq_kyb1",
        "country_name": "Iraq",
        "company_fetched_data_status": "",
        "addresses_detail":[address_details],
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
    data_for_db.append(shortuuid.uuid(record[0]+record[1]+'iraq_kyb1'+url_)) # entity_id
    data_for_db.append(googleTranslator(record[0].replace("'", ""))) #name
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME, driver
        SOURCE_URL = url
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=300)
        STATUS_CODE = response.status_code

        if STATUS_CODE != 200:
            for i in range(int(os.getenv('NO_OF_PROXIES'))):
                http_proxy = os.getenv('HTTP_PROXY_' + str(i+1))
                https_proxy = os.getenv('HTTPS_PROXY_'+str(i+1))
                options.add_argument('--proxy-server=' + http_proxy)
                options.add_argument('--proxy-server=' + https_proxy)
        
        driver.get(SOURCE_URL)
        
        DATA_SIZE = len(driver.page_source)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        driver.implicitly_wait(2)
        DATA = [] 
        try:
            heading_name = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[4]/h3/b').text.strip()
            try:
                btype = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[4]/p').text.strip()
            except:
                btype = ""
            compnay_info = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[8]').text.strip()
            contact_info = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[10]').text.strip()
            
            table = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[6]/table')
            rows = table.find_elements(By.XPATH, './/tr')
            for index,row in enumerate(rows):
                cells = row.find_elements(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[6]/table/tbody/tr/td/strong")
                row_data = [cell.text for cell in cells]
                Jurisdiction = row_data[0]
                Street = row_data[4]
                City = row_data[2]
                Location = row_data[3]
                Building = row_data[5]
                number_of_employees = row_data[-2]
                DATA.append([heading_name,btype,compnay_info,contact_info,Jurisdiction,Street,City,Location,Building, number_of_employees])
        except:
            pass

        for data in DATA:      
            record_for_db = prepare_data(data, category,country, entity_type, source_type, name, url, description)
            query = """INSERT INTO reports_test (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports_test.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports_test.image THEN reports_test.image || '{6}'::jsonb ELSE reports_test.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("stored in database\n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Iraq
    '''
    name = 'Iraqi International Trade Point'
    description = "One of the departments of the Private Sector Development Department affiliated to the Ministry of Commerce. It was established to provide informational and technical support to businessmen and investors"
    entity_type = 'Company/ Organisation'
    source_type = 'HTML'
    countries = 'Iraq'
    category = 'Free Zones/ Investment Promotion'
    for i in range(18,4733):
        url = "https://iitp.mot.gov.iq/Home/CompanyProfile?Id="+str(i)
        print(url)
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
