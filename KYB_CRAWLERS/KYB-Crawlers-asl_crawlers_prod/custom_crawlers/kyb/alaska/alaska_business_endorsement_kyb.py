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
    3) Get FATF countries profiles descriptions from database and store them.
    
    @param record
    @return dict
    '''
    # preparing summary dictionary object
    meta_detail = dict()
    meta_detail["license_number"] = str(record["LicenseNumber"]).replace("'","''") 
    meta_detail["issue_date"] =  record["IssueDate"].replace("/","-")
    meta_detail["renew_date"] =  record["RenewDate"].replace("/","-")
    meta_detail["expiry_date"] =  record["ExpireDate"].replace("/","-")
    
    addresses_detail = []
    endorsement_address = dict()
    endorsement_address['type'] = "endorsement_address"
    endorsement_address["address"] = str(record["EndLine1"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+str(record["EndLine2"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+record["EndCity"].replace("'","''")+' '+record["EndCountry"].replace("'","''")+' '+record["EndState"].replace("'","''")+' '+str(record["EndZipOut"]).replace("'","''")
    physical_address = dict()
    physical_address['type'] = "physical_address"
    physical_address['address'] = str(record["PhysicalLine1"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+str(record["PhysicalLine2"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+record["PhysicalCity"].replace("'","''")+' '+record["PhysicalCountry"].replace("'","''")+' '+record["PhysicalState"].replace("'","''")+' '+record["PhysicalZipOut"]
    
    mailing_address = dict()
    mailing_address['type'] = "mailing_address"
    mailing_address['address'] = str(record["MailingLine1"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+str(record["MailingLine2"]).replace("'","''").replace("none","").replace("NONE","").replace("None","")+' '+record["MailingCity"].replace("'","''")+' '+record["MailingCountry"].replace("'","''")+' '+record["MailingState"].replace("'","''")+' '+ record["MailingZipOut"]

    addresses_detail.append(mailing_address)
    addresses_detail.append(physical_address)
    addresses_detail.append(endorsement_address)

    # create data object dictionary containing all above dictionaries
    data_obj = {
        
        "name": record["BusinessName"].replace("'","''"),
        "status": record["Status"].replace("'","''"),
        "crawler_name": "custom_crawlers.kyb.alaska.alaska_business_endorsement_kyb",
        "country_name": "Alaska",
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
    data_for_db.append(shortuuid.uuid(str(record["EndorsementNumber"])+record["BusinessName"]+str(record['LicenseNumber']))) # entity_id
    data_for_db.append(record["BusinessName"].replace("'", "")) #name
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
        FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts'
        SOURCE_URL = url
        
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
      
        df = pd.read_csv('.//kyb/alaska/input/BusinessEndorsementDownload.CSV')
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
    url = "https://www.commerce.alaska.gov/cbp/DBDownloads/BusinessEndorsementDownload.CSV"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()