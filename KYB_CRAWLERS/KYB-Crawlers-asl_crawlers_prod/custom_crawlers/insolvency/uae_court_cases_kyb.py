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
    meta_detail['case_number'] = record[1]
    meta_detail['case_start_date'] = record[2]
    meta_detail['judgements'] = record[3]
    meta_detail['hearings'] = record[4]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.uae_court_cases_kyb.py",
        "country_name": "UAE",
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
        API_URL = "https://www.adgm.com/api/courtcase/GetCases?sc_itemid=d60a2589-7198-408e-951e-f3c4711abf02&sc_mode=normal&pageNumber={}&pageSize={}&startDate=&endDate=&orderByField=datecommenced_tdt&thenByOrderByField=case_number_s&orderDesc=true&caseType=true&searchText=&_=1683805306931"
        headers = {
                'authority': 'www.adgm.com',
                'method': 'GET',
                'path': '/api/courtcase/GetCases?sc_itemid=d60a2589-7198-408e-951e-f3c4711abf02&sc_mode=normal&pageNumber=1&pageSize=10&startDate=&endDate=&orderByField=datecommenced_tdt&thenByOrderByField=case_number_s&orderDesc=true&caseType=true&searchText=&_=1683805306931',
                'scheme': 'https',
                'accept': '*/*',
                'content-type': 'application/json',
                'referer': 'https://www.adgm.com/adgm-courts/cases',
                'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "macOS",
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
            }
        
        page_no = 1
        page_size = 10
        response = requests.get(API_URL.format(page_no,page_size), headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = response.json()
        pages = json_response['paginator']

        pager = BeautifulSoup(pages, 'html.parser')
        for page in pager.find_all('div', {'class':'px10'}):
            last_page = page.text
        page_size = page_size*int(last_page)

        response = requests.get(API_URL.format(page_no,page_size), headers=headers, timeout=60)
        json_data = response.json()
        template = json_data['tableResult']

        table_result = BeautifulSoup(template, 'html.parser')
        table = table_result.find('table', {'class':"judgments__table"})

        DATA = []
        for row in table.find_all('tr')[1:]:
            items = [td.text.split('v')[1].replace('\n','').replace('. ','') if ' v. ' in str(td) or ' v ' in str(td) else td.text.replace('\n','') for td in row.find_all('td')]
            
            if 'view' in str(row).lower():
                hearings = row.find('ul', {'class':'pl15'})
                judgements = []
                for each in hearings.find_all('li'):
                    hearing_item_text = []
                    for div in each.find_all('div'):
                        if 'view pdf' in str(div).lower():
                            hearing_url = div.find('a')['href']
                        else:
                            hearing_item_text.append(div.text)
                    judgements.append({'citation':' '.join(hearing_item_text), 'pdf_link':SOURCE_URL+hearing_url})
                record = [items[1],items[0],items[2],judgements,items[5]]
            else:
                record = [items[1],items[0],items[2],items[3],items[4]]

            DATA.append(record)

            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
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
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Bankruptcy/Insolvency/Liquidation"
    name ="Abu Dhabi Global Market"
    description = "Abu Dhabi Global Market is an international financial centre strategically located in the capital of the United Arab Emirates."
    source_type = "HTML"
    url = "https://www.adgm.com/adgm-courts/cases" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
