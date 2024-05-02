"""Set System Path"""
import sys
from pathlib import Path
# sys.path.append('/Users/tayyabali/Desktop/work/ASL-Crawlers')
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import pandas as pd
import requests, json,os
from langdetect import detect
from selenium import webdriver
from dotenv import load_dotenv
from helpers.logger import Logger
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import Select
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
# options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @param countries
    @param category_
    @param entity_type
    @return dict
    '''
    # preparing addresses_detail dictionary object
    addresses_detail = dict()
    addresses_detail["type"]= "general_address"
    addresses_detail["address"]= record[-4].replace("'","''")
    addresses_detail["description"]= ""
    addresses_detail["meta_detail"]= {}
    
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['last_annual_return'] = record[-3].replace("'","''")
    meta_detail['legal_authority'] = record[-1].replace("'","''")
    meta_detail['category'] = record[4].replace("'","''")
    meta_detail['aliases'] = record[3].replace("'","''")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[2].replace("'","''"),
        "status": record[-2],
        "registration_number": record[0],
        "registration_date": str(pd.to_datetime(record[1])),
        "dissolution_date": "",
        "type": record[5],
        "crawler_name": "crawlers.custom_crawlers.kyb.anguilla.anguilla_kyb",
        "country_name": "Anguilla",
        "company_fetched_data_status": "",
        "addresses_detail": [addresses_detail],
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-anguilla_kyb')) # entity_id
    data_for_db.append(record[2].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[1]))])) #dob
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
        driver.get(SOURCE_URL)
        response = requests.get(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(driver.page_source)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        driver.implicitly_wait(2)
        page_number = 1
        select = Select(driver.find_element(By.XPATH,'//*[@id="list.list"]/div/div[3]/div[1]/span[3]/select'))
        select.select_by_visible_text('100')
        time.sleep(5)
        while True:
            data = []
            # ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="list.list"]/div/table')))
            table = driver.find_element(By.XPATH,'//*[@id="list.list"]/div/table')
            # Find the "next" button and click it
            next_button = driver.find_element(By.CLASS_NAME, "jtable-page-number-next")
            next_btn_classes = next_button.get_attribute('class')
            driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight);", next_button)
            rows = table.find_elements(By.XPATH, './/tr')
            print(len(rows))
            for index,row in enumerate(rows):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                except:
                    time.sleep(2)
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                    except:
                        continue
                row_data = [cell.text for cell in cells]
                data.append(row_data)
            print("i came here 1")
            for record_ in data[1:]:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                if record_for_db[1].replace(' ', '') != '':
                    crawlers_functions.db_connection(query)
            # Print the current page number
            print(f"Page {page_number}")
            # Increment the page number
            page_number += 1
            if next_btn_classes.find('ui-state-disabled')!=-1 and next_btn_classes.find('jtable-page-number-disabled')!=-1:
                break
            next_button.click()
            # Wait for the next page to load
            time.sleep(3)
            

        driver.close()
        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Anguilla
    '''
    name = 'Anguilla Commercial Registry (ACORN)'
    description = "The Commercial Registry of Anguilla is responsible for maintaining the registration records of companies and other business entities operating in Anguilla. The registration system is called the Anguilla Commercial Online Registration Network (ACORN), and it was developed in cooperation with the Anguilla government."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Anguilla'
    category = 'Official Registry'
    url = 'https://cres.gov.ai/bereg/searchbusinesspublic'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()