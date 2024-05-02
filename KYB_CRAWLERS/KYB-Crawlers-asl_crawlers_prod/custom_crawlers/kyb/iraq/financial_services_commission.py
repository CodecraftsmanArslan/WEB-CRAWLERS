"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from lxml import etree
import re

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
    @param countries
    @param category_
    @param entity_type
    @return dict
    '''

    meta_detail = dict()
    meta_detail["capital"] = record[1].replace("'","''")
    meta_detail["address"] = record[2].replace("'","''")
    meta_detail["phone_number"] = record[3].replace("'","''")
    meta_detail["email_address"] = record[4].replace("'","''")
    meta_detail["financial_statements"] = record[5]
    meta_detail["peoples_detail"] = record[6]
    meta_detail["news"] = record[7]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.iraq.financial_services_commission",
        "country_name": "Iraq",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{url_}{record[2]}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record))) # data
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
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        name_ = soup.find('h1').text.strip()

        page_body = soup.find(class_='page-body')
        text_rows = page_body.find_all(text=True)
        text_rows_ = "" 
        for row in text_rows:
            if row.strip():
                text_rows_ = text_rows_ + row.strip() + '\n'
      
        capital_match = re.search(r"Capital: (.+)", text_rows_)
        address_match = re.search(r"Address: (.+)", text_rows_)
        telephone_match = re.search(r'(?:Telephone number|Phone):\s*(.+)', text_rows_)
        email_match = re.search(r'(?:Email|Email Address):\s*(.+)', text_rows_)

        capital = capital_match.group(1) if capital_match else ""
        address = address_match.group(1) if address_match  else ""
        telephone = telephone_match.group(1) if telephone_match and 'Email' not in  telephone_match.group(1) else ""
        email = email_match.group(1) if email_match else ""

        # Extracting Financial Reports Source URL
        financial_reports_url = [a['href'] for a in soup.find_all('a', class_='btn-orange')]
        financial_reports_url = [x for x in financial_reports_url if x != ""]
        financial_reports_url = ['https://www.isc.gov.iq/' + url for url in financial_reports_url]


        table = page_body.find('table')
        peoples_detail = []
        if table:
            # Extract header names
            header_row = soup.find('tr')
            # headers = [header.text.strip() for header in header_row.find_all('td')]
            headers = ['designation', 'name']
            # Extract data rows
            data_rows = soup.find_all('tr')[1:]

            # Extract key-value pairs
            for row in data_rows:
                columns = row.find_all('td')
                if len(columns) == len(headers):
                    row_data = {}
                    for i, column in enumerate(columns):
                        row_data[headers[i]] = column.text.strip()
                    peoples_detail.append(row_data)      
        
        # Extracting News related to the company
        news_related = soup.select('div.news-car-related-item')
        news_head_link = []
        for news in news_related:
            news_head_link.append(soup.find('a', class_='news-head')['href'])

        base_link = 'https://www.isc.gov.iq/index.php'

        # Add the base link to each item in the array
        new_links = [base_link + link for link in news_head_link]

        DATA = []
        DATA.append([
            name_,
            capital,
            address,
            telephone,
            email,
            financial_reports_url,
            peoples_detail,
            new_links
        ])

        for record_ in DATA:
            record_for_db = prepare_data(record_, category,
                                            country, entity_type, source_type, name, url, description)
                        
            
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: API Crawler for Iraq
    '''
    name = 'Securities Commission'
    description = "The Securities Commission is a regulator of the stock exchange and has established by Law No. (74) 2004 and it has financial and administrative independence and the purpose of its establishment is to protect investors with securities in the stock market."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Iraq'
    category = 'Financial Services'
    urls = pd.read_csv(".//kyb/iraq/input/financial_services_commission.csv")
    for url in urls.iterrows():
        url = url[1][0]
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
