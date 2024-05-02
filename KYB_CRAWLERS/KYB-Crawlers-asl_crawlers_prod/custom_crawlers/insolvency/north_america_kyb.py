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
    meta_detail['address'] = record[1].replace("'","''")
    meta_detail['category'] = record[3].replace("'","''")
    meta_detail['assets'] = record[4].replace("'","''")
    meta_detail['creditors'] = record[6].replace("'","''")
    meta_detail['liabilties'] = record[5].replace("'","''")
    meta_detail['industry_type'] = record[7].replace("'","''")
    meta_detail['bankruptcy_date'] = record[2]
    meta_detail['creditors_list_url'] = record[-1]
    meta_detail['filling_data_url'] = record[-2]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.north_america_kyb",
        "country_name": "North America",
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
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find_all('table')[0]
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        DATA = {}
        i = 0
        for tr in trs[1:]:
            tds = tr.find_all('td')
            creditors_url,filling_url = None,None
            if tds[0].text.strip() == 'View Filing' or tds[0].text.strip() =='View Petition':
                filling_url = tds[0].find('a').get('href') if tds[0].find('a') is not None else None
                tds = trs[i-1].find_all('td')
                Name,Location,Date,Event,Est_Assets,Est_Liabilities,Est_Creditors,Industry = tds[0].text.strip(),tds[1].text.strip(),tds[2].text.strip(),tds[3].text.strip(),tds[4].text.strip(),tds[5].text.strip(),tds[6].text.strip(),tds[7].text.strip()
            elif tds[0].text.strip() == "View Creditor's List" or tds[0].text.strip().find("View Creditor's")!=-1:
                creditors_url = tds[0].find('a').get('href') if tds[0].find('a') is not None else None
                tds = trs[i-1].find_all('td')
                Name,Location,Date,Event,Est_Assets,Est_Liabilities,Est_Creditors,Industry = tds[0].text.strip(),tds[1].text.strip(),tds[2].text.strip(),tds[3].text.strip(),tds[4].text.strip(),tds[5].text.strip(),tds[6].text.strip(),tds[7].text.strip()
            else:
                Name,Location,Date,Event,Est_Assets,Est_Liabilities,Est_Creditors,Industry = tds[0].text.strip(),tds[1].text.strip(),tds[2].text.strip(),tds[3].text.strip(),tds[4].text.strip(),tds[5].text.strip(),tds[6].text.strip(),tds[7].text.strip()
            DATA[Name] = [Name,Location,Date,Event,Est_Assets,Est_Liabilities,Est_Creditors,Industry, filling_url, creditors_url]
            i += 0
            
            record_for_db = prepare_data(DATA[Name], category,country, entity_type, source_type, name, url, description)
                        
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
    Description: HTML Crawler for North America Insovency
    '''
    countries = "North America"
    entity_type = "Company/Organisation"
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "Profit Guard"
    description = "ProfitGuard is the provider of business credit information to the Industrial Sector in North America.Their cloud-based platform provides one-stop resources to get essential credit information, view recommended credit limits, exchange trade information, see how your customers are paying others and have key accounts monitored. Given Link provides business bankruptcy records dating back to 1997." 
    source_type = "HTML"
    url = "https://bankruptcylist.eprofitguard.com" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
