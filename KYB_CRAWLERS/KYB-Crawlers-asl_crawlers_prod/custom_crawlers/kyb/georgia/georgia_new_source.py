"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
import pandas as pd
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
    # preparing additional_detail dictionary object

    people_details = list()
    if len(record['corporationAffiliations']) > 0:
        for people in record['corporationAffiliations']:
            people_detail = {
                "name": people['personName'].replace("'", "''"),
                "designation": people['role'].replace("'", "''"),
                "appointment_date": people['date'],
                "meta_detail": {
                    "exPerson" : "Yes" if people['exPerson'] == True  else "No",
                    "shares" : people['share'],
                    "document_link": "https://api.companyinfo.ge/" + people['document_link'] if people['document_link'] else '',
                    "person_registration_number": people['registration_number']
                }  
            }
            people_details.append(people_detail) 
    
    addresses_detail = [
        {
            'type' : 'general_address',
            'address' : record['corporation']['address'].replace("'", "''"),
        }
    ] if record['corporation']['address'] else []
   
    contact_details = [
        {
            "type": "email",
            "value": record['corporation']['email'].replace("'", "''"),
            
        }
    ] if record['corporation']['email'] else []
    
    meta_detail = {
        "aliases": record['corporation']['name'].replace("'","''"),
    }


    data_obj = {
        "name": record['corporation']['name'].replace("'","''"),
        "status": record['status'],
        "registration_number": str(record['corporation']['idCode']).replace("'","''"),
        "registration_date": record['corporation']['registrationDate']['date'] if record['corporation']['registrationDate']['date']  else '',
        "dissolution_date": "",
        "type": record['legalFormEn'].replace("'", "''"),
        "crawler_name": "georgia_kyb",
        "country_name": "Georgia",
        "company_fetched_data_status": "",
        "addresses_detail": addresses_detail,
        "people_detail": people_details,
        "contacts_detail": contact_details,
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
    crawlers_name= 'georgia_kyb'
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(record['corporation']['idCode']+str(url)+crawlers_name)) # entity_id
    data_for_db.append(record['corporation']['name'].replace("'","''")) #name
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
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url

        arguments = sys.argv
        offset = int(arguments[1]) if len(arguments)>1 else 1

        while offset <= 41147: #41105

            print("page number", offset)
            api_url = f'https://api.companyinfo.ge/api/corporations/search?name=&idCode=&address=&email=&legalForm=&status=&registered_after=&registered_before=&page={offset}' 
            response = requests.get(api_url)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            json_data = response.json()

            df = pd.DataFrame.from_records(d for d in json_data['items'])
            df.fillna("",inplace=True)
            if len(df) == 0:
                break
           
            df = df.astype(str)
            for record_ in df.iterrows():

                details_url = f"https://api.companyinfo.ge/api/corporations/{record_[1]['id']}"
                response = requests.get(details_url)
                if response.status_code == 200:
                    json_data = response.json()
                    record_for_db = prepare_data(json_data, category,
                                                country, entity_type, source_type, name, url, description)

                    query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', data='{7}',updated_at='{10}'""".format(*record_for_db)
                    
                    crawlers_functions.db_connection(query)
                    print('record stored')
            offset += 1

        return offset, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Georgia
    '''
    name = 'Georgian National Agency of Public Registry'
    description = "Official corporate registry search platform maintained by the Georgian National Agency of Public Registry. The website provides information on companies registered in Georgia and provides a range of relevant details such as the company name, registration status, and date of incorporation."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Georgia'
    category = 'Official Registry'
    url = 'https://www.companyinfo.ge/ka/additional-search'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
