"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime, random
import shortuuid,time
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
from langdetect import detect
from selenium import webdriver
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

arguments = sys.argv
PAGE_NUMBER = int(arguments[1]) if len(arguments)>1 else 1

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''
    # preparing addresses_detail dictionary object
    addresses_detail = dict()
    addresses_detail["type"]= "general_address"
    addresses_detail["address"]= record[-3].replace("'","").replace('NULL','').replace('NONE','').replace('--None--','')
    
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['aliases'] = record[4].replace("'","")
    meta_detail['source_url'] = record[1].replace("'","")
    previous_names_details = [
        {
        'name' : record[3].replace("'","").replace("none","").replace("null","").replace('NULL','').replace('NONE','').replace('--None--','')
        } if record[3].replace("'","") != "" else None
    ]
    previous_names_details = [c for c in  previous_names_details if c ]
    # prepare addintiona detail object
    
    people_detail = [
        {
        "designation":"registered_agent",
        "name":record[-2].replace("'","").replace("none","").replace("null","").replace('NULL','').replace('NONE','').replace('--None--','')
        } if record[-2].replace("'","") != "N/A" else None
    ]
    people_detail = [c for c in people_detail if c]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","").replace('\"',""),
        "status": record[-1],
        "registration_number": record[2],
        "registration_date": "",
        "dissolution_date": "",
        "type": record[-4],
        "crawler_name": "crawlers.custom_crawlers.kyb.new_hampshire.new_hampshire_new",
        "country_name": "New Hampshire",
        "company_fetched_data_status": "",
        "people_detail":people_detail,
        "previous_names_detail":previous_names_details,
        "addresses_detail": [addresses_detail],
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{record[2]}{"new_hampshire_kyb"}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'",""), "Name": name_}
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


def get_proxies():
    proxies = []
    proxy_response = requests.get('https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/US/any/sourceip/direct/-/')
    if proxy_response.status_code == 200:
        # Split the response text by newline character to get a list of proxies
        proxy_list = proxy_response.text.split('\n')
        proxies.extend(proxy.strip() for proxy in proxy_list if proxy.strip())
    else:
        print("Failed to retrieve proxies. Status code:", proxy_response.status_code)
    if proxies:
        return random.choice(proxies)
    else:
        print("No proxies available.")
        return None


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
        pidx = PAGE_NUMBER
        is_page_counted = False
        proxies = get_proxies()
        while True:
            res = requests.get('https://quickstart.sos.nh.gov/online/BusinessInquire/LandingPageBusinessSearch', proxies={
                            "http": f'http://{proxies}',
                            "https": f'http://{proxies}'
                        })
            if not res:
                proxies = get_proxies()
                continue
            if res.status_code == 200:
                res = res
                break
            else:
                time.sleep(7)
        cookies_dict = res.cookies.get_dict()
        STATUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        while True:
            body = {
                "sortby": "BusinessID",
                "stype": "a",
                "pidx": str(pidx)
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": f"ASP.NET_SessionId={cookies_dict['ASP.NET_SessionId']}"
            }
            while True:
                data_res = requests.post('https://quickstart.sos.nh.gov/online/BusinessInquire/BusinessSearchList', 
                    headers=headers,
                    data=body, 
                    proxies={
                        "http": f'http://{proxies}',
                        "https": f'http://{proxies}'
                    }
                )
                print('data_res',data_res)
                if not data_res:
                    proxies = get_proxies()
                    continue
                if data_res.status_code == 200:
                    data_res = data_res
                    break
                else:
                    time.sleep(10)

            data = []
            soup = BeautifulSoup(data_res.content, 'html.parser')
            table = soup.find_all('table')[0]
            if not is_page_counted:
                page_count = soup.find('li',class_ = 'pageinfo').text.split(',')[0].split('of')[-1].strip()
                is_page_counted = True
            
            if pidx == int(page_count):
                break

            tbody = table.find('tbody')
            trs = tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                try:
                    cpname_ = tds[0].get_text(strip = True)
                    source_url  = 'https://quickstart.sos.nh.gov'+tds[0].find('a').get('href')
                    reg_num = tds[1].get_text(strip = True)
                    aliases = tds[2].get_text(strip = True)
                    previous_name =tds[3].get_text(strip = True)
                    type_ = tds[4].get_text(strip = True)
                    address = tds[5].get_text(strip = True)
                    registered_agent = tds[6].get_text(strip = True)
                    status = tds[7].get_text(strip = True)
                except:
                    source_url,reg_num, aliases, = " ", " ", " ",
                data.append([cpname_, source_url,reg_num,aliases,previous_name, type_, address, registered_agent, status])
            
            for record_ in data:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports_hampshire (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}')""".format(*record_for_db)
                
                print("Stored records \n")
                json_data = json.loads(record_for_db[7])
                registration_number = json_data['registration_number']
                record_name = record_for_db[1].strip()
                if not (record_name == '' and registration_number.strip() == ''):
                    crawlers_functions.db_connection(query)
            pidx += 1
            print('Page number:', pidx)

        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for New Hampshire
    '''
    name = 'New Hampshire Secertary of State'
    description = "Online tool that allows users to search for businesses registered in New Hampshire. The website is provided by the New Hampshire Secretary of State's office and allows users to search for businesses by name, identification number, registered agent, and more."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'New Hampshire'
    category = 'Official Registry'
    url = 'https://quickstart.sos.nh.gov/online/BusinessInquire/LandingPageBusinessSearch'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
