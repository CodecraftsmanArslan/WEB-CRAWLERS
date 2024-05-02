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
import requests, json, os
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
    meta_detail['industry_details'] = record[3]
    meta_detail['aliases'] = record[4]
    meta_detail['license_type'] = record[6]
    meta_detail['incorporation_date'] = str(pd.to_datetime(record[8]))
    meta_detail['license_end_date'] = record[9]
    meta_detail['financial_year_end'] = record[12]
    meta_detail['capital_details'] = record[13]

    additional_detail = record[11]
    people_detail = record[10]
    addresses_detail = record[2]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": record[5],
        "registration_number": record[1],
        "registration_date": "",
        "dissolution_date": "",
        "type": record[7],
        "crawler_name": "crawlers.custom_crawlers.kyb.uae.uae_difc_freezone_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "people_detail": people_detail,
        "addresses_detail": addresses_detail,
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-uae_difc_freezone_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[8]))])) #dob
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
        API_URL = "https://retailportal.difc.ae/api/v3/public-register/overviewList?page={}&keywords=&companyName=&registrationNumber=&type=&status=&latitude=0&longitude=0&sortBy=&difc_website=1&data_return=true&isAjax=true"

        headers = {
            'Authority':'retailportal.difc.ae',
            'Method':'GET',
            'Path':'/api/v3/public-register/overviewList?page=1&keywords=&companyName=&registrationNumber=&type=&status=&latitude=0&longitude=0&sortBy=&difc_website=1&data_return=true&isAjax=true',
            'Scheme':'https',
            'Accept':'text/html, */*; q=0.01',
            'Accept-Language':'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin':'https://www.difc.ae',
            'Referer':'https://www.difc.ae/',
            'Sec-Ch-Ua':'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile':'?0',
            'Sec-Ch-Ua-Platform':"macOS",
            'Sec-Fetch-Dest':'empty',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-site',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        
        page_no = 1

        while True:
            response = requests.get(API_URL.format(page_no), headers=headers, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            json_response = response.json()
            print('Page No: ', page_no)
            if json_response['success'] == False and json_response.get('data') is None:
                break
            page_no += 1

            data = json_response['data']
            soup = BeautifulSoup(data, 'html.parser')

            sub_urls = soup.find_all('h4')
            DATA = []
            for sub_ in sub_urls:
                item_link = sub_.find('a')['href']
                
                item_response = requests.get(item_link, headers={
                    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}, timeout=60)
                soup = BeautifulSoup(item_response.content, 'html.parser')

                company_name = soup.find('h1').text.replace("'","")
                registration_number = soup.select_one('div.register-top > div > div > div.col-sm-6.left > div:nth-child(3) > div:nth-child(2) > p').text
                address = soup.select_one('div.register-top > div > div > div.col-sm-6.right > div > div:nth-child(2) > p').text.replace("'","")
                industry_details = soup.select_one('div.register-top > div > div > div.col-sm-6.left > div:nth-child(2) > div:nth-child(2) > p').text.replace("'","")
                company_information = soup.find_all('div', {'class':'col-sm-6'})

                addresses_detail = [{'type':'address','address':address}]

                company_secretary = ''
                for info in company_information:
                    if 'company information' in str(info).lower():
                        for div_tag in info.find_all('div', {'class':'col-sm-6'}):
                            if 'trading name' in str(div_tag).lower():
                                aliases = div_tag.find_next_sibling().find('p').text.replace("'","")
                            if 'status of registration' in str(div_tag).lower():
                                item_status = div_tag.find_next_sibling().find('p').text
                            if 'type of license' in str(div_tag).lower():
                                license_type = div_tag.find_next_sibling().find('p').text
                            if 'legal structure' in str(div_tag).lower():
                                item_type = div_tag.find_next_sibling().find('p').text
                            if 'date of incorporation' in str(div_tag).lower():
                                incorporation_date = div_tag.find_next_sibling().find('p').text
                            if 'commercial license validity date' in str(div_tag).lower():
                                license_end_date = div_tag.find_next_sibling().find('p').text
                            if 'commercial license validity date' in str(div_tag).lower():
                                license_end_date = div_tag.find_next_sibling().find('p').text
                            if 'directors' in str(div_tag).lower():
                                direct_list = div_tag.find_next_sibling().find_all('p')
                                directors = [direct.text.replace("'","") for direct in direct_list]
                            if 'company secretary' in str(div_tag).lower():
                                cs_list = div_tag.find_next_sibling().find_all('p')
                                company_secretary = [cs_.text.replace("'","") for cs_ in cs_list]
                            if 'dnfbp' in str(div_tag).lower():
                                dnfbp_list = div_tag.find_next_sibling().find_all('p')
                                dnfbp = [dn_.text.replace("'","") for dn_ in dnfbp_list]
                            if 'shareholders' in str(div_tag).lower():
                                sh_list = div_tag.find_next_sibling().find_all('p')
                                shareholders = [sh_.text.replace("'","") for sh_ in sh_list]
                            if 'financial year end' in str(div_tag).lower():
                                financial_year_end = div_tag.find_next_sibling().find('p').text
                            
                            capital_details = div_tag.find_next_sibling().find('p').text if 'share capital' in str(div_tag).lower() and div_tag.find_next_sibling() else ""

                additional_detail = []
                additional_detail.append({'type':'shareholders', 'data':shareholders})
                
                people_details = []
                people_details.append({'type':'directors', 'data':directors})
                people_details.append({'type':'company_secretary', 'data':company_secretary})
                people_details.append({'type':'dnfbp', 'data':dnfbp})

                DATA.append([company_name, registration_number, addresses_detail, industry_details, aliases, item_status, license_type, item_type, incorporation_date,
                             license_end_date, people_details, additional_detail, financial_year_end, capital_details])
                record = [company_name, registration_number, addresses_detail, industry_details, aliases, item_status, license_type, item_type, incorporation_date,
                         license_end_date, people_details, additional_detail, financial_year_end, capital_details]


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
    Description: HTML Crawler for UAE DIFC Freezone
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Free Zones/ Investment Promotion"
    name ="Dubai International Financial Centre (DIFC)"
    description = "The DIFC is one of the world’s most advanced financial centres and the leading financial hub for the Middle East, Africa and South Asia (MEASA), which comprises 72 countries with an approximate population of 3 billion and a nominal GDP of US$ 8 trillion."
    source_type = "HTML"
    url = "https://www.difc.ae/public-register/?companyName=%20&registrationNo=&status=&type=&sortBy=" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
