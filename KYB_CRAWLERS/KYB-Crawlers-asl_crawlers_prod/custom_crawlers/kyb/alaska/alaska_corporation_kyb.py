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

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
# FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/excel_csv/'
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
    # preparing summary dictionary object
    meta_detail = dict()
    meta_detail["aliases"] = str(record["ASSUMEDNAME"]).replace("'","''")  
    meta_detail["end_date"] = str(record["DURATIONEXPIRATIONDATE"]).replace("/","-") 
    
    filling_detail = [
        {
            "date":str(record["NEXTBRDUEDATE"]).replace("/","-"),
            "meta_detail": {} 
        } if record["NEXTBRDUEDATE"].strip() != ''  else None
    ]
    filling_detail = [c for c in filling_detail if c]
    
    people_detail = [
        {
            "name": str(record["REGISTEREDAGENT"]).replace("'","''"), 
            "designation":"registered_agent"
        } if record["REGISTEREDAGENT"].strip() != '' else None
    ]
    people_detail = [c for c in people_detail if c]
    
    addresses_detail = []
    postal_address = dict()
    postal_address["type"] = 'postal_address'
    postal_address['address'] = str(record["ENTITYMAILINGADDRESS1"]).replace("'","''")+' '+str(record['ENTITYMAILINGADDRESS2']).replace("'","''").replace("NONE","")+' '+record["ENTITYMAILINGCITY"].replace("'","''").replace("NONE","")+' '+record["ENTITYMAILINGCOUNTRY"].replace("NONE","").replace("'","''")+' '+record["ENTITYMAILINGSTATEPROVINCE"].replace("'","''")+' '+record["ENTITYMAILINGZIP"]
   
    physical_address = dict()
    physical_address["type"] = 'physical_address'
    physical_address['address'] = str(record["ENTITYPHYSADDRESS1"]).replace("'","''")+''+str(record['ENTITYPHYSADDRESS2']).replace("'","''").replace("NONE","")+' '+record["ENTITYPHYSCITY"].replace("'","''")+' '+record["HOMECOUNTRY"].replace("'","''").replace("NONE","")+' '+record["HOMESTATE"].replace("'","''")+' '+record["ENTITYPHYSZIP"]+' '+record["ENTITYPHYSSTATEPROVINCE"].replace("'","''")
    
    registered_postal_address = dict()
    registered_postal_address["type"] = 'registered_postal_address'
    registered_postal_address['address'] = str(record["REGISTEREDMAILADDRESS1"]).replace("'","''").replace("none","").replace("None","").replace("NONE","")+''+str(record['REGISTEREDMAILADDRESS2']).replace("'","''").replace("none","").replace("None","").replace("NONE","")+' '+record["REGISTEREDMAILCITY"].replace("'","''")+' '+record["REGISTEREDMAILCOUNTRY"].replace("'","''")+' '+record["REGISTEREDMAILSTATEPROVINCE"].replace("'","''")+' '+record["REGISTEREDMAILZIP"]
    
    registered_physical_address = dict()
    registered_physical_address["type"] = 'registered_physical_address'
    registered_physical_address['address'] = str(record["REGISTEREDPHYSADDRESS1"]).replace("'","''").replace("none","").replace("None","").replace("NONE","")+' '+str(record['REGISTEREDPHYSADDRESS2']).replace("'","''").replace("none","").replace("None","").replace("NONE","")+' '+record["REGISTEREDPHYSCITY"].replace("'","''").replace("none","").replace("None","")+' '+record["REGISTEREDPHYSCOUNTRY"].replace("'","''").replace("none","").replace("None","").replace("None","")+' '+record["REGISTEREDPHYSSTATEPROVINCE"].replace("'","''").replace("none","").replace("None","").replace("None","")+' '+record["REGISTEREDPHYSZIP"]
    
    
    if postal_address["address"].strip() != '':
        addresses_detail.append(postal_address)
    elif registered_physical_address["address"].strip() != '':
        addresses_detail.append(registered_physical_address)
    elif registered_postal_address["address"].strip() != '':
        addresses_detail.append(registered_postal_address)
    elif physical_address['address'].strip() != '':
        addresses_detail.append(physical_address)
        
    # create data object dictionary containing all above dictionaries
    data_obj = {
        
        "name": record["LEGALNAME"].replace("'","''"),
        "status": record["STATUS"],
        "registration_number": str(record['ENTITYNUMBER']),
        "registration_date": record['AKFORMEDDATE'].replace("/","-"),
        "dissolution_date": "",
        "incorporation_date":record['AKFORMEDDATE'].replace("/","-"),
        "type": record["CORPTYPE"],
        "crawler_name": "custom_crawlers.kyb.alaska.alaska_corporation_kyb",
        "country_name": "Alaska",
        "company_fetched_data_status": "",
        "addresses_detail": addresses_detail,
        "fillings_detail":filling_detail,
        "people_detail":people_detail,
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
    data_for_db.append(shortuuid.uuid(record["CORPTYPE"]+record["ENTITYNUMBER"])) # entity_id
    data_for_db.append(record["LEGALNAME"].replace("'", "")) #name
    data_for_db.append(json.dumps([record['AKFORMEDDATE'].replace("/","-")])) #dob
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
        SOURCE_URL = url
        
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
      
        df = pd.read_csv('.//kyb/alaska/input/CorporationsDownload.CSV')
        df.fillna("", inplace=True)
        DATA_SIZE = len(df)
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
            insertion_data, lang = crawlers_functions.check_language(
                record_for_db, source_type, url, description, name)
    
            if lang == 'en':
                crawlers_functions.language_handler(insertion_data, 'reports')
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
            else:
                query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                    *insertion_data)

            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: CSV Crawler for Alaska
    '''
    name = 'Corporations, Business & Professional Licensing, Department of Commerce, Community, and Economic Development'
    description = "Official website of Alaska Department of Commerce, Community, and Economic Development's Division of Corporations, Business and Professional Licensing (CBPL). This division is responsible for the regulation of businesses, professionals, and licensing in the state of Alaska, and the website provides information related to these matters."
    entity_type = 'Company/Organization'
    source_type = 'CSV'
    countries = 'Alaska'
    category = 'Official Registry'
    url = "https://www.commerce.alaska.gov/cbp/DBDownloads/CorporationsDownload.CSV"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
