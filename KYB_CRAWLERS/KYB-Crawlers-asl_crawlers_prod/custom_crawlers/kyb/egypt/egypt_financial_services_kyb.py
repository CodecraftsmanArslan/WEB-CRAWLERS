"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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


def googleTranslator(record_):
    """Description: This method is used to translate any language to english. It take name as input and return the translated name
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'","").replace('\"',"")
        
    except:
        return record_

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
    meta_detail['alias'] = record["اسم الشركة"].replace("'","")
    meta_detail['license_date'] = record["تاريخ الترخيص"] if 'تاريخ الترخيص' in record else ""
    meta_detail['address'] = googleTranslator(record["العنوان"].replace("'","") if 'العنوان' in record else "")
    meta_detail['license_number'] = record["رقم الترخيص"].replace("'","") if 'رقم الترخيص' in record else ""
    meta_detail['phone_number'] = record["تليفون"].replace("'","") if 'تليفون' in record else ""
    meta_detail['fax_number'] = record["فاكس"].replace("'","") if 'فاكس' in record else ""
    meta_detail['email_address'] = record["البريدالالكتروني"].replace("'","''") if 'البريدالالكتروني' in record else ""
    meta_detail['peoples_Detail'] = googleTranslator(record["رئيس مجلس الإدارة:عبد المحسن خلف احمد"].replace("'","") if 'رئيس مجلس الإدارة' in record else "")
    meta_detail['industry_type'] = googleTranslator(record["اسم  النشاط"].replace("'","") if 'اسم النشاط' in record else "")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":googleTranslator(record["اسم الشركة"].replace("'","")),
        "status": "",
        "registration_number": record['رقم الشركة'] if 'رقم الشركة' in record else "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.egypt.egypt_stock_market_kyb",
        "country_name": "Egypt",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail
    }
    
    return data_obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, table_url):
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
    data_for_db.append(shortuuid.uuid(record["اسم الشركة"]+record['رقم الشركة']+ table_url+ url+ description_)) # entity_id
    data_for_db.append(googleTranslator(record["اسم الشركة"].replace("'", ""))) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": table_url,
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
        
        for page_number in range(1,1374):
            DATA = []
            base_url = url
            SOURCE_URL = base_url+str(page_number)
            headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            verify=False
            response = requests.get(SOURCE_URL ,verify=verify,headers=headers)
            STATUS_CODE = response.status_code
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            DATA_SIZE = len(response.content)
            soup = BeautifulSoup(response.text, "html.parser")
            # Find all anchor tags (a) in the HTML
            content_urls= []
            
            tables = soup.find_all("table")[0]
            for row in tables.find_all("tr")[1:]:
                cells = row.find_all("td")
                table_urls = cells[1].find('a').get('href')
                content_urls.append(table_urls)
            
            for table_url in content_urls:
                content_response = requests.get(table_url,verify=verify, headers=headers)
                content_soup = BeautifulSoup(content_response.text, "html.parser")
                table = content_soup.find_all("table")[0]
                data_dict = {}
                # Loop through each row in the table (excluding the header row)
                for row_ in table.find_all("tr")[1:]:
                    # Find all the cells in the row
                    cells_ = row_.find_all("td")
                    # Extract the data from each cell
                    keys = cells_[0].get_text(strip = True).replace('\n', '').replace('   ', '')
                    try:
                        values = cells_[1].get_text(strip = True)
                    except:
                        values = cells_[0].get_text(strip = True)
                    data_dict[keys] = values
                    DATA.append(data_dict)
            
            for record in DATA:
                record_for_db = prepare_data(record, category,country, entity_type, source_type, name, url, description, table_url)
                query = """INSERT INTO reports_merged (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports_merged.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports_merged.image THEN reports_merged.image || '{6}'::jsonb ELSE reports_merged.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
                print("stored in database\n")
                crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Egypt
    '''
    name = 'Financial Regulatory Authority (FRA) - Egypt'
    description = "This website provides information on how to register and update records for companies in the Egyptian Stock Exchange Market. It also provides information on the required documents and fees for registration."
    entity_type = 'Company/ Organisation'
    source_type = 'HTML'
    countries = 'Egypt'
    category = 'Financial Services'
    url = "https://fra.gov.eg/%D8%AA%D8%B3%D8%AC%D9%8A%D9%84-%D9%88-%D8%AA%D8%AD%D8%AF%D9%8A%D8%AB-%D8%B3%D8%AC%D9%84%D8%A7%D8%AA-%D9%84%D8%B4%D8%B1%D9%83%D8%A7%D8%AA-%D8%B3%D9%88%D9%82-%D8%A7%D9%84%D9%85%D8%A7%D9%84/page/"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
