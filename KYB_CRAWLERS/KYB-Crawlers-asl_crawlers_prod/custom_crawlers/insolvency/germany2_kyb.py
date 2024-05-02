"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
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
    meta_detail = dict()
    meta_detail['description'] = record[-1].replace("'","''")
    meta_detail['orignal_research'] = record[0].replace("'","''")
    meta_detail['company'] = record[1].replace("'","''")
    meta_detail['isin'] = record[2].replace("'","''")
    meta_detail['reason_for_the_study'] = record[3].replace("'","''")
    # meta_detail['recommendation'] = record[4].replace("'","''")
    meta_detail['target_price'] = record[5].replace("'","''")
    meta_detail['analyst'] = record[6].replace("'","''")

 

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[1].replace("'","''"),
        "status": record[4].replace("'","''"),
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.insolvency.germany_kyb",
        "country_name": "Germany",
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
    data_for_db.append(shortuuid.uuid(record[0])) # entity_id
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
        # Wait for the page to load
        DATA = []
        soup = BeautifulSoup(response.text, 'lxml')
        new_string = soup.find('h1', class_='headline-text').get_text().strip()
        headline = new_string.replace(":suspended ", "")
        print("headline",headline)
        p_tags = soup.find_all('p')
        # print(p_tags)
        
        data = [tag.get_text().strip() for tag in p_tags if tag.get_text().strip()]
        orignal_research = ""
        company = ""
        isin=""
        reason_for_the_study=""
        target_price=""
        recommendation=""
        analyst=""
        desc = ""
        DATA.append([data,headline])
        start_flag = False
        
        for item in data:
            if item == "MagForce AG unexpectedly files for insolvency; price target and rating":
                start_flag = True
            if start_flag:
                desc += item + " "

            if "desired cost savings." in item:
                break

            if "Original-Research:" in item:
                orignal_research = item.replace("Original-Research:", "").strip()
            elif "Unternehmen:" in item:
                company= item.replace("Unternehmen:", "").strip()
            elif "ISIN:" in item:
                isin = item.replace("ISIN:", "").strip()
            elif "Anlass der Studie:" in item:
                reason_for_the_study = item.replace("Anlass der Studie:", "").strip()
            elif "Empfehlung:" in item:
                recommendation = item.replace("Empfehlung:", "").strip()
            elif "Kursziel:" in item:
                target_price = item.replace("Kursziel:", "").strip()
            elif "Analyst:" in item:
                analyst = item.replace("Analyst:", "").strip()
        
        DATA.append([orignal_research,company,isin,reason_for_the_study,recommendation,target_price,analyst,desc]) 
        for data_ in DATA[1:]:
            record_for_db = prepare_data(data_, category,country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record \n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Germany Insolvency
    '''
    countries = "Germany"
    entity_type = "Company/Organization"
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "Frankfurt Stock Exchange"
    description = "The website provides information on stocks, bonds, ETFs/ETPs, funds, commodities and certificates. It also provides news and market reports on various topics such as market indicators, market sentiment and market trends."
    source_type = "HTML"
    urls = ["https://www.boerse-frankfurt.de/news/87bf7036-bf73-4059-9d6d-01b942f6456f"]
    for url in urls:

        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
