"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
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
import requests
from bs4 import BeautifulSoup

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
    meta_detail["liquidator"] = record[1].replace("'", "''")
    meta_detail["type_of_proceeding"] = record[2].replace("'", "''")
    meta_detail["debtor"] = record[3].replace("'", "''")
    meta_detail["address"] = record[4].replace("'", "''")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[0].replace("'", "''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "custom_crawlers.insolvency.switzerland_kyb",
        "country_name": "Switzerland",
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
    data_for_db.append(shortuuid.uuid(f'{json.dumps(record)}-switzerland_kyb')) # entity_id
    data_for_db.append(name) #name
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

def get_links(url):
    url = 'https://www.finma.ch/en/api/search/getresult?skip={}'
    payload = 'query=insolvency&Order=4'
    skip = 0

    response = requests.post(url.format(skip), data=payload, timeout=60)
    data = response.json()
    total = data['Count']
    links = []

    while skip < total:
        print('add links...', skip)
        response = requests.post(url.format(skip), data=payload, timeout=60)
        data = response.json()
        for each in data.get("Items"):
            if 'Insolvency' in each['Category']:
                links.append('https://www.finma.ch'+each['Link'])
        skip += 25
    return links

def get_data(link):
    data = []
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        name_ = soup.select("h2.e-text")[0].text
        div_tags = soup.find_all("p", class_="text-page")
        liquidator = div_tags[1].text.strip()
        if liquidator.startswith("Liquidator"):
            liquidator = liquidator[len("Liquidator"):].strip()
        type_of_proceeding = div_tags[2].text.strip()
        if type_of_proceeding.startswith("Type of proceeding"):
            type_of_proceeding = type_of_proceeding[len("Type of proceeding"):].strip()
        debtor_text = div_tags[3].text.strip()
        debtor = debtor_text.split(",")[0]
        if debtor.startswith("Debtor"):
            debtor = debtor[len("Debtor"):].strip()
        address = debtor_text.split(",")[1]
        data.append(name_)
        data.append(liquidator)
        data.append(type_of_proceeding)
        data.append(debtor)
        data.append(address)
        print(name_, liquidator, type_of_proceeding, debtor, address)
    except:
        pass
    return data
    
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
        links = get_links(url)
        for link in links:
            record_ = get_data(link)
            if len(record_) != 0:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                                
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                print("Stored record\n")
                crawlers_functions.db_connection(query)
            else:
                print("Something went wrong")
        return len(record_), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: CSV Crawler for Switzerland
    '''
    countries = "Switzerland"
    entity_type = " Company/Organisation"
    category =  "Official Registry"
    name = "Swiss Financial Market Supervisory Authority (FINMA)"
    description = "FINMA is the primary regulatory body for financial markets and institutions in Switzerland. The website provides a search function to get information related to financial market supervision and regulation in Switzerland."
    source_type = "HTML"
    url = 'https://www.finma.ch/en/api/search/getresult'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
