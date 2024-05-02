"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import pandas as pd
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
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

FORMA_DICT = json.load(open('./mapping/FORMA.json'))
ICZUJ_DICT = json.load(open('./mapping/ICZUJ.json'))
KATPO_DICT = json.load(open('./mapping/KATPO.json'))
NACE_DICT = json.load(open('./mapping/NACE.json'))
OKRESLAU_DICT = json.load(open('./mapping/OKRESLAU.json'))
ROSFORMA_DICT = json.load(open('./mapping/ROSFORMA.json'))
TYPCDOM_DICT = json.load(open('./mapping/TYPCDOM.json'))
ZPZAN_DICT = json.load(open('./mapping/ZPZAN.json'))
CISS2010_DICT = json.load(open('./mapping/CISS2010.json'))


def get_code_value(code, dict):

    if code !='':
        code =  str(int(code)) if isinstance(code, float) else code
        if code in dict:
            return dict[f'{code}']
        else:
            return ''
    return ''

def record_changed(value):
    if value !='':
        if value == 'P':
            return 'Increase in the record compared to the previous state'
        if value == 'Z':
            return 'change in the record compared to the previous state'
    return ''

def combine_string(value, string):
    if value != '':
        return string + " " + value + ","
    else:
        return ''

def change_float_type(value):

    if value:
        if isinstance(value, float):
            return int(value)
        else:
            return value
    else:
        return ''



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
    meta_detail['reason_for_dissolution'] = get_code_value(record['ZPZAN'], ZPZAN_DICT)
    meta_detail['date_of_agreement'] =str(record['DDATPAKT']).replace("'","''")
    meta_detail['form_of_incorporation'] = get_code_value(record['ROSFORMA'], ROSFORMA_DICT) 
    meta_detail['number_of_employees'] = get_code_value(record['KATPO'], KATPO_DICT) 

    meta_detail['payment_date'] = record['DATPLAT']
    meta_detail['record_changed'] = record_changed(record['PRIZNAK'])
    meta_detail['aliases'] = record['FIRMA'].replace("'","''")
    
    addresses_detail = dict()
    addresses_detail['type'] = "general_address"
    addresses_detail['address'] = str(record['TEXTADR']).replace("'","''") + " " + get_code_value(record['ICZUJ'], ICZUJ_DICT)+" " + combine_string(str(change_float_type(record['CDOM'])).replace("'","''"), "house number") + " " +combine_string(str(change_float_type(record['COR'])).replace("'","''"), "building number") + record['ULICE_TEXT'].replace("'","''") + " " + record['COBCE_TEXT'].replace("'","''")+ " " +record['OBEC_TEXT'].replace("'","''") +" "+ str(get_code_value(record['OKRESLAU'], OKRESLAU_DICT))  + " " + str(change_float_type(record['PSC'])) 
    addresses_detail['description'] = ""

    meta_details = dict()

    meta_details['address_code'] = str(change_float_type(record['KODADM'])).replace("'","''") #address code
    addresses_detail['meta_detail'] = meta_details
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['FIRMA'].replace("'","''"),
        "status": "liquidation" if "likvidaci" in record['FIRMA'] else "",
        "registration_number": str(record['ICO']),
        "registration_date": str(pd.to_datetime(record['DDATVZN'])),
        "dissolution_date": str(pd.to_datetime(record['DDATZAN'])) if record['DDATZAN'] else  '',
        "type": get_code_value(record['FORMA'], FORMA_DICT) ,
        "crawler_name": "crawlers.custom_crawlers.kyb.czech_republic.czech_Republic_kyb.py",
        "country_name": "Czech Republic",
        "company_fetched_data_status": "",
        "addresses_detail": [addresses_detail],
        "meta_detail": meta_detail,
        "additional_detail": [
            {
                "type": "industry_information",
                "data":[
                    {
                        'industry_classification': get_code_value(record['NACE'], NACE_DICT),
                        'institutional_sector': get_code_value(record['CISS2010'], CISS2010_DICT)
                    }
                ]

            } if record['NACE'] != '' or record['CISS2010'] != '' else ''
        ]
    }

    data_obj['additional_detail'] = [p for p in data_obj['additional_detail'] if p]
    
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
    data_for_db.append(shortuuid.uuid(str(record['ICO'])+str(record['OKRESLAU']+'czech_Republic_kyb'))) # entity_id
    data_for_db.append(record['FIRMA'].replace("'", "")) #name
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
        FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts'
        SOURCE_URL = url
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        
        with open("data.csv", "wb") as file:
            file.write(response.content)
        
        df = pd.read_csv('data.csv')
        df.fillna("",inplace=True)

        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
            
            query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record\n")
            if record_for_db[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: CSV Crawler for Czech Republic
    '''
    name = 'Ministry of Justice - Public Register'
    description = "Official website of Czech Statistical Office (CZSO) that provides access to the Register of Economic Entities as open data. This is a publicly available database that contains information on economic entities such as companies and entrepreneurs registered in the Czech Republic. The database provides details such as identification number, legal form, registered office, date of registration, and other relevant information for each entity listed."
    entity_type = 'Company/Organization'
    source_type = 'CSV'
    countries = 'Czech Republic'
    category = 'Official Registry'
    url = 'https://opendata.czso.cz/data/od_org03/res_data.csv'
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
