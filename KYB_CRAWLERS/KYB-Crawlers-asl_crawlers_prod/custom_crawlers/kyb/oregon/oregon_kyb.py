"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
import re
from store_object import storeRecord
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
    # preparing meta details dictionary object
    meta_detail = dict()
    meta_detail['business_details'] = record.iloc[0]['business_details.url'].replace("'","''") 
    meta_detail['representative_registration_number'] = record.iloc[0]['entity_of_record_reg_number'].replace("'","''") 
    meta_detail['suffix'] = record.iloc[0]['suffix'].replace("'","''") 
    meta_detail['aliases'] = record.iloc[0]['entity_of_record_name'].replace("'","''")
    # preparing additional_detail dictionary object
    
    peopel_detail = []
    representative_name = dict()
    representative_name['designation'] = "representative"  
    try: 
        representative_name["name"] =  record.iloc[2]['first_name'].replace("'","''")+''+record.iloc[2]['middle_name'].replace("'","''")+''+record.iloc[2]['last_name'].replace("'","''")
    except:
        representative_name["name"] = record.iloc[0]['first_name'].replace("'","''")+''+record.iloc[0]['middle_name'].replace("'","''")+''+record.iloc[0]['last_name'].replace("'","''")

    if representative_name["name"].strip() != '':
        peopel_detail.append(representative_name)

    addresses_detail_lst = []
    addresses_detail = dict() 
    addresses_detail['type'] = "mailing_address"
    addresses_detail_address = f"{record.iloc[0]['address']} {record.iloc[0]['city']} {record.iloc[0]['state']} {str(record.iloc[0]['zip'])}"
    addresses_detail['address'] = addresses_detail_address.replace("'","''").replace("%", "%%").replace("  ", " ")
    addresses_detail['description'] = ""
    meta_details = dict()
    meta_details['jurisdiction'] = record.iloc[0]['jurisdiction']
    addresses_detail['meta_detail'] = meta_details
    
    principal_place_of_business = dict() 
    principal_place_of_business['type'] = "principal_place_of_business"
    try:
        principal_place_of_business_address = record.iloc[1]['address'].replace("'","''")
    except:
        principal_place_of_business_address = record.iloc[0]['address'].replace("'","''")
    principal_place_of_business['description'] = ""
    pmeta_details = dict()
    try:
        pmeta_details_city = record.iloc[1]['city'].replace("'","''")
    except:
        pmeta_details_city = record.iloc[0]['city'].replace("'","''")
    try:
        pmeta_details_state = record.iloc[1]['state'].replace("'","''")
    except:
        pmeta_details_state = record.iloc[0]['state'].replace("'","''")
    try:
        pmeta_details_zip_code = str(record.iloc[1]['zip']).replace("'","''")
    except:
        pmeta_details_zip_code = str(record.iloc[0]['zip']).replace("'","''")
    try:
        pmeta_details['jurisdiction'] = record.iloc[1]['jurisdiction']
    except:
        pmeta_details['jurisdiction'] = record.iloc[0]['jurisdiction']
    principal_place_of_business_address_ = f"{principal_place_of_business_address} {pmeta_details_city} {pmeta_details_state} {pmeta_details_zip_code}"
    principal_place_of_business['address'] = principal_place_of_business_address_.replace("'","''").replace("%", "%%").replace("  ", " ")
    principal_place_of_business['meta_detail'] = pmeta_details
    genral_address = dict()
    genral_address['type'] = "general_address"
    genral_address['description'] =""
    try:
        genral_address_address = record.iloc[2]['address'].replace("'","''")
    except:
        genral_address_address  = record.iloc[0]['address'].replace("'","''")
    genral_address_data = dict()
    try:
        genral_address_data_city = record.iloc[2]['city'].replace("'","''")
    except IndexError:
        genral_address_data_city = record.iloc[0]['city'].replace("'","''")
    try:
        genral_address_data_state = record.iloc[2]['state'].replace("'","''")
    except IndexError:
        genral_address_data_state = record.iloc[0]['state'].replace("'","''")
    try:
        genral_address_data_zip_code = str(record.iloc[2]['zip']).replace("'","''")
    except IndexError:
        genral_address_data_zip_code = str(record.iloc[0]['zip']).replace("'","''")
    try:
        genral_address_data['jurisdiction'] = record.iloc[2]['jurisdiction']
    except IndexError:
        genral_address_data['jurisdiction'] = record.iloc[0]['jurisdiction']
    genral_address_address_ = f"{genral_address_address} {genral_address_data_city} {genral_address_data_state} {genral_address_data_zip_code}"
    genral_address['address'] = genral_address_address_.replace("'","''").replace("%", "%%").replace("  ", " ")
    genral_address['meta_detail'] = genral_address_data
    
    if addresses_detail['address'] != "":
        addresses_detail_lst.append(addresses_detail)
    elif principal_place_of_business['address'] != "":
        addresses_detail_lst.append(principal_place_of_business)
    elif genral_address['address'] != "":
        addresses_detail_lst.append(genral_address)
    
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": re.sub(r'[^a-zA-Z0-9\s]', '', record.iloc[0]['business_name'].replace("'","''")),
        "status": "", 
        "registration_number": record.iloc[0]['registry_number'],
        "registration_date": str(pd.to_datetime(record.iloc[0]['registry_date'].replace("'","''"))),
        "dissolution_date": "",
        "type": record.iloc[0]['entity_type'].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.oregon_kyb",
        "country_name": "Oregon",
        "company_fetched_data_status": "",
        "addresses_detail": addresses_detail_lst,
        "meta_detail": meta_detail,
        "people_detail": peopel_detail
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
    entity_name_ = record.iloc[0]['business_name'].replace("'", "")
    data_for_db.append(shortuuid.uuid(f"{record.iloc[0]['registry_number']}{entity_name_}-kyb.oregon_kyb")) # entity_id
    data_for_db.append(entity_name_) #name
    dt = record.iloc[0]['registry_date'][:record.iloc[0]['registry_date'].find('T')]
    data_for_db.append(json.dumps([dt])) #dob
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

def divide_dataframe_into_chunks(df):
    """Divides a pandas DataFrame into chunks of three rows each"""
    chunked_df = []
    for i in range(0, len(df), 3):
        chunked_df.append(df.iloc[i:i+3])
    return chunked_df

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
            api_url = f"https://data.oregon.gov/api/id/tckn-sxa6.json?$select=`registry_number`,`business_name`,`entity_type`,`registry_date`,`associated_name_type`,`first_name`,`middle_name`,`last_name`,`suffix`,`not_of_record_entity`,`entity_of_record_reg_number`,`entity_of_record_name`,`address`,`address_continued`,`city`,`state`,`zip`,`jurisdiction`,`business_details`&$order=`:id`+ASC&$limit={i}&$offset={j}" #2785900
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
        data = divide_dataframe_into_chunks(df)
        for chunk in data:
            if chunk.iloc[0]['registry_number']:
                record_for_db = prepare_data(chunk, category,
                                            country, entity_type, source_type, name, url, description)    
                print(record_for_db)
                storeRecord(record_for_db)
            
        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Oregon
    '''
    name = 'Oregon Secretary of State, Corporation Division'
    description = "The dataset includes information on active and inactive businesses registered with the Oregon Secretary of State's Corporation Division. It includes the business name, registry number, registration date, and whether the business is active or inactive."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Oregon'
    category = 'Official Registry'
    url = 'https://data.oregon.gov/business/Active-Businesses-ALL/tckn-sxa6'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
