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
    meta_detail["naic#"] = record[0].replace("'","''")
    meta_detail["dom"] = record[0].replace("'","''")
    meta_detail["group_details"] = record[2]
    meta_detail["contact_details"] = record[3]
    meta_detail["cpaf"] = record[4].replace("'","''")
    meta_detail["dmv#"] = record[5].replace("'","''")
    meta_detail["admitted_dt"] = record[6].replace("'","''")
    meta_detail["fid"] = record[7].replace("'","''")
    meta_detail["address"] = record[9].replace("'","''")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[8].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.newyork.financial_services_commission",
        "country_name": "New York",
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
    data_for_db.append(shortuuid.uuid(f'{record[8]}{url_}')) # entity_id
    data_for_db.append(record[8].replace("'", "")) #name
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
        tables = soup.find_all('table')
        # Find all table rows except the first row
        try:
            rows = tables[1].find_all('tr')[1:]
            row1 = rows[0].find_all('td')
            naic_no = row1[1].text.strip()
            dom = row1[3].text.strip()
            group_name = row1[5].text.strip()
            phone = row1[6].text.strip()
            row2 = rows[1].find_all('td')
            group_no =  row2[5].text.strip()
            cpaf = row2[5].text.strip()
            row3 = rows[2].find_all('td')
        
            # try:
            website =  row3[3].text.strip()
            # except Exception as e:
                # website = ""

            dmv_no = row3[1].text.strip()

            try:
                admitted_dt = row3[5].text.strip()
            except Exception as e:
                admitted_dt = ""

            try:
                fid = row3[7].text.strip()
            except Exception as e:
                fid = ""

            group_details = { "group_name": group_name, "group_number": group_no }
            contact_details = { "phone_number": phone, "website": website}
            row4 = rows[3].find_all('td')
            # Find the first <br> tag within the <td> element
            br_tag = row4[0].find('br')

            # try:
                # Retrieve the text content of the first <br> tag
            text_before_br = br_tag.previous_sibling.strip()
            name_ = text_before_br
            # except:
            #     rows = tables[1].find_all('tr')
            #     br_tag = rows[6].find('br')
            #     text_before_br = br_tag.previous_sibling.strip()
            #     name_ = text_before_br

            # Retrieve the text content ignoring <br> tags
            text_content = row4[0].get_text(separator=' ').replace('\n', '')
            # Print the modified text content
            address = text_content.replace(name_, "").strip()
        except:
            rows = tables[1].find_all('tr')
            row5 = rows[5].find_all('td')
            website =  row5[3].text.strip()
            phone_row = rows[0].find_all('tr')[0]
            phone = phone_row.find_all('td')[7].text.strip()
            contact_details = { "phone_number": phone, "website": website}
            group_name = rows[1].find_all('td')[5].text.strip()
            group_number = rows[2].find_all('td')[5].text.strip()
            group_details = { "group_name": group_name, "group_number": group_number }
            cpaf = rows[0].find_all('tr')[1].find_all('td')[1].text.strip()
            dmv_no = row5[1].text.strip()
            admitted_dt = row5[5].text.strip()
            fid = row5[7].text.strip()
            br_tag = rows[6].find('br')
            text_before_br = br_tag.previous_sibling.strip()
            name_ = text_before_br
            text_content = rows[6].get_text(separator=' ').replace('\n', '')
            # Print the modified text content
            address = text_content.replace(name_, "").strip()

        DATA = []
        DATA.append([
            naic_no,
            dom,
            group_details,
            contact_details,
            cpaf,
            dmv_no,
            admitted_dt,
            fid,
            name_,
            address
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
    Description: API Crawler for New York
    '''
    name = 'New York Company Search - DFS Portal'
    description = "This website provide companies listing in New York State Department of Financial Services"
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'New York'
    category = 'Financial Services'
    urls = pd.read_csv(".//kyb/newyork/input/output.csv")
    for url in urls.iterrows():
        url = url[1][0]
        print(url)
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
