"""Set System Path"""
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
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
    # meta_detail['company_name'] = record[0].replace("'","''")
    meta_detail['last_audit'] = record[1]
    meta_detail['suspension_date'] = record[6]
    meta_detail['remarks'] = str(record[2]).replace("'","''")
    meta_detail['compliance_status'] = record[3]
    meta_detail['action_taken'] = str(record[4]).replace("'","''")
    meta_detail['defaulted_date'] = record[5]
    meta_detail['people_details'] = str(record[-1]).replace("'","''")
   

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.insolvency.pakistan.pakistan_stock_exchange_kyb",
        "country_name": "Pakistan",
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
    data_for_db.append(shortuuid.uuid(record[0]+ str(record[1])+record[5]+str(record[4])+str(url)+ "pakistan_stock_exchange_kyb")) # entity_id
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
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table element containing the data
        p_tags = soup.find_all('p', class_=["CurrentSegment"])
        ids = []
        
        for p_tag in p_tags:
            a_tags = p_tag.find_all('a')
            
            for a_tag in a_tags:
                id= a_tag.get('id')
                # count += 1 
                # print(count,id)
                #Check if the href attribute exists
                if id:
                    id_ = id.split('/')[-1]
                    ids.append(id_)
        
        base_url = "https://www.psx.com.pk/psx/resources-and-tools/call-test?id={}&XID=7e1c2eb5dca0984f70c0a35651ddd994b00169bf"
        for id in ids:
            dummy_data = dict()
            dummy_data['people_details'] = []
            new_url = base_url.format(id)
            print(new_url)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'Host': 'www.psx.com.pk'
            }
            res = requests.get(new_url, headers=headers)
            res = res.json()
            print("Response",res)
            DATA = []
            for compane_name in res['keyfive']:
                dummy_data['company_name'] = compane_name['company_name']

            dummy_data['last_audit'] = ""
            dummy_data['remarks'] = ""
            dummy_data['action_taken'] = ""
            dummy_data['compliance_status'] = []

            if res['keyone']:
                for entry in res['keyone']:
                    dummy_data['remarks'] = entry['REMARKS']
                    clause_violated_list = entry['CLAUSE_VIOLATED']
                    dummy_data['compliance_status'].append(clause_violated_list)
                    dummy_data['action_taken'] = entry['CORRECTIVE_ACTIONS']
                    
                # dummy_data['defaulted_date'] = entry['DATE_OF_PLACEMENT']
                    
            if len(res['keyone']) > 0:
                dummy_data['defaulted_date'] = res['keyone'][0]['DATE_OF_PLACEMENT']
            else:
                dummy_data['defaulted_date'] = ""
            # dummy_data['defaulted_date'] = res['keyone'][0]['DATE_OF_PLACEMENT'] 
            # print(clause_violated_list)

            for entry in res['keytwo']:
                name_of_director = entry['NAME_OF_DIRECTOR']
                designation = entry['DESIGNATION']
                directors_no_of_shares = entry['DIRECTORS_NO_OF_SHARES']
                share_holding_pct = entry['SHARE_HOLDING_PCT']
                
                people_details = {"name_of_director": name_of_director, 'designation':designation,'directors_no_of_shares':directors_no_of_shares,'share_holding_pct':share_holding_pct} 
                dummy_data['people_details'].append(people_details)
                # DATA.append(people_details)
            suspension_dates = res['keyfour']
            if suspension_dates:
                dummy_data['suspension_date'] = suspension_dates[0]['SUSPENSION_DATE_FROM']
            else:
                dummy_data['suspension_date'] = ""
                    
                    
            print(dummy_data)
            DATA=[dummy_data['company_name'],dummy_data['last_audit'],dummy_data['remarks'],dummy_data['compliance_status'],dummy_data['action_taken'],dummy_data['defaulted_date'],dummy_data['suspension_date'],dummy_data['people_details']]  
            record_for_db = prepare_data(DATA, category,country, entity_type, source_type, name, url, description)
            
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("stored in database\n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Australia
    '''
    name = 'Pakistan Stock Exchange'
    description = "The Pakistan Stock Exchange (PSX) is the main stock exchange of Pakistan, located in Karachi, the country's largest city and financial center.Given link is of List of Companies that've been defaulted"
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Pakistan'
    category = 'Bankruptcy/ Insolvency/ Liquidation'
    url = "https://www.psx.com.pk/psx/resources-and-tools/Defaulting-Companies-Profile-Portal"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
