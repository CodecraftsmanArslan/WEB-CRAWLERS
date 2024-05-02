"""Set System Path"""
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import requests, json,os, time
from bs4 import BeautifulSoup
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

arguments = sys.argv
DUMMY_COR = int(arguments[1]) if len(arguments)>1 else 1
end_number = int(arguments[2]) if len(arguments)>2 else 2900267

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
    meta_detail['place_of_formation'] = record['Place of Formation']
    principal_address = record['Principal Address'].replace("'","''").replace("NONE","").replace("NULL","") if record['Principal Address'] != 'Not Provided' else ''
    principal_mailing_address = record['Principal Mailing Address'].replace("'","''").replace("NONE","").replace("NULL","") if record['Principal Mailing Address'] != 'Not Provided' else ''

    address_detail = [
        {"type": "general_address", "address": principal_address} if principal_address != '' else None,
        {"type": "postal_address", "address": principal_mailing_address} if principal_mailing_address != '' else None
    ]

    address_detail = [c for c in address_detail if c]
    register_agent_name = record.get('Registered Agent Name', '').replace("'","''") if record.get('Registered Agent Name') != 'Not Provided' else ''
    incor_name = record.get('Incorporator Name','').replace("'","''") if record.get('Incorporator Name') != 'Not Provided' else ''

    people_detail = [
        {
            'designation': 'registered_agent',
            'name': register_agent_name,
            'address': record.get('Registered Office Street Address', '').replace("'","''") if record.get('Registered Office Street Address') != 'Not Provided' else '',
            'postal_address': record.get('Registered Office Mailing Address', '').replace("'","''") if record.get('Registered Office Mailing Address') != 'Not Provided' else ''
        } if register_agent_name != '' else None,
        {
            'designation': 'incorporator',
            'name': incor_name,
            'address': record.get('Incorporator Street Address', '').replace("'","''") if record.get('Incorporator Street Address') != 'Not Provided' else '',
            'postal_address': record.get('Incorporator Mailing Address', '').replace("'","''") if record.get('Incorporator Mailing Address') != 'Not Provided' else ''
        } if incor_name != '' else None,
        {
            'designation': 'director',
            'name': record.get('Director Name', '').replace("'","''").replace("NULL","").replace("NONE",""),
            'address': record.get('Director Street Address', '').replace("'","''").replace("NULL","").replace("NONE",""),
            'postal_address': record.get('Director Mailing Address', '').replace("'","''").replace("NONE","")
        } if 'Director Name' in record else None
    ]
    people_detail = [c for c in people_detail if c]

    capital_info = {
    'authorized_share_capital': record.get('Capital Authorized', '') if 'Capital Authorized' in record else '',
    'capital_paid_in': record.get('Capital Paid In', '') if 'Capital Paid In' in record else ''
    }

    if not capital_info['authorized_share_capital'] and not capital_info['capital_paid_in']:
        additional_information = []
    else:
        additional_information = [
            {
                'type': 'capital_information',
                'data': [capital_info] if any(capital_info.values()) else []
            }
        ]
   

    fillings_detail = [
        {
            'date':record['Year'] if 'Year' in record else "",
            'file_url':record['Year']if 'Year' in record else ""
        } if 'Year' in record else None
    ]
    fillings_detail =[c for c in fillings_detail if c]
    
    previous_names_detail = [
        {
            'name':record['Legal Name Changed From'].replace("'","''") if 'Legal Name Changed From' in record else "",
            "update_date": record['Transaction Date'] if 'Transaction Date' in record else ""
        }  if 'Legal Name Changed From' in record else None
    ]
    previous_names_detail = [c for c in previous_names_detail if c]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record['name'].replace("'","''"),
        "status": record['Status'],
        "registration_number": record['Entity ID Number'],
        "registration_date": "",
        "dissolution_date": "",
        "incorporation_date":record['Formation Date'].replace("/","-"),
        "type": record['Entity Type'].replace("'","''"),
        "industries":record['Nature of Business'].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.alabama.alabama_official_registry",
        "country_name": "Alabama",
        "company_fetched_data_status": "",
        "addresses_detail":address_detail,
        "additional_detail":additional_information,
        "fillings_detail":fillings_detail,
        "people_detail":people_detail,
        "previous_names_detail":previous_names_detail,
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
    data_for_db.append(shortuuid.uuid(record['Entity ID Number']+'alabama_official_registry.py')) # entity_id
    data_for_db.append(record['name'].replace("'", "")) #name
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
        dummy_cor = DUMMY_COR
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        while True:
            corp = str(dummy_cor).zfill(9)
            print('corp',corp)
            SOURCE_URL = f'https://arc-sos.state.al.us/cgi/corpdetail.mbr/detail?corp={corp}'
            response = requests.get(SOURCE_URL, headers = headers, timeout=120)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Find the table element containing the data
            DATA = []
            data = {}
            dummy_cor += 1
            if not soup.find_all('table'):
                if corp != '002900267':
                    continue
                
                break
            table = soup.find_all('table')[1]
            trs = table.find_all('tr')
            thead = table.find_all('thead')
            cpname_= thead[0].find('tr').find('td').get_text(strip=True)
            for tr in trs[1:]:
                tds = tr.find_all('td')
              
                key = tds[0].get_text(strip=True)
                try:
                    value = tds[1].get_text(separator=' ', strip=True)
                except:
                    value = ""
                data['name'] = cpname_
                data[key] =  value
            DATA.append(data)
           
            for record in DATA:
                record_for_db = prepare_data(record, category,country, entity_type, source_type, name, url, description)
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                print("Stored records\n")
                crawlers_functions.db_connection(query)
        
            print(f"Page {dummy_cor}\n")
            

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Alabama
    '''
    name = 'Alabama Secretary of State'
    description = "It provides a wide range of services and resources related to business filings, elections, and government information. The website offers various tools and features to assist individuals, businesses, and organizations in accessing important information and conducting official transactions."
    entity_type = 'Company/ Organisation'
    source_type = 'HTML'
    countries = 'Alabama'
    category = 'Official Registry'
    url = 'https://arc-sos.state.al.us/cgi/corpdetail.mbr/detail?corp=000000001'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
