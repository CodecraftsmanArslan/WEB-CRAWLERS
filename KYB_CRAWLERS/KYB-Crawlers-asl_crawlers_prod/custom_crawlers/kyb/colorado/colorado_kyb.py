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
    
    meta_detail = dict()
    people_detail = {} if record["agentfirstname"].strip() == '' and record["agentmiddlename"].strip() == '' and record["agentlastname"].strip() == '' and all(value.strip() == '' for value in [record["agentprincipaladdress1"], record["agentprincipaladdress2"], record["agentprincipalcity"], record["agentprincipalstate"], record["agentprincipalzipcode"], record["agentprincipalcountry"]]) else {
        "designation": "registered_agent",
        "name": (record["agentfirstname"].replace("'", "''") + ' ' + record["agentmiddlename"].replace("'", "''") + ' ' + record["agentlastname"].replace("'", "''")).strip(),
        "address": ' '.join(filter(None, [
            str(record["agentprincipaladdress1"]).replace("'", "''").strip(),
            str(record["agentprincipaladdress2"]).replace("'", "''").strip(),
            record["agentprincipalcity"].replace("'", "''").strip(),
            record["agentprincipalstate"].replace("'", "''").strip(),
            str(record["agentprincipalzipcode"]).replace("'", "''").strip(),
            record["agentprincipalcountry"].replace("'", "''").strip(),
            record["agentmailingcity"].replace("'", "''").strip() if record["agentmailingcity"] else '',
            str(record["agentmailingstate"]).replace("'", "''").strip() if record["agentmailingstate"] else '',
            str(record["agentmailingzipcode"]).replace("'", "''").strip() if record["agentmailingzipcode"] else '',
            record["agentmailingcountry"].replace("'", "''").strip() if record["agentmailingcountry"] else ''
        ])).replace("'", "''").strip(),
        "postal_address": ' '.join([
            str(record["agentmailingaddress1"]).replace("'", "''").replace("null", "").strip(),
            str(record["agentmailingaddress2"]).replace("'", "''").replace("null", "").strip()
        ]).strip(),
        "meta_detail": {
            "suffix": str(record["agentsuffix"]).replace("'", "''").strip(),
            "organization": record["agentorganizationname"].replace("'", "''").strip(),
        }
    }

    # Remove "meta_detail" if all its nested keys' values are empty
    if people_detail != {} and all(value == "" for value in people_detail["meta_detail"].values()):
        people_detail.pop("meta_detail")

    # preparing addresses_detail_lst dictionary object
    addresses_detail = [
        {
            "type": "principal_office_address",
            "address": ', '.join(filter(None, [
                str(record["principaladdress1"].replace("'", "''") + ' ' + record["principaladdress2"].replace("'", "''")).strip(),
                record["principalcity"].replace("'", "''").strip() if record["principalcity"] else '',
                record["principalstate"].replace("'", "''").strip() if record["principalstate"] else '',
                str(record["principalzipcode"]).replace("'", "''").strip() if record["principalzipcode"] else '',
                record["principalcountry"].replace("'", "''").strip() if record["principalcountry"] else ''
            ]))
        },
        {
            "type": "postal_address",
            "address": ', '.join(filter(None, [
                str(record["mailingaddress1"]).replace("'", "''").strip(),
                str(record["mailingaddress2"]).replace("'", "''").strip(),
                record["mailingcity"].replace("'", "''").strip(),
                record["mailingstate"].replace("'", "''").strip(),
                str(record["mailingzipcode"]).replace("'", "''").strip(),
                record["mailingcountry"].replace("'", "''").strip()
            ])).replace("'", "''").replace("'", "''").strip()
        } if record["mailingaddress1"].strip() != '' else None
    ]

#    
    addresses_detail = [c for c in addresses_detail if c]


    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["entityname"].replace("'","''"),
        "status": record["entitystatus"].replace("'","''"),
        "registration_number": record['entityid'],
        "registration_date": record["entityformdate"],
        "dissolution_date": "",
        "type": record["entitytype"].replace("'","''"),
        "jurisdiction" :str(record["jurisdictonofformation"]).replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.colorado.colorado_kyb",
        "country_name": "Colorado",
        "company_fetched_data_status": "",
        "people_detail": [people_detail],
        "addresses_detail": addresses_detail,
        "meta_detail": meta_detail
    }
    if people_detail != {} and people_detail['name'] != '':
        data_obj['people_detail'] = [people_detail]
    
    #  Filter out empty objects
    data_obj["people_detail"] = [obj for obj in data_obj["people_detail"] if obj]

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
    data_for_db.append(shortuuid.uuid(f'{record["entityid"]}-colorado_kyb')) # entity_id
    data_for_db.append(record["entityname"].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
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
            api_url = f"https://data.colorado.gov/api/id/4ykn-tg5h.json?$select=`entityid`,`entityname`,`principaladdress1`,`principaladdress2`,`principalcity`,`principalstate`,`principalzipcode`,`principalcountry`,`mailingaddress1`,`mailingaddress2`,`mailingcity`,`mailingstate`,`mailingzipcode`,`mailingcountry`,`entitystatus`,`jurisdictonofformation`,`entitytype`,`agentfirstname`,`agentmiddlename`,`agentlastname`,`agentsuffix`,`agentorganizationname`,`agentprincipaladdress1`,`agentprincipaladdress2`,`agentprincipalcity`,`agentprincipalstate`,`agentprincipalzipcode`,`agentprincipalcountry`,`agentmailingaddress1`,`agentmailingaddress2`,`agentmailingcity`,`agentmailingstate`,`agentmailingzipcode`,`agentmailingcountry`,`entityformdate`&$order=`:id`+ASC&$limit={i}&$offset={j}" 
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
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
            insertion_data, lang = crawlers_functions.check_language(
                record_for_db, source_type, url, description, name)
    
            if lang == 'en':
                crawlers_functions.language_handler(insertion_data, 'reports')
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            else:
                query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                    *insertion_data)
            
            print("Stored record\n")
            if record_for_db[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Colorado
    '''
    name = 'Colorado Secretary of State, Business Division'
    description = "This is an open dataset provided by the Colorado Secretary of State's office. The dataset contains information on business entities registered with the Colorado Department of State , including corporations, limited liability companies, and limited partnerships. The data includes information on the entity's name, entity ID number, registration date, status, and other details."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Colorado'
    category = 'Official Registry'
    url = 'https://data.colorado.gov/Business/Business-Entities-in-Colorado/4ykn-tg5h'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
