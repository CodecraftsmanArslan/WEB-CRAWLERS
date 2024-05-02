"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
from bs4 import BeautifulSoup
import shortuuid,time
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
    # preparing addresses_detail dictionary object
    addresses_ = []
    if record[2] != "":
        addresses_detail = {}
        addresses_detail["type"]= "general_address"
        addresses_detail["address"]= record[2].replace("'","''")
        addresses_.append(addresses_detail)
    # preparing summary dictionary object
    meta_detail = dict()  
    if record[1] != "":
        meta_detail['description'] = record[1].replace("'","''")
    contacts = []
    try:
        content_num = record[3].split(",")
        content_num = [{c.split(':')[0].strip().lower().replace(' ','_'):c.split(':')[1].strip()} for c in content_num]
        for con in content_num:
            contacts.append({
                "type": "contact_number",
                "value": str(list(con.values())[0]).replace(" orTerminal",""),
                "meta_detail": {"department":list(con.keys())[0] }
            })
    except Exception as e:
        # print(e)
        content_num = record[3]
        contacts.append(
                {
                "type": "contact_number",
                "value": content_num.replace(" orTerminal",""),
                })
    contact_detail = [
            {
                "type": "email",
                "value": record[4].replace("'","''"),
            } if record[4].strip() != '' else None,
            {
                "type": "website",
                "value": record[5].replace("'","''"),
            } if record[5].strip() != '' else None
    ]

    contact_detail.extend(contacts)
    contact_detail = [c for c in contact_detail if c]
   
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[0].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.cocos_keeling_islands.Cocos_(Keeling)_Islands_kyb",
        "country_name": "Cocos (Keeling) Islands",
        "contacts_detail":contact_detail,
        "meta_detail": meta_detail,
        "addresses_detail": addresses_
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
    data_for_db.append(shortuuid.uuid(record[3]+record[5]+'cocos_(Keeling)_Islands_kyb')) # entity_id
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
        for page in range(1, 10):
            url_template = 'https://iot-businesses.com.au/business_directory/page/{page}/?search_keyword=%5BIOTCocosKeelingIslandSearchKey%5D&directory_category&layout=list'
            url_ = url_template.format(page=page)
            response = requests.get(url_,headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all business listings
            listings = soup.select('#post-98 > div > div > div > div.et_pb_section.et_pb_section_1.et_pb_with_background.et_section_regular > div.et_pb_row.et_pb_row_4 > div > div > div > div > div.ebd-directory-listing-wrap.ebd-list-template-1.ebd-list-layout > div > div.ebd-list-details-wrap')
            # Loop through each listing and extract data
            data = []
            for listing in listings:
                name_ = listing.find('h2', class_='ebd-list-title').text.strip()
                try:
                    description_ = soup.find('div', class_='ebd-listing-description').text.strip().replace("[IOTChristmasIslandSearchKey]","").replace("[IOTBothLocationSearchKey]","").replace("[IOTCocosKeelingIslandSearchKey]","")
                except:
                    description_ = ""
                try:
                    address = listing.find('div', class_='ebd-address').text.strip()
                except:
                    address= ""
                try:
                    phone_num = listing.find('div', class_='ebd-phn-number').text.strip()
                except:
                    phone_num = ""
                try:
                    email = listing.find('div', class_='ebd-email-add').text.strip()
                except:
                    email = ""
                try:
                    website = listing.find('div', class_='ebd-webadd').text.strip()
                except:
                    website = ""
                data.append([name_, description_, address, phone_num, email, website])
           
            for record_ in data:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                print("stored records\n")
                if record_for_db[1].replace(' ', '') != '':
                    crawlers_functions.db_connection(query)

        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Cocos (Keeling) Islands
    '''
    name = 'Indian Ocean Territories Regional Development Organisation - Business Directory'
    description = "The directory includes information on businesses operating in a variety of fields, including tourism, hospitality, construction, and other industries. The information provided for each business includes the name and contact details of the business, as well as additional details such as business category and services offered."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Cocos (Keeling) Islands'
    category = 'Official Registry'
    url = 'https://iot-businesses.com.au/business_directory/?search_keyword=[IOTCocosKeelingIslandSearchKey]&directory_category='

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
