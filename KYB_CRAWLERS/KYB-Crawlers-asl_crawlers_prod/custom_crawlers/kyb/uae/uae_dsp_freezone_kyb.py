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
        "crawler_name": "crawlers.custom_crawlers.kyb.uae_dsp_freezone_kyb",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_dsp_freezone_kyb')) # entity_id
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
        API_URL = "https://dsp.ae/list/SearchFeature/ListCompanies"

        headers = {
            'Authority': 'dsp.ae',
            'Method': 'POST',
            'Path': '/list/SearchFeature/ListCompanies',
            'Scheme': 'https',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '__RequestVerificationToken=WIXaaNAeJjPb9Qf3KZuzy0EZSJri_7ihMWA5uM-P82vl7XPemEWNC8OgiCprPNoPh58P143tg8WJ8SFeZsFcHw0Fi8GSYbys5F56CgQeqZ41; sxa_site=DSP; DH=!vgggwdQ6601g+IYIPWoxTGdWsIcboRceFdjLJqCGCS47nLeGQeNXOjwYDVeEm0qQujpZ8mFn6K5ruQ==; TS0119a385028=0140868dbcd4fa56ace97c09d2668a94dca64915d95acfc62a1afc36242001f9e618ccb7e21d6035727e292ece360f4525b201ef5a; ASP.NET_SessionId=nbb1501zqsv0c1kebmlaxis0; TS0119a385=0156d765a57eec205c09f8777a77a0f5eb93e9f7b03b46a839d33f0e31194b7bf31aaa05004fda658abb0a93d20e29f8578d13e0f63e721dd5c8df688d9c1176af524efa664e0f1887348a26df956361667b0f16a94fe56aa6dfc8f0a6af7ee5456ad8411426084483d02ffc82eb585c6c0a369c53; _gcl_au=1.1.1053807012.1684750614; wscrCookieConsent=1=true&2=true&3=true&4=true&5=true&visitor=ff7335b3-af36-48d7-be64-7e80dd3830bd&version=20230518-001; _gid=GA1.2.1996384921.1684750615; ln_or=eyIzNjczNTUzIjoiZCJ9; _fbp=fb.1.1684750615592.2042603335; _gat_UA-68684294-1=1; _ga_SC62STKG91=GS1.1.1684750615.1.1.1684750829.0.0.0; _ga=GA1.1.537866372.1684750615; TSee44fa84027=08fa1e9612ab20008bf73d9a76bfae92ac98542c15ff819a61003853cd890000df0bd12b6d2f119908e4f7c29811300097bb931d13997cd9da44393ef13aea53af9d97cbc25d1e0f45557a26ef5f5aa2bdf6464a33751c4d2bf4babda01095ef',
            'Origin': 'https://dsp.ae',
            'Referer': 'https://dsp.ae/the-community/community-directory',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        payload = {'body':'keyword=&BusinessPark=DSP&Segment=-1&Alphabet=-1&Page=0&NumberShow={}&id=&inputID=&lang=en'}
        
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
    Description: HTML Crawler for UAE Dubai Science Park Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name = "Dubai Science Park"
    description = "This website describes Dubai Science Park as a free zone community that serves the entire value chain of the science, health and pharma sectors, fostering an environment that supports research, creativity, innovation and passion, ensuring a supportive ecosystem for businesses to establish sustainable and positive change."
    source_type = "HTML"
    url = "https://dsp.ae/the-community/community-directory" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
