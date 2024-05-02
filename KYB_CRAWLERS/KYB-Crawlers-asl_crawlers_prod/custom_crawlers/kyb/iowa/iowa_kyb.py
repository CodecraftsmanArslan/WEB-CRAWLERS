"""Set System Path"""
import sys
from pathlib import Path
# sys.path.append('/Users/tayyabali/Desktop/work/ASL-Crawlers')
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import os
import json
import requests
import time
import shortuuid
from helpers.crawlers_helper_func import CrawlersFunctions
from helpers.logger import Logger
from dotenv import load_dotenv
from langdetect import detect
import pandas as pd
import datetime
import traceback

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME = ''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'


def get_listed_object(record,  countries):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @return dict
    '''
    try:
        ra_location = str(record["ra_location.coordinates"][0])
    except:
        ra_location = ""
    try:
        ra_location1 = str(record["ra_location.coordinates"][1])
    except:
        ra_location1 = ""
    # preparing summary dictionary object
    if str(record["ra_address_1"]).strip() != "":
        registered_agent = dict()
        registered_agent['designation'] = 'registered_agent'
        registered_agent['name'] = record["registered_agent"].replace("'", "''").replace("NULL","").replace("NONE","").replace("null","")
        registered_agent['address'] = str(record["ra_address_1"].replace("'", "''").replace("NULL","").replace("NONE","").replace("null","")).replace("'", "''")+' '+record['ra_address_2'].replace(
            "'", "''").replace("NULL","").replace("NONE","").replace("null","")+' '+record["ra_city"].replace("'", "''")+' '+record["ra_state"].replace("'", "''")+' '+str(record["ra_zip"]).replace("'", "''")
        meta_detail_agent = dict()
        meta_detail_agent['location'] = record["ra_location.type"] + ','+ra_location+','+ra_location1
        registered_agent['meta_detail'] = meta_detail_agent
        PEOPLE_DETAIL = [registered_agent]
    else:
        PEOPLE_DETAIL = []
    try:
        ho_location = str(record["ho_location.coordinates"][0])
    except:
        ho_location = ""
    try:
        ho_location1 = str(record["ho_location.coordinates"][1])
    except:
        ho_location1 = ""
    
    if (str(record["ho_address_1"] + record["ho_address_2"])).strip() != "":
        address = dict()
        address['type'] = "general_address"
        address['address'] = (
            str(record["ho_address_1"] + ' ' + record["ho_address_2"])
            .replace("'", "''").replace("NULL","").replace("NONE","") + ' '
            + record["ho_country"].replace("'", "''") + ' '
            + record["ho_city"].replace("'", "''") + ' '
            + record["ho_state"].replace("'", "''") + ' '
            + str(record["ho_zip"]).replace("'", "''")
        )
        meta_detail_address = dict()
        if (
            record["ho_location.type"] != ""
            and ho_location != ""
            and ho_location1 != ""
        ):
            meta_detail_address['locations'] = (
                record["ho_location.type"] + ','
                + ho_location + ',' + ho_location1
            )
        address['meta_detail'] = meta_detail_address

        addresses_detail = []
        if meta_detail_address.get('locations') != "":
            addresses_detail.append(address)

        ADDRESSES_DETAIL = [address]
    else:

        ADDRESSES_DETAIL = []

    country_bounding = {
        "county_boundary": str(record[':@computed_region_y683_txed'])
    }if str(record[':@computed_region_y683_txed']).strip() != '' else {}

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["legal_name"].replace("'", "''"),
        "status": "Active",
        "registration_number": record["corp_number"],
        "registration_date": str(pd.to_datetime(record["effective_date"])),
        "dissolution_date": "",
        "type": record["corporation_type"].replace("'", "''"),
        "crawler_name": "custom_crawlers.kyb.iowa.iowa_kyb.py",
        "country_name": countries,
        "company_fetched_data_status": "",
        "addresses_detail": ADDRESSES_DETAIL,
        "people_detail": PEOPLE_DETAIL,
        "meta_detail": country_bounding
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
    data_for_db.append(shortuuid.uuid(
        f'{record["corp_number"]}-{record["effective_date"]}-kyb.iowa.iowa_kyb'))  # entity_id
    data_for_db.append(record["legal_name"].replace("'", ""))  # name
    data_for_db.append(json.dumps([]))  # dob
    data_for_db.append(json.dumps([category.title()]))  # category
    data_for_db.append(json.dumps([country.title()]))  # country
    data_for_db.append(entity_type.title())  # entity_type
    data_for_db.append(json.dumps([]))  # img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'", "''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record, country)))  # data
    data_for_db.append(json.dumps(source_details))  # source_details
    data_for_db.append(name_ + "-" + type_)  # source
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
            api_url = f"https://data.iowa.gov/api/id/ez5t-3qay.json?$select=`corp_number`,`legal_name`,`corporation_type`,`effective_date`,`registered_agent`,`ra_address_1`,`ra_address_2`,`ra_city`,`ra_state`,`ra_zip`,`home_office`,`ho_address_1`,`ho_address_2`,`ho_city`,`ho_state`,`ho_zip`,`ho_country`,`ra_location`,`ho_location`,`:@computed_region_y683_txed`&$order=`:id`+ASC&$limit={i}&$offset={j}"
            response = requests.get(api_url, headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            json_data = json.loads(response.text)
            if len(json_data) == 0:
                break
            DATA.extend(json_data)
            print('Total records: ', len(DATA))
            j += 10000

        df = pd.json_normalize(DATA)
        df.fillna("", inplace=True)

        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                         country, entity_type, source_type, name, url, description)

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'", "''")


if __name__ == '__main__':
    '''
    Description: JSON Crawler for Iowa
    '''
    name = 'Iowa Division of Corporations'
    description = "This dataset provides a list of active business entities in the state of Iowa . The dataset includes information on both domestic business organizations that are organized under and subject to the laws of Iowa , as well as foreign business organizations that are authorized to do business in Iowa. The data includes the name of the entity, entity status, formation/authorization date, principal office address, registered agent name and address, and the type of entity (e.g. LLC, corporation, etc.)."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Iowa'
    category = 'Official Registry'
    url = "https://data.iowa.gov/Regulation/Active-Iowa-Business-Entities/ez5t-3qay"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                              category, url, name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path": file_path, "trace_back": trace_back,  "crawler": "HTML"})
    logger.log()
