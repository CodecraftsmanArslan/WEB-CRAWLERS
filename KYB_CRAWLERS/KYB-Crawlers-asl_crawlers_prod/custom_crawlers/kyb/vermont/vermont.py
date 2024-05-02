"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import wget
import pandas as pd
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
import pandas as pd
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
# FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/excel_csv/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'


def recurse_section(obj, section_details, row):
    """This function recurses through the section_details object and fill the data accordingly based on the type of section
    Args:
        obj (dict): the dictionary to add data to
        section_details (dict): the dictionary to recurse
        row (dict): the dictionary to get data from
    """
    for key in section_details:
        if isinstance(section_details[key],str):
            value = (' '.join([f"{key}" for key in [row[key] for key in section_details[key].split('+')]]) if section_details[key].split('+')[0] in list(row.keys()) else  section_details[key]).strip()
            obj[key] = value.replace("null", " ").replace("  ", "").replace("None", " ").replace("none", " ").replace('NONE', ' ').replace('noneO',"").strip()
        elif isinstance(section_details[key],dict):
            obj[key] = {}
            recurse_section(obj[key],section_details[key],row)
        elif isinstance(section_details[key],list):
            obj[key] = []
            for index, section in enumerate(section_details[key]):
                obj[key].append({})
                recurse_section(obj[key][index],section,row)
                
def get_listed_object(record,section_details):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @param section_details
    @return dict
    '''
    obj = {}
    recurse_section(obj, section_details, record)
    return obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, schema_):
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
    @return data_for_db:List<str/json>
    '''
    data_obj = get_listed_object(record,schema_)
    data_obj["additional_detail"] = [detail for detail in data_obj["additional_detail"] if detail["data"][0] and any(detail["data"][0].values())]
    data_obj["addresses_detail"] = [address for address in data_obj["addresses_detail"] if address["address"] != ""]
    try:
        data_obj["people_detail"] = [people_detail for people_detail in data_obj["people_detail"] if people_detail["name"] != ""]
    except:
        data_obj["people_detail"] = []
    try:
        people_detail_list = data_obj['people_detail']
        
        cleaned_people_detail = [
            person for person in people_detail_list
            if person.get('name') not in [None, 'NONE', 'None']
        ]
        data_obj['people_detail'] = cleaned_people_detail
    except KeyError:
        pass 
    
    for address_info in data_obj['addresses_detail']:
        if 'address' in address_info:
            address_info['address'] = address_info['address'].replace('NONE', ' ').replace('None', ' ').replace("none", " ").replace("  ", " ").replace('noneO',"")

    data_for_db = list()
    data_for_db.append(shortuuid.uuid(data_obj["registration_number"]+data_obj["name"])) # entity_id
    data_for_db.append(data_obj["name"].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(data_obj).replace("'","''")) # data
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


def get_records(source_type, entity_type, country, category, url, name, description,schema):
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
        FILE_PATH = os.path.dirname(os.getcwd()) + '/custom_crawlers/kyb/vermont/'
        FILENAME = url
        # SOURCE_URL = url
        
        # response = requests.get(SOURCE_URL, headers={
        #     'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        # STATUS_CODE = response.status_code
        # CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
      
        df = pd.read_excel(f'{FILENAME}')
        df.fillna("", inplace=True)
        DATA_SIZE = len(df)
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description, schema)
                        

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':

    name = 'Vermont Secertary of State'
    description = "Vermont Secretary of State Corporations and Business Services Division that allows businesses to register and manage their businesses online. The website provides a search tool that allows users to search for information about existing businesses in Vermont, as well as provides a platform for new businesses to register, file, and manage their business online."
    entity_type = 'Company/Organization'
    source_type = 'CSV'
    countries = 'Vermont'
    category = 'Official Registry'
    url = "https://bizfilings.vermont.gov/online/OnlineDashboard/FullDownload"
    
    with open("schema.json") as f:
        json_schema = f.read()
    json_schema = json.loads(json_schema)
    for source in json_schema:
        if not not json_schema[source]:
            number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,category, json_schema[source]['sheet_name'],name, description, json_schema[source]['schema'])
            logger = Logger({"number_of_records": number_of_records, "status": status,
                            "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"custom"})
            logger.log()
