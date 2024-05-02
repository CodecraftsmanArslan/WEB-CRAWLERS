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
        "crawler_name": "crawlers.custom_crawlers.kyb.uae.uae_dubai_police_freezone_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "additional_detail":additional_detail
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_dubai_police_freezone_kyb')) # entity_id
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
        API_URL = "https://dpc.ae/list/SearchFeature/ListCompanies"

        headers = {
            'Authority': 'dpc.ae',
            'Method': 'POST',
            'Path': '/list/SearchFeature/ListCompanies',
            'Scheme': 'https',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '__RequestVerificationToken=h5eiADlZEy5WhT5o8EIpEppjy2PMTuJQq9OpFUW1XN03lLNSUP6bkL1Dqzea_W0rp-XlVl-zv_bwTY1lOqu0nBCG3K8pFO3yGze751g50qs1; sxa_site=DPC; DH=!6q7cFXVjBLTA0gMIPWoxTGdWsIcboTrh4zrJHuXQqNaAcmnwWhX+MiKmLg+lmKeTvYHiSmoom/tAbQ==; TS01a0240f028=0140868dbc45c5004d2bd4ff8089dd87c829a98c78f05b23e392eca814b8cc0d68711e1353310853834cbe674cc66ca701f15174c8; wscrCookieConsent=1=true&2=true&3=true&4=true&5=true&visitor=f7fb29d1-4e53-482c-8ee9-0a35137dc260&version=20230518-001; _gcl_au=1.1.2114068126.1684499429; _gid=GA1.2.1333114357.1684499429; ASP.NET_SessionId=jk5md3adkd342rn15hkjm0jh; TS01a0240f=0156d765a540d2032853813f3026e4d9fd6e4810c505ba0b34facaef55d213268dff7e6e85635d9f6fa4e8da4b55ec53b3337ba6e9aa6c22306c272f4853c69c4426fc1756a8eb713e80225cf128e19c680bbff132bb5f6123bd77d1d7c6acfbaa5172a6caf6b2003fadf51b49b2e7b85d92fb67b1; _ga=GA1.2.1271631784.1684499429; _gat_UA-75405742-1=1; _ga_NMVW50QGWW=GS1.1.1684499429.1.1.1684499496.0.0.0; TSee44fa84027=08fa1e9612ab2000f8f76cdb2adcb816917485b2b9dcb929e21c314e8f01a34035e66a3d08f3da0f086749b8ac113000ec9831d712100e46ae9ed6cc26f7c7513e61564d9f4a5962709befbf974decea12df74a5a7e22fc53ea55f97389e8e52',
            'Origin': 'https://dpc.ae',
            'Referer': 'https://dpc.ae/the-community/community-directory',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        payload = {'body':'keyword=&BusinessPark=DPC&Segment=-1&Alphabet=-1&Page=0&NumberShow={}&lang=en'}
        
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
    Description: HTML Crawler for UAE Dubai Police Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name ="Dubai Police College"
    description = "The website is a comprehensive community directory that helps you conveniently find companies based in Dubai Production City as well as their retail outlets."
    source_type = "HTML"
    url = "https://dpc.ae/the-community/community-directory" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
