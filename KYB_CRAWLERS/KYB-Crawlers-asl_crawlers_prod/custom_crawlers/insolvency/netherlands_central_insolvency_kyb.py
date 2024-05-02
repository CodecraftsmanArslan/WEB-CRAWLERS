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
    meta_detail['bankruptcy_end_details'] = record[1]
    meta_detail['publication_details'] = record[2]
    meta_detail['authorized_liquidators'] = record[3]
    meta_detail['court_details'] = record[4]
    meta_detail['financial_details'] = record[5]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.netherlands_central_insolvency_kyb.py",
        "country_name": "Netherlands",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{record[2]}')) # entity_id
    data_for_db.append(record[0].replace("'", "").replace('"', '')) #name
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
        API_URL = "https://insolventies.rechtspraak.nl/Services/WebInsolventieService/zoekOpRechtspersoon"
        DETAILS_URL = "https://insolventies.rechtspraak.nl/Services/WebInsolventieService/haalOp/?id={}"
        FINANCIAL_DETAILS_URL = "https://insolventies.rechtspraak.nl/Services/VerslagenService/findGoedgekeurdeVerslagen/{}"
        pay_load = {
            "model": "{\"naam\":\"*\",\"KvKNummer\":\"\",\"postcode\":\"\",\"huisnummer\":\"\",\"type\":\"rechtspersoon\"}"
        }
        headers = {
            '__requestverificationtoken': 'aqw9LSj4f0LEfrSgKItiwrElKiuTIZZyOx-mhyFAqta7UqY4DDiao0jhKNX24T2x_HePwFgod6wG_9BUTzspM4eiR-s1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'insolventies.rechtspraak.nl',
            'Origin': 'https://insolventies.rechtspraak.nl',
            'Referer': 'https://insolventies.rechtspraak.nl/',
            'Cookie': "__RequestVerificationToken=cYmyJ1bdfL4QKlN8SGgMxdftmdheKWIMHkAqNKOpYrAVtBb9vQAjLuNSJy83emOXb5GSU-DFzsCRE1k90qTXQrERTRk1; stg_returning_visitor=Thu%2C%2011%20May%202023%2010:56:24%20GMT; stg_traffic_source_priority=2; _pk_ses.a9eb1fb4-1209-45e3-8a15-9da9c613d63a.aac0=*; stg_externalReferrer=https://app.clickup.com/; _pk_id.a9eb1fb4-1209-45e3-8a15-9da9c613d63a.aac0=2e40ff945e5fc3f8.1683801191.2.1683873496.1683871176.; stg_last_interaction=Fri%2C%2012%20May%202023%2006:58:37%20GMT",
            'Sec-Ch-Ua':'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }

        response = requests.post(API_URL, data=json.dumps(pay_load), headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = response.json()
        keys = json_response['result']['model']['items']

        details_payload = {"id": ""}
        details_headers = {
            '__RequestVerificationToken': 'cYmyJ1bdfL4QKlN8SGgMxdftmdheKWIMHkAqNKOpYrAVtBb9vQAjLuNSJy83emOXb5GSU-DFzsCRE1k90qTXQrERTRk1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': '__RequestVerificationToken=cYmyJ1bdfL4QKlN8SGgMxdftmdheKWIMHkAqNKOpYrAVtBb9vQAjLuNSJy83emOXb5GSU-DFzsCRE1k90qTXQrERTRk1; stg_returning_visitor=Thu%2C%2011%20May%202023%2010:56:24%20GMT; stg_traffic_source_priority=2; _pk_ses.a9eb1fb4-1209-45e3-8a15-9da9c613d63a.aac0=*; stg_externalReferrer=https://app.clickup.com/; _pk_id.a9eb1fb4-1209-45e3-8a15-9da9c613d63a.aac0=2e40ff945e5fc3f8.1683801191.2.1683874719.1683871176.; stg_last_interaction=Fri%2C%2012%20May%202023%2007:06:12%20GMT',
            'Host': 'insolventies.rechtspraak.nl',
            'Referer': 'https://insolventies.rechtspraak.nl/',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }

        DATA = []
        for key in keys:
            details_payload['id'] = key['publicatiekenmerk']
            response = requests.get(DETAILS_URL.format(key['publicatiekenmerk']), data=json.dumps(details_payload), headers=details_headers, timeout=60)
            
            details_data = response.json()

            name_item = details_data['model']['persoon']['achternaam'].replace("'", "").replace('"', '')
        
            bankruptcy_end_details = []
            for bankruptcy in details_data['model']['handelendOnderDeNamen']:
                detail_dict = {'name': bankruptcy['handelsnaam'].replace("'", "").replace('"', ''), 'chamber_of_commerce_number': bankruptcy['KvKNummer']}
                detail_dict['business_address'] = ["{} {} {} {}".format(b_address['straat'],b_address['huisnummer'], b_address['postcode'], b_address['plaats']).replace("'", "").replace('"', '') for b_address in bankruptcy['vestigingsadressen']]
                bankruptcy_end_details.append(detail_dict)
            publication_details = []
            for publication in details_data['model']['publicatiegeschiedenis']:
                public_dict = {'bankruptcy_notice':publication['publicatieOmschrijving'].replace("'", "").replace('"', ''), 'date':publication['publicatieDatum'], 'feature':publication['publicatieKenmerk'].replace("'", "").replace('"', '')}
                publication_details.append(public_dict)
            authorized_liquidators = []
            for curator in details_data['model']['curators']:
                curator_dict = {'name':"{} {} {}".format(curator['titulatuur'],curator['voorletters'],curator['achternaam']).replace("'", "").replace('"', ''),
                                'address': "{} {} {} {}".format(curator['adres']['straat'],curator['adres']['huisnummer'],curator['adres']['postcode'],curator['adres']['plaats']).replace("'", "").replace('"', ''),
                                'phone_number':curator['adres']['telefoonnummer']}
                authorized_liquidators.append(curator_dict)
            court_details = {'judge_name':details_data['model']['RC'].replace("'", "").replace('"', ''), 'case_number':details_data['model']['toezichtZaaknummer'].replace("'", "").replace('"', ''),
                             'insolvency_number':details_data['model']['landelijkUniekZaaknummer'].replace("'", "").replace('"', '')}
            
            financial_response = requests.get(FINANCIAL_DETAILS_URL.format(details_data['model']['landelijkUniekZaaknummer']), headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
            financial_details = []
            if financial_response.status_code == 200:
                financial_data = financial_response.json()
                
                for fd in financial_data:
                    f_data = {'title':fd['Titel'].replace("'", "").replace('"', ''), 'report_date':fd['DatumVerslagen'].replace("'", "").replace('"', ''), 'attribute':fd['VerslagKenmerk'].replace("'", "").replace('"', '')}
                    financial_details.append(f_data)
            
            DATA.append([name_item, bankruptcy_end_details, publication_details, authorized_liquidators, court_details, financial_details])

            record = [name_item, bankruptcy_end_details, publication_details, authorized_liquidators, court_details, financial_details]
            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',source='{9}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record.")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for North America Insovency
    '''
    countries = "Netherlands"
    entity_type = "Company/Organisation"
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "Central Insolvency Register"
    description = "This is the website of the Dutch judiciary's database of insolvency cases. It provides information about bankruptcies, debt restructuring, and other insolvency-related cases being processed in the Netherlands."
    source_type = "HTML"
    url = "https://insolventies.rechtspraak.nl/#!/resultaat?naam=*&KvKNummer=&postcode=&huisnummer=&type=rechtspersoon"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
