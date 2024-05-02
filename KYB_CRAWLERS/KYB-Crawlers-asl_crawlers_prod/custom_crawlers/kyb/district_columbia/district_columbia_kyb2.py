"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
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
    # preparing additional_detail dictionary object
    
    people_detail = {
            "designation": "principal_owner",
            "name": record["PRINCIPALOWNER"].replace("'","''")
            }
    
    contact_details = [
            {
                "type": 'email',
                "value": record["EMAIL"].replace("'","''"),
                "meta_detail":{"contact_name": record["CONTACTNAME"].replace("'","''")}
            } if record["EMAIL"].strip() != "" else None, 
            {
                "type": 'phone_number',
                "value": record["PHONE"],
                "meta_detail":{}
            } if record["PHONE"].strip() != "" else None, 
            {
                "type": 'fax_number',
                "value": record["FAX"].replace("'","''"),
                "meta_detail":{}
            } if record["FAX"].strip() != "" else None,
            {
                "type": 'website_link',
                "value": str(record["WEBSITE"]).replace("'","''"),
                "meta_detail":{}

            } if record["WEBSITE"].strip() != "" else None 
    ]
    contact_details = [c for c in contact_details if c]
    additional_detail = []
    license_information = dict()
    license_information['type'] = 'license_information'
    license_information['data'] = [
        {
            "start_date":str(datetime.datetime.fromtimestamp(int(record["STARTDATE"])/1000)),
            "end_date":str(datetime.datetime.fromtimestamp(int(record["EXPIRATIONDATE"])/1000))
        }
    ]
    
    additional_detail.append(license_information)
    
    # preparing addresses details dictionary object
    addresses_detail = dict()
    addresses_detail['type'] = 'general_address'
    addresses_detail['address'] =record["ADDRESS"].replace("'","''")
    addresses_detail['meta_detail'] ={
          "master_address_repository_identifier": record["MAR_ID"].replace("'","''"),
          "ward": record["WARD"].replace("'","''"),
          "latitude": str(record["LATITUDE"]).replace("'","''"),
          "longitude": str(record["LONGITUDE"]).replace("'","''"),
          "x_coordinates": str(record["XCOORD"]).replace("'","''"),
          "y_coordinates": str(record["YCOORD"]).replace("'","''")
    }
    
    meta_detail = dict()
    meta_detail['description'] = record["BUSINESSDESC"].replace("'","''").replace("\t"," ")
    meta_detail["gis_last_modified_date"] = str(datetime.datetime.fromtimestamp(int(record["GIS_LAST_MOD_DTTM"])/1000))
    meta_detail['proposal_points'] = record['PROPOSALPOINTS'].replace("'","''")
    meta_detail['bid_price_reduction'] = record['BIDPRICEREDUCTION'].replace("'","''")
    meta_detail['certificates'] = record['OTHERCERTIFICATIONS'].replace("'","''")
    meta_detail["category"] = record["CATEGORIES"].replace("'","''")
    meta_detail["small_business_enterprise"] = record["SBE"].replace("'","''")
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["BUSINESSNAME"].replace("'","''"),
        "status": "",
        "registration_number": record["CERTIFICATIONNUMBER"],
        "registration_date": str(datetime.datetime.fromtimestamp(int(record["DATEESTABLISHED"])/1000)),
        "dissolution_date": "",
        "type": record["ORGANIZATIONTYPE"].replace("'","''"),
        "crawler_name": "custom_crawlers.kyb.district_columbia.district_columbia_kyb2",
        "country_name": "District of Columbia",
        "company_fetched_data_status": "",
        'incorporation_date':str(datetime.datetime.fromtimestamp(int(record["STARTDATE"])/1000)),
        "additional_detail": additional_detail,
        "addresses_detail": [addresses_detail],
        'contacts_detail': contact_details,
        "people_detail": [people_detail],
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
    crawlers_name= 'district_columbia_kyb2'
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(record["OBJECTID"] +record["CERTIFICATIONNUMBER"]+str(url)+record['BUSINESSNAME']+crawlers_name)) # entity_id
    data_for_db.append(record["BUSINESSNAME"].replace("'", "")) #name
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
        # Wait for the page to load
        i = 1000
        offset = 0
        while offset < 2000:
            api_url = f'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Business_Licensing_and_Grants_WebMercator/MapServer/33/query/?f=json&where=1%3D1&outFields=*&returnGeometry=false&resultOffset={offset}&resultRecordCount={i}'
            response = requests.get(api_url)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            json_data = response.json()
            df = pd.DataFrame.from_records(d['attributes'] for d in json_data['features'])
            if len(df) == 0:
                break
            df.fillna("",inplace=True)
            df = df.astype(str)
            for record_ in df.iterrows():
                record_for_db = prepare_data(record_[1], category,
                                                country, entity_type, source_type, name, url, description)
    
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
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
    description = "This dataset provided by the District of Columbia that contains information about basic business license applications received in the past 10 years. The dataset includes the license number, application date, business name, owner name, address, and other related information."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'District of Columbia'
    category = 'Official Registry'
    url = 'https://opendata.dc.gov/datasets/DCGIS::certified-business-enterprise/explore'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
