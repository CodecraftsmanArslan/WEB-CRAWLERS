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
    meta_detail['address'] = record[1].replace("'","''")
    meta_detail['date'] = record[2]
    meta_detail['filing_type'] = record[3].replace("'","''")
    meta_detail['company_lawyer'] = record[4].replace("'","''")
    meta_detail['trustee'] = record[5].replace("'","''")
    meta_detail['applicant'] = record[6].replace("'","''")
    meta_detail['applicant_lawyer'] = record[7].replace("'","''")
    meta_detail['industry_type'] = record[8]
    meta_detail['description'] = record[9].replace("'","''")
    meta_detail['detail_case_link'] = record[10]
    

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.canada_insolvency_insider_kyb",
        "country_name": "Canada",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[3]}-{record[-1]}-{record[5]}')) # entity_id
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
        payload = {"action":"facetwp_refresh",
                   "data":{"facets":{"location":[],"filing_type":[],"industry":[],"trustee":[],"applicant":[],"applicant_counsul":[],"company_counsul":[],"load_more":[2]},
                           "frozen_facets":{},
                           "http_params":{"get":[],"uri":"filing","url_vars":[]},
                           "template":"wp",
                           "extras":{"selections":True,"sort":"default"},
                           "soft_refresh":1,
                           "is_bfcache":1,
                           "first_load":0,
                           "paged":2}}
        headers = {
                'authority': 'insolvencyinsider.ca',
                'method': 'POST',
                'path': '/filing/',
                'scheme': 'https',
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://insolvencyinsider.ca',
                'referer': 'https://insolvencyinsider.ca/filing/',
                'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "macOS",
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
            }
        
        response = requests.post(SOURCE_URL, data=json.dumps(payload), headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        json_data = response.json()
        total_pages = json_data.get('settings').get("pager").get("total_pages")

        DATA = []
        # Pagination on API
        for i in range(1, total_pages+1):
            payload['data']['paged'] = i
            payload["data"]['facets']['load_more'] = [i]
            
            response = requests.post(SOURCE_URL, data=json.dumps(payload), headers=headers, timeout=60)

            json_data = response.json()
            template = json_data.get('template')
            soup = BeautifulSoup(template, "html.parser")

            page_content = soup.find("div",{'id':'content'})
            data = page_content.find_all('div')

            items_dict = {}
            for each in data:
                if "filing-entry" in str(each):
                    items_dict = {'name':each.select("h3.filing-name")[0].text, 'date':each.select("p.filing-date")[0].text, 'filing_type':'',
                            'company_counsel':'', 'trustee':'', 'applicant':'', 'applicant_counsel':'', 'industry':'', 'province':'',
                            'description':'', 'detail_case_link':''}
            
                    meta_data = each.find_all("p")
                    for meta in meta_data:
                        if "filing type" in str(meta).lower():
                            items_dict["filing_type"] = meta.find("a").text
                        elif "company counsel" in str(meta).lower():
                            items_dict["company_counsel"] = meta.text.replace("Company Counsel: ","")
                        elif "trustee:" in str(meta).lower():
                            items_dict["trustee"] = meta.text.replace("Trustee: ", "")
                        elif "applicant:" in str(meta).lower():
                            items_dict["applicant"] = meta.text.replace("Applicant:", "")
                        elif "applicant counsel:" in str(meta).lower():
                            items_dict["applicant_counsel"] = meta.text.replace("Applicant Counsel:", "")
                        elif "industry:" in str(meta).lower():
                            items_dict["industry"] = meta.find("a").text
                        elif "province:" in str(meta).lower():
                            items_dict["province"] = meta.find("a").text
                        elif "view case details" in str(meta).lower():
                            items_dict['detail_case_link'] = meta.find('a')['href']
                    
                    items_dict['description'] = each.select('div.filing-content p')[0].text
                    
                    DATA.append(items_dict)
        
        for each_ in DATA:
            record = [each_['name'],each_['province'],each_['date'],each_['filing_type'],each_['company_counsel'],each_['trustee']
                      ,each_['applicant'],each_['applicant_counsel'],each_['industry'],each_['description'],each_['detail_case_link']]
            record_for_db = prepare_data(record, category,country, entity_type, source_type, name, url, description)
                        
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
    Description: HTML Crawler for Canada Insovency
    '''
    countries = "Canada"
    entity_type = "Company/Organization"
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "Insolvency Insider"
    description = "Insolvency Insider is a publication which covers latest Canadian insolvency filings, court cases, news and more"
    source_type = "HTML"
    url = "https://insolvencyinsider.ca/filing/"  

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
