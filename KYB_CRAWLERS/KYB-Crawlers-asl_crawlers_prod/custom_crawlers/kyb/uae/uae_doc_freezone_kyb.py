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
    meta_detail = dict()
    meta_detail['industry_details'] = record[1]
    meta_detail['description'] = record[2]
    
    additional_detail = []
    additional_detail.append({'type':'contact_detail', 'data':[record[3]]})

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.uae.uae_doc_freezone_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "additional_detail": additional_detail
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_doc_freezone_kyb')) # entity_id
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
        API_URL = "https://dubaioutsourcecity.ae/list/SearchFeature/ListCompanies"

        headers = {
            'Authority': 'dubaioutsourcecity.ae',
            'Method': 'POST',
            'Path': '/list/SearchFeature/ListCompanies',
            'Scheme': 'https',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '__RequestVerificationToken=pQzI-R8p05XvaDxW2gM2QcTeRS6V_vliiI2fytl-amSKQ-Dgm9prNSsPv7ACF0Sf_Z-8V87Vsp8VY9IybcbQlMh8DIin2OtGrRDhBNQyNeI1; sxa_site=DOC; DH=!9k4a0K+D+b6dFpQIPWoxTGdWsIcboSSy+XW9p0ercuCDnaXlNbZXMffK8Cfvl2mpsPPoNT4I55ETHg==; TS014aeba6028=0140868dbcb960cb0482f6fd484dd867c41c7de95266f7638d649f2d46dac4400cc72100187d8e87b87d797acebb0cee5b743015f6; ASP.NET_SessionId=lnazw1pz1lee5xahbqvrs2nb; wscrCookieConsent=1=true&2=true&3=true&4=true&5=true&visitor=9d781a8f-729f-49d4-86df-1d5163671997&version=20230518-001; TS014aeba6=0156d765a5d8f9946359729aed73f9fb36c923df83c9a23cbac08be8c0a6d7897eacf34a4b56789320dc438524b9ce0a0f818ad7b8ad0c16c78019273046f3f47ded364e8508be748ac0b965337ccfc664a0d12345ce0febde3a1233063d934bdad1698282c2e25f2d458ff12249a0267a6eb54b05; TSee44fa84027=08fa1e9612ab2000119b9dd52a07be72934c6b6b402860cbdffa1879419525026444a50a29ff497e08e29943f6113000173c5e5f3df82c6a2f97a4de360607015a09e77522e20a8aebe8c5ef64f39d148da82154ed285a680c4c88de677c64e1',
            'Origin': 'https://dubaioutsourcecity.ae',
            'Referer': 'https://dubaioutsourcecity.ae/the-community/community-directory',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        payload = {'body':'keyword=&BusinessPark=DOC&Segment=-1&Alphabet=-1&Page=0&NumberShow={}&id=&inputID=&lang=en'}
        
        response = requests.post(API_URL, data=payload['body'].format(10), headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = json.loads(response.content)
        total_count = json_response['TotalResults']

        response = requests.post(API_URL, data=payload['body'].format(total_count), headers=headers, timeout=60)
        json_response = json.loads(response.content)
        accounts = json_response['Accounts']

        DATA = []
        for account in accounts:
            print(account.get('Name'))
            entity_name = account.get('Name').replace("'","")
            industry_details = account.get('Segments')[0].replace("'","") if account.get('Segments') else ""
            entity_description = account.get('Profile').replace("'","")
            contact_details = {'phone_number':account.get('Phone'), 'website':account.get('Website')}

            DATA.append([entity_name, industry_details, entity_description, contact_details])
            record = [entity_name, industry_details, entity_description, contact_details]

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
    Description: HTML Crawler for UAE Dubai Outsource City Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name ="Community Directory of Dubai (Dubai Outsource City)"
    description = "This is the website of the community directory of Dubai Outsource City. It provides a comprehensive directory of companies based in Dubai Outsource City."
    source_type = "HTML"
    url = "https://dubaioutsourcecity.ae/the-community/community-directory" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
