"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime, json
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
from time import sleep

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
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def get_listed_object(record, entity_type, category_, countries):
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
    addresses_detail["type"]= "address"
    addresses_detail["address"]= record[-3].replace("'","''")
    addresses_detail["description"]= ""
    addresses_detail["meta_detail"]= {}
    
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['previous_name'] = record[3].replace("'","''")
    meta_detail['aliases'] = record[2].replace("'","''")
    meta_detail['source_url'] = record[-1].replace("'","''")
    
    # prepare addintiona detail object
    additional_detail = list()
    additional_detail.append({
        "type":"registered_agent_details",
        "data":[{
            "name":record[-3].replace("'","''")
        }]
    })

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": record[-2],
        "registration_number": record[1],
        "registration_date": "",
        "dissolution_date": "",
        "type": record[4],
        "crawler_name": "crawlers.custom_crawlers.kyb.new_hampshire_kyb",
        "country_name": "New Hampshire",
        "company_fetched_data_status": "",
        "additional_detail":additional_detail,
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{record[1]}{record[4]}{record[5]}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record, entity_type, category, country))) # data
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


def get_records(source_type, entity_type, country, category, url, name, description, pay_load):
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
        search_box = driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td[2]/input')
        search_box.send_keys("*")
        search_button = driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/input[1]')
        search_button.click()
        response = requests.post(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, json=pay_load, timeout=60)
        STATUS_CODE = response.status_code
        print(STATUS_CODE)
        
        time.sleep(5)
        page_number = 1
        print("Start")
        while True:
            data = []
            ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
            next_button = driver.find_element(By.XPATH, '//*[@id="pagination-digg"]/li[9]')
            rows = driver.find_elements(By.XPATH, '//*[@id="grid_businessList"]/tbody/tr')
            for index,row in enumerate(rows):
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text for cell in cells]
                links = row.find_elements(By.TAG_NAME,'a')
                row_data.append(links[0].get_attribute('href') if len(links) > 0 else "")
                data.append(row_data)
                print(row_data)
            
            time.sleep(30)
            next_button.click()
            page_number+=1

            # page_box = driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr[2]/td/div/table[2]/tbody/tr/td/div/ul/li[11]/input')
            # page_box.send_keys(page_number)
            # go_button = driver.find_element(By.XPATH, '//*[@id="lkGoPage"]')
            # go_button.click()
            # time.sleep(30)
            
            if page_number > 4:
                break
       
            
        data = []
        driver.close()
        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        driver.close()
        print('here')
        print(e)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Anguilla
    '''
    name = 'Georgia Corporations Division'
    description = "Online tool that allows users to search for businesses registered in Georgia. The website is provided by the Georgia Secretary of State's office and allows users to search for businesses by name, identification number, registered agent, and more."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Georgia'
    category = 'Company/SIE'
    url = 'https://ecorp.sos.ga.gov/BusinessSearch'
    pay_load = {
        'search.SearchType': 'BusinessName',
        'search.SearchValue': '*',
        'search.SearchCriteria': 'Contains'
    }

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description, pay_load)
    # logger = Logger({"number_of_records": number_of_records, "status": status,
    #                 "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    # logger.log()