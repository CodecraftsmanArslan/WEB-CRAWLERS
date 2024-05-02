"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
from bs4 import BeautifulSoup
import pandas as pd
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from helpers.crawlers_helper_func import CrawlersFunctions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from deep_translator import GoogleTranslator

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
# options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        max_chunk_size = 5000  # Maximum chunk size for translation
        translated_chunks = []
        
        if len(record_) <= max_chunk_size:
            # If the record is within the limit, translate it as a whole
            translated_record = GoogleTranslator(source='auto', target='en').translate(record_)
            translated_chunks.append(translated_record)
        else:
            # Split the record into smaller chunks and translate them individually
            chunks = [record_[i:i + max_chunk_size] for i in range(0, len(record_), max_chunk_size)]
            for chunk in chunks:
                translated_chunk = GoogleTranslator(source='auto', target='en').translate(chunk)
                translated_chunks.append(translated_chunk)
        
        translated_record = ' '.join(translated_chunks)
        return translated_record.replace("'", "''").replace('"', '')
    
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        time.sleep(2)
        return record_

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''
    meta_detail = dict()
    meta_detail['aliases'] = record[2].replace('\"','"')

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": googleTranslator(record[2].replace("'","''")),
        "status": googleTranslator(record[4]),
        "registration_number": record[0],
        "registration_date": record[3].replace(".", "-"),
        "tax_number": record[1],
        "crawler_name": "crawlers.custom_crawlers.kyb.tajikstan.tajikistan_kyb",
        "country_name": "Tajikistan",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-tajikistan_kyb')) # entity_id
    data_for_db.append(googleTranslator(record[2].replace("'", ""))) #name
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
        SOURCE_URL = url

        LEGAL_URLs = [
            "https://registry.andoz.tj/legal.aspx?lang=en",
            "https://registry.andoz.tj/physical.aspx?lang=en",
        ] 
        
        DATA = []
        for LEGAL_URL in LEGAL_URLs:
            driver.get(LEGAL_URL)
            response = requests.get(LEGAL_URL, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}, 
                verify=False, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            
            time.sleep(5)
            driver.find_element(By.ID, "ASPxButton1_CD").click()

            page_number = 1
            while True:
                print("Page Number: ", page_number)
                time.sleep(5)
                next_page = driver.find_elements(By.CSS_SELECTOR, 'td.dxpButton_Office2003Blue')[1]
                
                if  'disabled' in str(next_page.get_attribute('class')).lower():
                    break

                rows = driver.find_elements(By.CSS_SELECTOR, "tr.dxgvDataRow_Office2003Blue")
                for row in rows:
                    columns = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(columns) == 5:
                        record = [col.text for col in columns]

                        DATA.append(record)
                        record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                                    
                        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                        
                        if record_for_db[1] != "":
                            print("Stored record.")
                            crawlers_functions.db_connection(query)

                next_page.click()
                page_number+=1
                time.sleep(10)
                
        driver.close()
        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        driver.close()
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Tajikistan
    '''
    countries = "Tajikistan"
    entity_type = "Company/Organization"
    category = "Official Registry"    
    name = "Unified State Register of taxpayers (Tajikistan)"
    description = "The webpage is intended for taxpayers in Tajikistan to access information related to their tax registration and status, including obtaining their taxpayer identification number (EIN/INN), submitting tax returns and payments, and reviewing their tax history. The website may offer resources such as forms, instructions, and contact information for assistance with tax-related issues."
    source_type = "HTML"
    url = "https://www.andoz.tj/ForTaxpayer/UnifiedStateRegister" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
