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
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
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
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

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
    meta_detail['file_information'] = record[1]
    meta_detail['company_information'] = record[2]
    meta_detail['monitor_information'] = record[3]
    

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
        driver.get(SOURCE_URL)        
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        URLs = []
        time.sleep(2)
        try:
            while True:
                urls_1 = driver.find_elements(By.CSS_SELECTOR, '#wb-auto-4 > tbody > tr > td > b > a')
                for each in urls_1:
                    URLs.append(each.get_attribute("href"))
                urls_2 = driver.find_elements(By.CSS_SELECTOR, '#wb-auto-4 > tbody > tr > td > strong > a')
                for each in urls_2:
                    URLs.append(each.get_attribute("href"))
                urls_3 = driver.find_elements(By.CSS_SELECTOR, "#wb-auto-4 > tbody > tr > td.sorting_1 > a")
                for each in urls_3:
                    URLs.append(each.get_attribute("href"))
                next_page = driver.find_element(By.XPATH, '//*[@id="wb-auto-4_next"]')

                if 'disabled' in str(next_page.get_attribute("class")).lower():
                    break
                else:
                    next_page.click()
                    time.sleep(2)
            driver.close()
        except Exception as e:
            print(e)
            driver.close()

        print("Total Rows: ", len(URLs))
        DATA = []
        for item in URLs:
            data = {'name':'', 'file_information':{}, 'company_information':{}, 'monitor_information':{}}
            response = requests.get(item, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)

            soup = BeautifulSoup(response.content, 'html.parser')
            data['name'] = soup.find('h1', {'id':'wb-cont'}).text
            contents = soup.select('div.content div')
            for content in contents:
                if 'clearfix' in str(content).lower():
                    continue
                if "court file number" in str(content).lower(): data["file_information"]["number"] = content.find_next('div').text
                elif "court and judicial district" in str(content).lower(): data["file_information"]["court_name"] = content.find_next('div').text.replace("'","''")
                elif "osb file number" in str(content).lower(): data["file_information"]["osb_file_number"] = content.find_next('div').text
                elif "date of the initial order" in str(content).lower(): data["file_information"]["date_of_order"] = content.find_next('div').text
                elif "monitor's web page" in str(content).lower(): data["file_information"]["moitors_webpage_link"] = content.find_next('div').text
                elif "company name" in str(content).lower(): data["company_information"]["name"] = content.find_next('div').text.replace("'","''")
                elif "other names under" in str(content).lower(): data["company_information"]["alliases"] = content.find_next('div').text.replace("'","''")
                elif "head office" in str(content).lower(): data["company_information"]["address"] = content.find_next('div').text.replace("'","''")
                elif "telephone" in str(content).lower(): data["company_information"]["phone_number"] = content.find_next('div').text
                elif "website" in str(content).lower(): data["company_information"]["internet_address"] = content.find_next('div').text
                elif "court-appointed monitor" in str(content).lower(): data["monitor_information"]["name"] = content.find_next('div').text.replace("'","''")
                elif "website" in str(content).lower(): data["monitor_information"]["internet_address"] = content.find_next('div').text
                elif "monitor's representative" in str(content).lower(): data["monitor_information"]["representative"] = content.find_next('div').text.replace("'","''")
                elif "address" in str(content).lower(): data["monitor_information"]["address"] = content.find_next('div').text.replace("'","''")
                elif "telephone" in str(content).lower(): data["monitor_information"]["phone_number"] = content.find_next('div').text
                elif "email" in str(content).lower(): data["monitor_information"]["email_address"] = content.find_next('div').text.replace("'","''")
                elif "date of the court order discharging" in str(content).lower(): data["monitor_information"]["date_of_court_order"] = content.find_next('div').text
                
            DATA.append(data)
        
        for each_ in DATA:
            record = [each_['name'],each_['file_information'],each_['company_information'],each_['monitor_information']]
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
    countries = "Canada"
    entity_type = "Company/Organization" 
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "Canada.ca"
    description = "The official website of the Government of Canada. The OSB  is responsible for administration of the Bankruptcy and Insolvency Act ( BIA ), as well as certain duties under the Companies' Creditors Arrangement Act ( CCAA ). Below is a list of all companies that have been granted protection under the Companies' Creditors Arrangement Act (CCAA) since September 18, 2009 ."
    source_type = "HTML"
    url = "https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/ccaa-records-list" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
