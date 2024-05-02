"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
from bs4 import BeautifulSoup
import pandas as pd
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
    # preparing meta_detail dictionary object
    meta_detail = dict()
    try:
        dob = str(pd.to_datetime(record[1]))
    except:
        dob = ""
    meta_detail['date_of_birth'] = dob
    try:
        meta_detail['order_date'] = str(pd.to_datetime(record[2],errors='coerce', format ='%d/%m/%Y'))
    except:
        meta_detail['order_date'] = ""
    meta_detail['period_of_restrictions'] = record[3]
    meta_detail['court_number'] = str(record[4]).replace("'","''")
    meta_detail['address'] = str(record[5]).replace("'","''")
    try:
        meta_detail['reason'] = str(record[6]).replace("'","''")
    except:
        meta_detail['reason'] = ""

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":str(record[0]).replace("'","''").replace("&nbsp"," "),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.insolvency.uk_insolvency_service_kyb",
        "country_name": "United Kingdom",
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
    data_for_db.append(shortuuid.uuid(str(record[0])+str(record[4])+str(url))) # entity_id
    data_for_db.append(str(record[0]).replace("'", "''").replace("&nbsp"," ")) #name
    try:
        dob = str(pd.to_datetime(record[1]))
    except:
        dob = []
    data_for_db.append(json.dumps([dob])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": str(record[-1]).replace("\t","").replace(" ","_"),
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
        response = requests.get(SOURCE_URL,verify = False, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup_ = BeautifulSoup(response.text, 'html.parser')
        font_tags = soup_.find_all("font")
        DATA=[]
        name_count = 0
        for font_tag in font_tags:
            name_aw = font_tag.find("b", text="Name:")
            if name_aw:
                name_text = name_aw.next_sibling.strip()
                a_tag = font_tag.find_next("p").find('a')['href']
                if a_tag:
                    new_link ='https://www.insolvencydirect.bis.gov.uk/IESdatabase/'+a_tag
                    
                    response_ = requests.get(new_link)
                    
                    soup = BeautifulSoup(response_.content, "html.parser")
                    if soup.find("td", text="No records returned") or response_.status_code == 200:
                        date_of_birth = soup.find("b", text="Date of Birth:").find_next_sibling(text=True).strip()
                        date_of_order = soup.find("b", text="Date of Order:").find_next_sibling(text=True).strip()
                        length_of_order = soup.find("b", text="Length of order:").find_next_sibling(text=True).strip()
                        court_number = soup.find("b", text="Court Number:").find_next_sibling(text=True).strip()
                        last_known_address = soup.find("b", text="Last Known Address:").find_next_sibling(text=True).strip()
                        conduct = soup.find("b", text="Conduct:").find_next_sibling(text=True).strip()
                        DATA.append([name_text, date_of_birth, date_of_order, length_of_order, court_number, last_known_address, conduct, new_link])
                    
                    elif response_.status_code == 404:
                        name_text  = name_text
                        date_of_birth, date_of_order, length_of_order, court_number, last_known_address, conduct, new_link = "", "", "", "", "", "", ""
                        DATA.append([name_text, date_of_birth, date_of_order, length_of_order, court_number, last_known_address, conduct, new_link])
                        
        for record in DATA:
            record_for_db = prepare_data(record, category,country, entity_type, source_type, name, url, description)        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record \n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for United Kindom Insolvency
    '''
    countries = "United Kingdom"
    entity_type = "Person"
    category = "Bankruptcy/Insolvency/Liquidation"
    name = "The Insolvency Register"
    description = "The IIR is an amalgamation of the individual insolvency, bankruptcy restrictions and debt relief restrictions registers. Search can be made either by Name Details or by Trading Name Details"
    source_type = "HTML"
    url = 'https://www.insolvencydirect.bis.gov.uk/IESdatabase/viewbrobrusummary-new.asp'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
