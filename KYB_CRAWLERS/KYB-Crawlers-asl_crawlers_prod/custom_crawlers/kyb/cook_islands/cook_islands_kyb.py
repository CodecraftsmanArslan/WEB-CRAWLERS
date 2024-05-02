"""Set System Path"""
import sys
from pathlib import Path
import zipfile
sys.path.append('/Users/tayyabali/Desktop/work/ASL-Crawlers')
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
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def get_data(corpId):
    res = requests.get(f"https://registry.justice.gov.ck/Api/Corp/GetCorpProfile?id={corpId}")
    data = res.json()
    addresses_detail = []
    fillings_detail = []
    item = {}
    meta_detail = {}
    item["meta_detail"] = meta_detail
    item["crawler_name"] = "crawlers.custom_crawlers.kyb.cook_islands_kyb"
    item["country_name"] = "Cook Islands"
    item["name"] = data["Corp"]["CompanyName"].replace("'", "''") if data["Corp"]["CompanyName"] is not None else ""
    item["registration_number"] = data["Corp"]["RegistrationNumber"].replace("'","''") if data["Corp"]["RegistrationNumber"] is not None else ""
    item["type"] = data["Corp"]["CompanyType"].replace("'", "''") if data["Corp"]["CompanyType"] is not None else ""
    item["status"] = data["Corp"]["Status"].replace("'", "''") if data["Corp"]["Status"] is not None else ""
    item["registration_date"] = data["Corp"]["RegistrationDateFormatted"].replace("/", "-") if data["Corp"]["RegistrationDateFormatted"] is not None else ""
    item["meta_detail"]["is_foreign_enterprise"] = f"{data['Corp']['IsForeign']}"
    item["meta_detail"]["annual_return_due_date"] = data["Corp"]["AnnualReturnDueDateFormatted"].replace("/", "-")
    if data["Corp"]["RegisteredOfficeAddress"] is not None and data["Corp"]["RegisteredOfficeAddress"] != "":
        addresses_detail.append({
            "type": "office_address",
            "address": data["Corp"]["RegisteredOfficeAddress"].replace("<div>", " ").replace("</div>", " ").replace("  ", " ").replace("'", "''")
        })
    if data["Corp"]["PostalAddress"] is not None and data["Corp"]["PostalAddress"] != "":
        addresses_detail.append({
            "type": "postal_address",
            "address": data["Corp"]["PostalAddress"].replace("<div>", " ").replace("</div>", " ").replace("  ", " ").replace("'", "''")
        })

    principal_activity = ""
    for val in data["Activities"]:
        principal_activity += val.get("CorpActivityType")

    if data.get('CorpFilings') and len(data['CorpFilings']) > 0:
        for filing in data['CorpFilings']:
            filing_details = {}
            filing_details["filing_code"] = filing.get('DocumentNumber', "")
            filing_details["title"] = filing.get('CorpFilingTypeAndFormNumber', "").replace("-", "").replace("'", "''")
            filing_details["filing_date"] = filing.get('FilingDateFormatted', "").replace("/", "-")
            filing_details["meta_detail"] = {
                "effective_date": filing.get('EffectiveDateFormatted', "").replace("/", "-")
            }
            fillings_detail.append(filing_details)

    item["meta_detail"]["principal_activity"] = principal_activity
    item["addresses_detail"] = addresses_detail
    item["fillings_detail"] = fillings_detail
    return item

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''
    # preparing summary dictionary object
    data_obj = get_data(record["CorpId"])    
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
    data_for_db.append(shortuuid.uuid(f'{str(record["CorpId"])}-cook_islands_kyb')) # entity_id
    data_for_db.append(record["Name"].replace("'", "")) #name
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
        url_template = "https://registry.justice.gov.ck/api/corp/SearchCorp?Term=*&ExcludePending=true&UseGenericSearch=false&PaginationPageSize=455&PaginationCurrentPage={page}&OrderAscending=true"

        data = []
        for page in range(1, 456):
            json_url = url_template.format(page=page)
            response = requests.get(json_url, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            page_data = json.loads(response.text)
            data.extend(page_data["records"])

        df = pd.json_normalize(data)
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
            insertion_data, lang = crawlers_functions.check_language(
                record_for_db, source_type, url, description, name)
            print(insertion_data[7])
            if lang == 'en':
                crawlers_functions.language_handler(insertion_data, 'reports')
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
            else:
                query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                    *insertion_data)

            print("Stored record\n")
            if insertion_data[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: JSON Crawler for Cook Islands
    '''
    name = 'Cook Islands Registry Services, Ministry of Justice of the Cook Islands'
    description = "Official corporate registry search platform maintained by the Ministry of Justice of the Cook Islands. The website provides information on corporations registered in the Cook Islands and provides a range of relevant details such as the company name, registration status, and date of incorporation."
    entity_type = 'Company/Organization'
    source_type = 'JSON'
    countries = 'Cook Islands'
    category = 'Official Registry'
    url = "https://registry.justice.gov.ck/corp/search.aspx"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
