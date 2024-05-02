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
NAICS_DICT = json.load(open('kyb/texas/mapping/naics-codes.json'))

def get_naics_value(naic_sub_code):
    naic_sub_code = naic_sub_code.strip()
    if naic_sub_code !='':
        if naic_sub_code in NAICS_DICT:
            return NAICS_DICT[f'{naic_sub_code}']
        else:
            return None
    return None

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''
    # preparing meta details dictionary object
    meta_detail = dict()
    code = record["_621111"].strip()
    meta_detail['record_type_code'] = record["record_type_code"].replace("'","''")
    meta_detail['last_updated'] = record["sos_status_date"]
    meta_detail['sos_id'] = record["secretary_of_state_sos_or_coa_file_number"]
    meta_detail['sos_charter_date'] = record["sos_charter_date"]
    meta_detail['right_to_transact_business_code'] = record["right_to_transact_business_code"].replace("'","''")
    meta_detail['current_exempt_reason_code'] = record["current_exempt_reason_code"]
    meta_detail['exempt_begin_date'] = record["exempt_begin_date"].replace("'","''")
    meta_detail['trade_code'] = get_naics_value(code).replace("'","''") if get_naics_value(code) else ''
    # preparing address_details dictionary object
    addresses_detail = dict()
    meta_details = dict()
    addresses_detail["type"]= "billing_address"
    addresses_detail["address"]= record["taxpayer_address"].replace("'","''").replace("NULL","").replace("NONE","")+' '+record["taxpayer_city"].replace("'","''")+' '+record["taxpayer_state"].replace("'","''")+' '+ str(record["taxpayer_zip"]).replace("'","''") 
    meta_details['county_code'] = record['taxpayer_county_code']
    addresses_detail['meta_detail'] = meta_details

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["taxpayer_name"].replace("'","''"),
        "status": record["sos_status_code"],
        "registration_number": "",
        "registration_date": str(pd.to_datetime(record["responsibility_beginning_date"])),
        "dissolution_date": "",
        "type": record["taxpayer_organizational_type"].replace("'","''"),
        "crawler_name": "custom_crawlers.kyb.texas.texas_kyb",
        "country_name": "Texas",
        "tax_number":record["taxpayer_number"].replace("'","''"),
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
    data_for_db.append(shortuuid.uuid(record["taxpayer_number"]+'texas_kyb')) # entity_id
    data_for_db.append(record["taxpayer_name"].replace("'", "")) #name
    data_for_db.append(json.dumps([record["responsibility_beginning_date"].replace('T00:00:00.000','')])) #dob
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
            api_url = f"https://data.texas.gov/api/id/9cir-efmm.json?$select=`taxpayer_number`,`taxpayer_name`,`taxpayer_address`,`taxpayer_city`,`taxpayer_state`,`taxpayer_zip`,`taxpayer_county_code`,`taxpayer_organizational_type`,`record_type_code`,`responsibility_beginning_date`,`secretary_of_state_sos_or_coa_file_number`,`sos_charter_date`,`sos_status_date`,`sos_status_code`,`right_to_transact_business_code`,`current_exempt_reason_code`,`exempt_begin_date`,`_621111`&$order=`:id`+ASC&$limit={i}&$offset={j}" 
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
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            json_data = json.loads(record_for_db[7])
            registration_number = json_data['registration_number']
            record_name = record_for_db[1].strip()
            if not (record_name == '' and registration_number.strip() == ''):
                print("Stored record\n")
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: JSON Crawler for Texas
    '''
    name = 'Texas Comptroller of Public Accounts'
    description = "Dataset provided by the Texas Comptroller of Public Accounts that contains information on businesses that hold an active franchise tax permit in the state of Texas. The dataset includes the business name, taxpayer number, city, state, zip code, and the effective date of the permit. "
    entity_type = 'Company/Organization'
    source_type = 'JSON'
    countries = 'Texas'
    category = 'Official Registry'
    url = 'https://data.texas.gov/dataset/Active-Franchise-Tax-Permit-Holders/9cir-efmm'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
    