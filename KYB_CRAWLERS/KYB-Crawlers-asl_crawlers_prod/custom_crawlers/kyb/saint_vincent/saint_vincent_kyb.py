"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
from langdetect import detect
from selenium import webdriver
from dotenv import load_dotenv
from helpers.logger import Logger
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
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


def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    @param record
    @return dict
    ''' 
    
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[0].replace("'","''"),
        "status": record[3],
        "registration_number": record[1],
        "registration_date": "",
        "incorporation_date":record[4],
        "dissolution_date": "",
        "type": record[2].replace("'","''"),
        "crawler_name": "crawlers.custome_crawlers.kyb.saint_vincent.saint_vincent_kyb",
        "country_name": "Saint Vincent and the Grenadines",
        "company_fetched_data_status": "",
        "people_detail":[{
            "designation":"registered_agent",
            "name":record[5].replace("'","''")
        }],
        "meta_detail": {}
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
    data_for_db.append(shortuuid.uuid(f'{record[1]}-{record[4]}-saint_vincent_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([record[4]])) #dob
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
        total_data_size = 0
        while True:
            data = []
            # Get the table element containing the search results
            table = driver.find_element(By.XPATH,'/html/body/div[2]/div[4]/div/div/main/div/div/div/div[3]/div/div/div/div[2]/div/div/table')
            # Find all the rows in the table
            rows = table.find_elements(By.XPATH, './/tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text for cell in cells]
                data.append(row_data)
            # Print the current page number
            print(f"Page {page_number}")
            # Find the "next" button and click it
            next_button = driver.find_element(By.CLASS_NAME, "next")
            # Increment the page number
            page_number += 1
            for record_ in data[1:]:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                insertion_data, lang = crawlers_functions.check_language(
                    record_for_db, source_type, url, description, name)
        
                if lang == 'en':
                    crawlers_functions.language_handler(insertion_data, 'reports')
                    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
                else:
                    query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                        *insertion_data)
                   
                crawlers_functions.db_connection(query)
            total_data_size += len(data)
            next_btn_classes = next_button.get_attribute('class')
            if next_btn_classes.find('disabled')!=-1:
                break
            else:
                next_button.click()        
        driver.close()
        return total_data_size, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Saint Vincent
    '''
    name = 'Financial Services Authority (FSA)'
    description = "Financial Services Authority (FSA) of St . Vincent and the Grenadines. The FSA is responsible for overseeing and regulating financial services in the country, including the licensing and oversight of international forex and trading brokers."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Saint Vincent and the Grenadines'
    category = 'Official Registry'
    url = 'https://svgfsa.com/company-name-search/'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
