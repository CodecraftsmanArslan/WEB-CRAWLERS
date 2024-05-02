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
    additional_detail = []
    additional_detail.append({'type':'contact_details', 'data':[record[1]]})

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": record[2],
        "crawler_name": "crawlers.custom_crawlers.kyb.uae_sharjah_airport_freezone_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": additional_detail
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_sharjah_airport_freezone_kyb')) # entity_id
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
        DATA_URL = "https://www.saif-zone.com/umbraco/surface/LoadMore/RenderAuditorItems?numberOfItems=20&page={}&keyword="
        POPUP_URL = "https://www.saif-zone.com/umbraco/surface/LoadMore/RenderInvestorPopUp?AutoId={}"

        page_no = 1
        DATA = []
        while True:
            response = requests.get(DATA_URL.format(page_no), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            print('Page No: ', page_no)
            soup = BeautifulSoup(response.content, 'html.parser')
            if soup.find('div', {'class':'idRow'}) is None:
                break
            page_no+=1

            item_ids = soup.find_all('div', {'class':'col3'})
            for item in item_ids:
                item_id = item.find('span').get('data-page-id')
                
                response = requests.get(POPUP_URL.format(item_id), headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}, timeout=60)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                data_rows = soup.find_all('tr')
                
                for row in data_rows:
                    if 'company name' in str(row).lower():
                        company_name = row.find_all('td')[1].text.replace("'","")
                    elif 'po box' in str(row).lower():
                        po_box = row.find_all('td')[1].text
                    elif 'telephone no' in str(row).lower():
                        telephone_no = row.find_all('td')[1].text
                    elif 'e-mail' in str(row).lower():
                        email = row.find_all('td')[1].text
                    elif 'business type' in str(row).lower():
                        business_type = row.find_all('td')[1].text.replace("'","")
                contact_details = {'po_box':po_box, 'telephone_no':telephone_no, 'email':email}

                DATA.append([company_name, contact_details, business_type])
                record = [company_name, contact_details, business_type]

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
    Description: HTML Crawler for UAE Sharjah International Airport Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name = "Sharjah International Airport Free Zone"
    description = "The website provides an overview of their official auditing partners, including direct contact information1. Sharjah International Airport Free Zone (SAIF Zone) is one of the oldest, largest and fastest-growing free trade zones in the UAE."
    source_type = "HTML"
    url = "https://www.saif-zone.com/en/auditors-directory/" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
