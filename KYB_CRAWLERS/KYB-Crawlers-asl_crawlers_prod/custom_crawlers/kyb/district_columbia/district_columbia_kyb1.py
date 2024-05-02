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
    additional_detail_lst = []
    people_detail = {
        "name": record[3].replace("'", "''") +''+ record[5].replace("'", "''")+''+record[4].replace("'", "''"),
        "phone_number": str(record[6]).replace("'", "''"),
        "designation":'registered_agent',
    } 
    
    license_information = dict()
    license_information["type"] = "license_information"
    ldata_ = []
    lic_data = {
         "license_number": str(record[10]).replace("'","''"),
          "category_description": str(record[20]).replace("'","''"),
          "category": str(record[12]).replace("'","''"),
          "category_code": str(record[21]).replace("'","''"),
          "end_date": str(datetime.datetime.fromtimestamp(int(float(record[17]))/1000) if record["LICENSE_END_DATE"] != "" else ""),
          "issue_date": str(datetime.datetime.fromtimestamp(int(float(record[18]))/1000)if record["LICENSE_ISSUE_DATE"] != "" else ""),
          "tracking_number": str(record[27]).replace("'","''"),
          "last_modification_date": str(datetime.datetime.fromtimestamp(int(float(record[28]))/1000) if record[28] != "" else ""),
          "status": record[22].replace("'","''"),
    }
    ldata_.append(lic_data)
    license_information["data"] = ldata_
    
    additional_detail_lst.append(license_information)
    
    # preparing addresses_detail dictionary object
    addresses_detail_lst = [] 
    addresses_detail = dict()
    addresses_detail['type'] = "general_address"
    addresses_detail["address"] = record[7].replace("'","''") +' '+str(record[8]).replace("'","''")
    addresses_detail["description"] = ""
    addresses_detail['meta_detail'] = {
          "city":record["CITY"].replace("'","''"),
          "master_address_repository_identifier": record["MARADDRESSREPOSITORYID"].replace("'","''"),
          "ward": record["WARD"].replace("'","''"),
          "advisory_neighborhood_commission": record["ANC"].replace("'","''"),
          "single_member_district": record["SMD"].replace("'","''"),
          "district": record["DISTRICT"].replace("'","''"),
          "police_service_area": record["PSA"].replace("'","''"),
          "neighborhood_cluster": record["NEIGHBORHOODCLUSTER"].replace("'","''"),
          "business_improvement_district": record["BUSINESSIMPROVEMENTDISTRICT"].replace("'","''"),
          "latitude": str(record["LATITUDE"]).replace("'","''"),
          "longitude": str(record["LONGITUDE"]).replace("'","''"),
          "x_coordinates": str(record["XCOORD"]).replace("'","''"),
          "y_coordinates": str(record["YCOORD"]).replace("'","''"),
          "main_street":record['MAINSTREET']
    }
    
    billing_address = dict()
    billing_address['type'] = "billing_address"
    billing_address['address'] = record["BILLING_ADDRESS"].replace("'","''")+''+record['BILLING_ADDRESS_CITY_STATE_ZIP'].replace("'","''")
    billing_address['description'] = ""
    ad_meta_detail = dict()
    ad_meta_detail['billing_name'] = str(record["BILLING_NAME"]).replace("'","''")
    billing_address['meta_detail'] = ad_meta_detail
    
    addresses_detail_lst.append(billing_address)
    addresses_detail_lst.append(addresses_detail)
    contact_details = [
            {
                "type": "phone_number",
                "value": record[23],
                "meta_detail":{}
            } if record[23].strip() != "" else None
        ]
    
    contact_details = [c for c in contact_details if c]

    meta_details = dict()
    meta_details['last_updated'] = str(datetime.datetime.fromtimestamp(int(float(record["DCS_LAST_MOD_DTTM"]))/1000))
    meta_details['database_id'] = record['OBJECTID'] if 'OBJECTID' in record else ""
    meta_details['in_state'] = record['DC_ADDR_FLAG'] if 'DC_ADDR_FLAG' in record else ""
    meta_details["entity_name"] = record[2].replace("'","''")
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[13].replace("'","''"),
        "status": "",
        "registration_number": str(record[10]).replace("'","''"),
        "registration_date": str(datetime.datetime.fromtimestamp(int(float(record[19]))/1000) if record[19] != "" else ""),
        "dissolution_date": "",
        "type": "",
        "crawler_name": "custom_crawlers.kyb.district_columbia.district_columbia_kyb1",
        "country_name": "District of Columbia",
        "company_fetched_data_status": "",
        "additional_detail": additional_detail_lst,
        "addresses_detail": addresses_detail_lst,
        "people_detail": [people_detail],
        "contacts_detail": contact_details,
        "meta_detail": meta_details
    }
    if addresses_detail_lst[1]["address"] != "":
        data_obj["addresses_detail"] = addresses_detail_lst
    
    
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
    crawlers_name= 'district_columbia_kyb1'
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(record[24]+str(url)+crawlers_name)) # entity_id
    data_for_db.append(record[13].replace("'","''")) #name
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
        offset = 0
        while offset < 229000:
            api_url = f'https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/DCRA/MapServer/0/query?f=json&where=1%3D1&outFields=*&returnGeometry=false&resultOffset={offset}&resultRecordCount=1000' 
            response = requests.get(api_url)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            json_data = response.json()
            df = pd.DataFrame.from_records(d['attributes'] for d in json_data['features'])
            df.fillna("",inplace=True)
            if len(df) == 0:
                break
            df = df.astype(str)
            for record_ in df.iterrows():
                record_for_db = prepare_data(record_[1], category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                if record_for_db[1] != '':
                    crawlers_functions.db_connection(query)
            offset = offset+len(df)
            print('stored ', offset, ' records')
        return offset, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for District of Columbia
    '''
    name = 'Department of Consumer and Regulatory Affairs - Corporations Division'
    description = "The Department of Consumer and Regulatory Affairs - Corporations Division is a department of the District of Columbia government responsible for registering and regulating various types of business entities operating in the District of Columbia . The Corporations Division manages the registration process for legal entities including corporations, limited liability companies, partnerships, and other business structures, as well as ensuring compliance with relevant regulations governing these entities."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'District of Columbia'
    category = 'Official Registry'
    url = 'https://opendata.dc.gov/datasets/DCGIS::basic-business-licenses/explore'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
