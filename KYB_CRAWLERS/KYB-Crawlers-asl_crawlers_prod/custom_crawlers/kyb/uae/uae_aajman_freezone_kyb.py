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
    meta_detail['aliases'] = record[1]
    meta_detail['license_state_date'] = record[2]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.uae_aajman_freezone_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_aajman_freezone_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
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

        JSON_URL = "https://eportal.secure.force.com/AFZExternal/VF_DataSetReportJSON?reportName=companyName&isJSON=true"

        response = requests.get(JSON_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_data = response.json()

        DATA = []
        for item in json_data:
            company_name = item.get('Company Name').replace("'","")
            aliases = item.get('Company Name - Arabic').replace("'","") if item.get('Company Name - Arabic') else ""
            license_state_date = item.get('License State Date').replace("'","")
            
            DATA.append([company_name, aliases, license_state_date])
            record = [company_name, aliases, license_state_date]

            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            if record_for_db[1] != "":
                print("Stored record.")
                crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for UAE Aajman Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name = "Aajman Freezone"
    description = "This is the website of the Ajman Freezone. It provides the list of companies in Ajman with their License State Date."
    source_type = "HTML"
    url = "https://eportal.secure.force.com/AFZExternal/VF_DataSetReportView?reportName=companyName" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
