"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json, os, re
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver


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

def create(record_, source_type, entity_type, country, category, url, name, description):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
        print(record_for_db)
        print("Stored record\n")
        crawlers_functions.db_connection(query)
    else:
        print("Something went wrong")


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
    data_for_db.append(shortuuid.uuid(f"{record['Entity Id']}{url_}-new_jersey_kyb")) # entity_id
    data_for_db.append(record['Business Name'].replace("'", "''")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'",""), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record))) # data
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
    meta_detail = {}
    if record['City'] is not None and record['City'].replace("NONE", "").replace("None", "").replace("none", "").replace("NULL", "").replace("Null", "").replace("null", "") != "":
        meta_detail['city'] = record['City'].replace("'","''")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": re.sub(r'\s+', ' ', record['Business Name'].replace("'", "''")) if 'Business Name' in record else "",
        "registration_number": record['Entity Id'],
        "incorporation_date": record['Incorporated Date'].replace("/", "-") if 'Incorporated Date' in record else "",
        "meta_detail": meta_detail,
        "type": record['Type'].replace("\n","") if 'Type' in record else "",
        "crawler_name": "custom_crawlers.kyb.new_jersey.new_jersey_kyb",
        "country_name": "New Jersey",
    }
    
    return data_obj

def get_cookies_and_token():
    res = requests.get('https://www.njportal.com/DOR/BusinessNameSearch/Search/EntityId')
    soup = BeautifulSoup(res.text, 'html.parser')
    token_el = soup.find('input', {'name': '__RequestVerificationToken'})
    data = {
                'cookies': res.cookies.get_dict(),
                '__RequestVerificationToken': token_el.get('value')
            }
    return data


def get_page_data(url, number, cookie, verification_token):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie,
        'Host': 'www.njportal.com'
    }

    # print(headers)
    data = {
        '__RequestVerificationToken': verification_token,
        'EntityId': number
    }

    response = requests.post(url, headers=headers, data=data)

    print(response.status_code)  # Check the response status code

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table')
    headers = [th.text for th in table.find_all('th')]
    rows = []

    for row in table.find_all('tr'):
        data = [td.text for td in row.find_all('td')]
        if data:
            rows.append(dict(zip(headers, data)))

    return rows


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
        D = get_cookies_and_token()
        token = D['__RequestVerificationToken']
        cookie_token = [D['cookies'][key] for key in D['cookies'].keys() if key.find('__RequestVerificationToken')!=-1][0]
        cookie_name = [key for key in D['cookies'].keys() if key.find('__RequestVerificationToken')!=-1][0]
        cookie_ = f'{cookie_name}={cookie_token};'

        numbers = []
                # Check if a command-line argument is provided
        if len(sys.argv) > 1:
            start_number = int(sys.argv[1])
        else:
            # Assign a default value if no command-line argument is provided
            start_number = 100000001

        numbers += [f"0{i:07}" for i in range(100000001, 100999999)]
        numbers += [f"0{i:07}" for i in range(400000001, 400759254)]
        numbers += [f"0{i:07}" for i in range(600000001, 600480661)]
        
        for number in numbers:
            if start_number > int(number):
                continue
            print('Entity Id: ', number)
            items = get_page_data(url, number, cookie_, token)
            for item in items:
                if 'Entity Id' in item:
                    DATA_SIZE += 1
                    create(item, source_type, entity_type, country, category, url, name, description)
            


        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","")
    

if __name__ == '__main__':
    '''
    Description: Crawler New Jersey
    '''
    name = "New Jersey Portal"
    description = "The New Jersey Portal is an official online platform that serves as a central hub for accessing various services and information related to the state of New Jersey, USA. It provides a wide range of resources for residents, businesses, and visitors to access government services, conduct transactions, and find important information."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'New Jersey'
    category = 'Official Registry'
    url = "https://www.njportal.com/DOR/BusinessNameSearch/Search/EntityId"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
