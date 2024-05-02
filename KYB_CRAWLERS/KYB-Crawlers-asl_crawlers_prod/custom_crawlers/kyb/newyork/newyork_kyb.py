"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
import pandas as pd
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
    # preparing additional_detail dictionary object
    
    people_detail = [
        
        {
        "designation":"registered_agent",
        "name": record["registered_agent_name"].replace("'","''").replace('\"',"").replace("NULL","").replace("NONE","").replace("#NULL",""),
        "address": str(record["registered_agent_address_1"]).replace("'","''").replace("#NULL","").replace("NULL","").replace("NONE","")+''+str(record['registered_agent_address_2']).replace("'","''")+' '+record["registered_agent_city"].replace("'","''")+' '+record["registered_agent_state"]+' '+record["registered_agent_zip"],
        "meta_detail":{}
        } if record["registered_agent_name"] != '' else None,
        
        {
            "designation": "legal_representative",
            "name":record["dos_process_name"].replace("'","''").replace('\"',"").replace("NULL","").replace("NONE","").replace("#NULL",""),
            "address": str(record["dos_process_address_1"]).replace("'","''").replace("#NULL","").replace("NULL","").replace("NONE","")+' '+str(record['dos_process_address_2']).replace("'","''")+' '+str(record["dos_process_city"]).replace("'","")+' '+str(record["dos_process_state"]).replace("'","''")+' '+record["dos_process_zip"]
        } if record["dos_process_name"] != '' else None,
        
        {
            "designation": "ceo",
            "name": record["chairman_name"].replace("'","''").replace('\"',"").replace("NULL","").replace("NONE","").replace("#NULL",""),
            "address": str(record['chairman_address_1']).replace("'","''").replace("#NULL","").replace("NULL","").replace("NONE","")+' '+str(record['chairman_address_2']).replace("'","''")+' '+str(record['chairman_city']).replace("'","''")+' '+record['chairman_state']+' '+record['chairman_zip'],
        } if record["chairman_name"] != '' else None
    ]
   
    people_detail = [c for c in people_detail if c]


    filling_detail =[
        {
        "date":str(pd.to_datetime(record['initial_dos_filing_date']))
        }
    ]

    meta_detail = {
        'county':record["county"].replace("'","''")
    }
  
    # preparing addresses_detail_lst dictionary object
    addresses_detail = [
        {
        "type" :"general_address",
        "address": str(record["location_address_1"]).replace("'", "''").replace("#NULL","").replace("NULL","").replace("NONE","")+' '+str(record["location_address_2"]).replace("'", "''").replace("#NULL","").replace("NULL","").replace("NONE","")+' '+record["location_city"].replace("'","''")+' '+record["location_state"]+' '+record["location_zip"],
        "meta_detail":{
           "location_name": record["location_name"].replace("'","''").replace('\"',"")
        }
        } if record["location_address_1"] != "" else None 
    ]
    addresses_detail  = [c for c in addresses_detail if c]
    
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['current_entity_name'].replace("'","''").replace('\"',""),
        "status": "",
        "registration_number": record['dos_id'],
        "registration_date": "",
        "dissolution_date": "",
        "jurisdiction":record['jurisdiction'].replace("'","''"),
        "type": record['entity_type'].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.newyork.newyork_kyb",
        "country_name": "New York",
        "company_fetched_data_status": "",
        "people_detail": people_detail,
        "fillings_detail":filling_detail,
        "addresses_detail": addresses_detail,
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
    data_for_db.append(shortuuid.uuid(f'{record["dos_id"]}-{record["current_entity_name"]}-{record["entity_type"]}-{record["dos_process_name"]}-{url_}')) # entity_id
    data_for_db.append(record["current_entity_name"].replace("'", "")) #name
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
        DATA = []
        i = 10000
        j = 0
        while True:
            api_url = f"https://data.ny.gov/api/id/n9v6-gdp6.json?$select=`dos_id`,`current_entity_name`,`initial_dos_filing_date`,`county`,`jurisdiction`,`entity_type`,`dos_process_name`,`dos_process_address_1`,`dos_process_address_2`,`dos_process_city`,`dos_process_state`,`dos_process_zip`,`chairman_name`,`chairman_address_1`,`chairman_address_2`,`chairman_city`,`chairman_state`,`chairman_zip`,`registered_agent_name`,`registered_agent_address_1`,`registered_agent_address_2`,`registered_agent_city`,`registered_agent_state`,`registered_agent_zip`,`location_name`,`location_address_1`,`location_address_2`,`location_city`,`location_state`,`location_zip`&$order=`:id`+ASC&$limit={i}&$offset={j}" # 3547074
            response = requests.get(api_url,  headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            json_data = json.loads(response.text)
            if len(json_data) == 0:
                break
            DATA.extend(json_data)
            print('Total records: ',len(DATA))
            j += 10000
            
        df = pd.json_normalize(DATA)
        df.fillna("", inplace=True)
        print(len(df))
        
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
           
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
           
            print("Stored record\n")
            if record_for_db[1] != "":
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for  New York
    '''
    name = 'Economic Development department of the State of New York'
    description = "Official dataset provided by the Economic Development department of the State of New York. The dataset contains information on all active and inactive corporations from 1800 until the present day in the state of New York. The data includes the name, address, jurisdiction, status, effective date, and filing date of each corporation. "
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'New York'
    category = 'Official Registry'
    url = 'https://data.ny.gov/Economic-Development/Active-Corporations-Beginning-1800/n9v6-gdp6'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
