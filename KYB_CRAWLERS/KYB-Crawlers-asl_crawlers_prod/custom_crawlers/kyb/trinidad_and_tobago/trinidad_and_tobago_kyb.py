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
from helpers.crawlers_helper_func import CrawlersFunctions


import http

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except http.IncompleteRead as e:
            return e.partial
    return inner


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

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def create(record_, source_type, entity_type, country, category, url, name, description):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
        
        print("Stored record\n")
        crawlers_functions.db_connection(query)
    else:
        print("Something went wrong")

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

    meta_detail = {}
    if record['aliases_'] or record['identifier_number']:
        meta_detail["aliases"] = record['aliases_']
        meta_detail["identifier_number"] = record['identifier_number']
    
    addresses_detail = []
    if record['address'] != "":
        addresses_detail.append({
            "type" :"general_address",
            "address" : record['address'].replace("'", "''")
        })

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['title_'].replace("'",""),
        "registration_date": record['registration_date'].replace("/","-"),
        "registration_number": record['registration_number'].replace("'",""),
        "meta_detail": meta_detail,
        "status": record['status_'],
        "dissolution_date": record['dissolution_date_'],
        "type": record['type_'],
        "addresses_detail": addresses_detail,
        "crawler_name": "custom_crawlers.kyb.trinidad_and_tobago.trinidad_and_tobago_kyb",
        "country_name": "Trinidad And Tobago",
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
    ENTITY_ID = record['identifier_number'] + record['registration_date'] + record['address'].replace("'", "")
    data_for_db.append(shortuuid.uuid(f"{ENTITY_ID}-trinidad_and_tobago_kyb")) # entity_id
    data_for_db.append(record["title_"].replace("'", "")) #name
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

def get_data():
    s = requests.Session()

    res = s.get('https://rgd.legalaffairs.gov.tt/ttNameSearch/', verify=False)
    cookiesession1 = res.cookies.get_dict()['cookiesession1']
    res = s.get('https://rgd.legalaffairs.gov.tt/namesearch-server/webapi/en/session/ttNameSearch')
    jwt = res.headers['Set-Cookie'].split(';')[0]


    API_URL = 'https://rgd.legalaffairs.gov.tt/namesearch-server/webapi/en/search'

    HEADERS = {
        "Content-Type":"application/json",
        "Cookie":f"{jwt};cookiesession1={cookiesession1};",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    BODY = {"rvr-input-lang":"en","CompanyName":".","searchName":"ns-public-search"}

    res = s.post(API_URL, json=BODY, headers=HEADERS, timeout=1200, stream=True)
    with open('trinidad_and_tobago/input/data.json','w') as f:
        f.write(res.text)

    s.close()
    return 'input/data.json'

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

        get_data()
        # Read the JSON file
        with open('trinidad_and_tobago/input/data.json') as file:
            data = json.load(file)

        # Extract keys and store them in an array
        keys = []
        for fields in data['resultset']:
            item = {}
            item["title_"] = fields['fields']['CompanyName'].replace("'","")
            item["type_"] = fields['fields']['RecordType'].replace("'","''")
            item["status_"] = fields['fields']['RecordStatus'].replace("'","''")
            item["dissolution_date_"] = fields['fields']['ExpiryDate'].replace("/", "-") if "ExpiryDate" in fields['fields'] else ""

            item["aliases_"] = ""
            if 'ProposedAlternateNames:1' in fields['fields']:
                proposed_alternate_names = [value for key, value in data['fields'].items() if key.startswith('ProposedAlternateNames')]
                proposed_alternate_names_str = ', '.join(proposed_alternate_names)
                item["aliases_"] = proposed_alternate_names_str.replace("'", "''")

            current_street_address = fields['fields']['CurrentStreetAddress'] if "CurrentStreetAddress" in fields['fields'] else ""
            current_state = fields['fields']['CurrentState'] if "CurrentState" in fields['fields'] else ""
            item["address"] = f"{current_street_address}, {current_state}" if current_state else current_street_address
            item["identifier_number"] = fields['fields']['CompanyIdentifier'] if "CompanyIdentifier" in fields['fields'] else ""
            item["registration_date"] = fields['fields']['RegistrationDate'] if "RegistrationDate" in fields['fields'] else ""           
            item["registration_number"] = fields['fields']['CompanyNumber'] if "CompanyNumber" in fields['fields'] else ""
                
            DATA_SIZE += 1
            create(item, source_type, entity_type, country, category, url, name, description)

        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: Crawler Trinidad And Tobago
    '''
    name = "Registrar General''s Department"
    description = "This is the website of the Trinidad and Tobago Companies Registry, which is run by the Registrar General's Department under the Ministry of Attorney General and Legal Affairs . The Companies Registry is responsible for the registration of companies and businesses in Trinidad and Tobago, and maintains a database of registered companies."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Trinidad And Tobago'
    category = 'Official Registry'
    url = "https://rgd.legalaffairs.gov.tt/ttNameSearch/"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
