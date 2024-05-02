"""Set System Path"""
import sys
from pathlib import Path
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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from helpers.crawlers_helper_func import CrawlersFunctions
from selenium.webdriver.chrome.service import Service

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

service = Service(ChromeDriverManager(os.getenv('CHROME_VERSION')).install())
# driver = webdriver.Chrome(options=options)

driver = webdriver.Chrome(service=service, options=options)

arguments = sys.argv
PAGE_NUMBER = int(arguments[1]) if len(arguments)>1 else 1

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''

    # create data object dictionary containing all above dictionaries
    people_detail=[
                {
                "designation":"registered_agent",
                "name":record[-2],
                "address":record[-1]
                } if record[-2] != '' else None
                ]
             
    people_detail = [c for c in people_detail if c]      
    
    data_obj = {
        "name":record[1].replace("'","''"),
        "status": record[3],
        "registration_number": record[0],
        "registration_date": "",
        "incorporation_date":record[4],
        "dissolution_date": record[-3],
        "type": record[2],
        "crawler_name": "crawlers.custom_crawlers.kyb.marshall_islands.marshall_islands_kyb",
        "country_name": "Marshall Islands",
        "company_fetched_data_status": "",
        "people_detail":people_detail,
        "meta_detail":{
            "annulment_date":record[5]
        }
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-marshall_islands')) # entity_id
    data_for_db.append(record[1].replace("'", "")) #name
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


def get_data(driver, page_number):
    """
    Description: This method returns a list of objects that have all the information
    @param driver:
    @param page_number
    @return: data:list
    """
    data = []
    for i in range(0,15):
        # Find the elements with the specified XPath and click on the i-th element
        entity_number_click = driver.find_elements(By.XPATH, '/html/body/div[2]/form/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[4]/div[2]/div[3]/div/div[2]/table/tbody/tr/td[1]/span/a')
        entity_number_click[i].click()
        time.sleep(10)
        # Get the required data from different elements and strip any leading/trailing whitespace
        if len(driver.find_elements(By.ID,'pt1:r1:2:it1::content')) == 0:
            continue
        entity_number = driver.find_element(By.ID,'pt1:r1:2:it1::content').text.strip()
        entity_name_ = driver.find_element(By.ID, 'pt1:r1:2:it2::content').text.strip()
        entitytype = driver.find_element(By.ID,'pt1:r1:2:it3::content').text.strip()    
        status = driver.find_element(By.ID,'pt1:r1:2:it4::content').text.strip()    
        existen_data = driver.find_element(By.ID,'pt1:r1:2:it6::content').text.strip()    
        annulment_date = driver.find_element(By.ID, 'pt1:r1:2:it9::content').text.strip()
        dissolution_date = driver.find_element(By.ID, 'pt1:r1:2:it10::content').text.strip()
        agent_name = driver.find_element(By.ID, 'pt1:r1:2:it28::content').text.strip()
        aggent_address = driver.find_element(By.ID, 'pt1:r1:2:it29::content').text.strip()
        data.append([entity_number, entity_name_,entitytype,status,existen_data,annulment_date,dissolution_date,agent_name,aggent_address])
        # Click the search result button
        if len(driver.find_elements(By.ID, 'pt1:r1:2:b2')) == 0:
            continue
        searc_resutl_button = driver.find_element(By.ID, 'pt1:r1:2:b2')
        searc_resutl_button.click()
        time.sleep(8)
        #  Find the page input element and clear its content
        if len(driver.find_elements(By.ID,"pt1:r1:1:t1::nb_in_pg")) == 0:
            continue
        page_input = driver.find_element(By.ID,"pt1:r1:1:t1::nb_in_pg")
        page_input.clear()
        # Enter the page number and press ENTER to load the next page
        page_input.send_keys(str(page_number))
        page_input.send_keys(Keys.ENTER)
        time.sleep(5)

    return data

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
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(driver.page_source)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        time.sleep(5)
        page_number = PAGE_NUMBER
        entity_name = driver.find_elements(By.CLASS_NAME,'x25')[1]
        entity_name.send_keys('____')
        entity_type_ = Select(driver.find_element(By.CLASS_NAME,'x2h'))
        entity_type_.select_by_visible_text('Corporation')
        search_button = driver.find_element(By.ID,'pt1:r1:0:b1')
        search_button.click()
        time.sleep(5)
        while True:
            try:
                page_input = driver.find_element(By.ID,"pt1:r1:1:t1::nb_in_pg")
                page_input.clear()
            except:
                page_input = driver.find_element(By.ID,"pt1:r1:1:t1::nb_in_pg")
                time.sleep(8)
                page_input.clear()

            if page_number == 7947:
                break
            
            page_input.send_keys(str(page_number))
            page_input.send_keys(Keys.ENTER)
            time.sleep(8)
            
            data = get_data(driver, page_number)
            
            for record_ in data:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                print("Stored record\n")
                crawlers_functions.db_connection(query)
            print(f"Page {page_number}")
            # Increment the page number
            page_number += 1
            
        driver.close()
        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Marshall Islands
    '''
    name = 'International Registries, Inc'
    description = "International Registries, Inc. and its affiliates (IRI) provide administrative and technical support to the Republic of the Marshall Islands (RMI) Maritime and Corporate Registries. IRI has been administering maritime and corporate programs and involved in flag State administration since 1948."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Marshall Islands'
    category = 'Official Registry'
    url = 'https://resources.register-iri.com/CorpEntity/Corporate/Search'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()