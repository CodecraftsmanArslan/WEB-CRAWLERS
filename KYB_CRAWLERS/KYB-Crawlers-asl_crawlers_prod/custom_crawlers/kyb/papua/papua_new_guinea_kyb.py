"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from old_range import data_array

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

def replace_na(data):
    for key, value in data.items():
        if value == "N/A":
            data[key] = ""
    return data

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''
    additional_detail  =[]
    # preparing additional_detail dictionary object
    status_details = dict()
    status_details['type']= 'status_information'
    status_details['data']=  [replace_na(record[10])]
    additional_detail.append(status_details)
    reference_entity = dict()
    reference_entity['type'] = 'reference_entity_information'
    reference_entity['data'] = [replace_na(record[-1])]
    if reference_entity['data'][0]['reference_entity_Url'] != "":
        additional_detail.append(reference_entity)
    contacts_detail = []
    if record[8]["e_mail"] != "N/A":
        email_detail = dict()
        email_detail['type']= 'email'
        email_detail['value'] = record[8]["e_mail"].replace("N/A", "") if "e_mail" in record[8] else ""
        contacts_detail.append(email_detail)

    if record[8]["phone_number"] != "N/A":
        phone_number_detail = dict()
        phone_number_detail['type'] = 'phone_number'
        phone_number_detail['value'] = record[8]["phone_number"].replace("N/A", "") if "phone_number" in record[8] else ""
        contacts_detail.append(phone_number_detail)

    meta_detail = dict()
    meta_detail["annual_return_due_date"] = record[7].replace("/","-")
    meta_detail["has_own_constitution"] = f"{record[11]['has_own_constitution']}" if record[11]["has_own_constitution"] != None else ""
    meta_detail["foreign_enterprise"] = f"{record[11]['foreign_enterprise']}" if record[11]["foreign_enterprise"] != None else ""
    meta_detail["registration_expiry_date"] = f"{record[11]['expiry_date']}" if record[11]["expiry_date"] != None else ""
    meta_detail["commencement_date"] = f"{record[11]['commencement_date']}" if record[11]["commencement_date"] != None else ""

    addresses_detail = []

    general_address = dict()
    general_address['type'] = "general_address"
    general_address['address'] = record[11]["address"].replace("<br />", "") if "address" in record[11] else ""


    postal_address = dict()
    postal_address['type'] = "postal_address"
    postal_address['address'] = record[11]["postal_address"].replace("<br />", "") if "postal_address" in record[11] else ""

    if postal_address['address'] != "" and postal_address['address'] != "N/A":
        addresses_detail.append(postal_address)
    if general_address['address'] != "" and general_address['address'] != "N/A":
        addresses_detail.append(general_address)


    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[0].replace("'","''"),
        "status": record[6].replace("'","''"),
        "registration_number": record[3],
        "registration_date": record[4].replace("'","''").replace("/","-"),
        "type": record[5].replace("'","''"),
        "industries": record[11]["business_activity"],
        "crawler_name": "custom_crawlers.kyb.papua_new_guinea_kyb",
        "country_name": "Papua New Guinea",
        "contacts_detail": contacts_detail, 
        "fillings_detail": record[9],
        "additional_detail": additional_detail,
        "addresses_detail": addresses_detail,
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{url_}{record[3]}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
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
        items = data_range()

        # Check if a command-line argument is provided
        if len(sys.argv) > 1:
            start_number = sys.argv[1]
        else:
            # Assign a default value if no command-line argument is provided
            start_number = '1-10001'

        # Split the start_number into its components
        start_number_parts = start_number.split('-')
        start_prefix = int(start_number_parts[0])
        start_suffix = int(start_number_parts[1])

        for item in items:
            # Split the item into its components
            item_parts = item.split('-')
            item_prefix = int(item_parts[0])
            item_suffix = int(item_parts[1])

            # Compare the start_number with the current item
            if start_prefix > item_prefix or (start_prefix == item_prefix and start_suffix > item_suffix):
                continue

            ids = item_id(item)
            print(item)
            for id in ids:

                api_url='https://www.ipa.gov.pg/Api/Corp/GetCorpProfile?id='+id
                response = requests.get(api_url, stream=True, headers={
                    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
                STATUS_CODE = response.status_code
                CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
                json_data = json.loads(response.text)
                DATA=[]
                api_name= json_data['Corp']['CompanyName'] if json_data.get('Corp') and json_data['Corp'].get('CompanyName') else ""
                address = json_data['Corp']['RegisteredOfficeAddress']['UIFormattedAddress'].replace("'","''") if json_data.get('Corp') and json_data['Corp'].get('RegisteredOfficeAddress') else ""
                postal_address = json_data['Corp']['PostalAddress']['UIFormattedAddress'].replace("'","''") if json_data.get('Corp') and json_data['Corp'].get('PostalAddress') else ""
                registration_number= json_data['Corp']['RegistrationNumber'] if json_data.get('Corp') and json_data['Corp'].get('RegistrationNumber') else ""
                registration_date=json_data['Corp']['RegistrationDateFormatted'] if json_data.get('Corp') and json_data['Corp'].get('RegistrationDateFormatted') else ""
                type_=json_data['Corp']['CompanyType'] if json_data.get('Corp') and json_data['Corp'].get('CompanyType') else ""
                status_= json_data['Corp']['Status'] if json_data.get('Corp') and json_data['Corp'].get('Status') else ""
                yearly_annual_return_due_date= json_data['Corp']['AnnualReturnDueDate'] if json_data.get('Corp') and json_data['Corp'].get('AnnualReturnDueDate') else ""
                contact_details= {
                    "e_mail": json_data['Corp']['EmailAddress'].replace("'","''") if json_data.get('Corp') and json_data['Corp'].get('EmailAddress') else "",
                    "phone_number": json_data['Corp']['PhoneNumber'] if json_data.get('Corp') and json_data['Corp'].get('PhoneNumber') else ""    
                }    
                foreign_enterprise = json_data['Corp']['IsForeign'] if json_data.get('Corp') and "IsForeign" in json_data['Corp'] else ""
                
                if foreign_enterprise is False:
                    foreign_enterprise = 'No'
                else:
                    foreign_enterprise = 'Yes'

                filing_details_list = []

                if json_data.get('CorpFilings') and len(json_data['CorpFilings']) > 0:
                    for filing in json_data['CorpFilings']:
                        filing_details = {}
                        filing_details["filing_code"] = filing.get('DocumentNumber', "")
                        filing_details["filing_type"] = filing.get('CorpFilingTypeAndFormNumber', "").replace("-", "").replace("'", "''")
                        filing_details["date"] = filing.get('ReceivedDateFormatted', "").replace("/", "-")
                        filing_details["meta_detail"] = {
                            "submission_date": filing.get('ProcessedDateFormatted', "").replace("/", "-")
                        }
                        filing_details_list.append(filing_details)
                
                status_details= {"status": json_data['CorpStatesHistory'][0]['CorpState'] if json_data.get('CorpStatesHistory') and len(json_data['CorpStatesHistory']) > 0 and json_data['CorpStatesHistory'][0].get('CorpState') else "", 
                        "form_type": json_data['CorpStatesHistory'][0]['CorpFilingTypeAndFormNumber'].replace("'", "''") if json_data.get('CorpStatesHistory') and len(json_data['CorpStatesHistory']) > 0 and json_data['CorpStatesHistory'][0].get('CorpFilingTypeAndFormNumber') else "", 
                        "effective_date": json_data['CorpStatesHistory'][0]['EffectiveDateOfChangeFormatted'].replace("/", "-") if json_data.get('CorpStatesHistory') and len(json_data['CorpStatesHistory']) > 0 and json_data['CorpStatesHistory'][0].get('EffectiveDateOfChangeFormatted') else "", 
                        "note": json_data['CorpStatesHistory'][0]['Note'] if json_data.get('CorpStatesHistory') and len(json_data['CorpStatesHistory']) > 0 and json_data['CorpStatesHistory'][0].get('Note') else ""}
                reference_entity_information = {
                    "reference_entity_Url": '',
                    "reference_entity_registration_number": ''
                }

                if json_data.get('Corp') and json_data['Corp'].get('ReferencedCorp'):
                    reference_entity_information["reference_entity_Url"] = 'https://www.ipa.gov.pg' + \
                        json_data['Corp']['ReferencedCorp'].get('EntityProfileUrl', '')

                    reference_entity_information["reference_entity_registration_number"] = \
                        json_data['Corp']['ReferencedCorp'].get('EntityRegistrationNumber', '')
                
                meta_details_= {
                    "has_own_constitution": json_data['Corp'].get('HasOwnConstitution', ''),
                    "business_activity": json_data['Activities'][0].get('CorpActivityType', '').replace("'","") if json_data.get('Activities') and len(json_data['Activities']) > 0 and json_data['Activities'][0].get('CorpActivityType') else "",
                    "address": address.replace("'","''"),
                    "postal_address": postal_address.replace("'","''"),
                    "expiry_date": json_data['Corp'].get('ExpiryDate', '').replace("/","-") if json_data['Corp'].get('ExpiryDate', '') != None else "",
                    "commencement_date": json_data['Corp'].get('CommencementDate', '').replace("/","-") if  json_data['Corp'].get('CommencementDate', '') != None else "",
                    "foreign_enterprise": foreign_enterprise
                }
                
                DATA.append([api_name, address, postal_address, registration_number, registration_date, type_, status_, yearly_annual_return_due_date, contact_details, filing_details_list, status_details, meta_details_, foreign_enterprise, reference_entity_information])
                for record_ in DATA:
                    DATA_SIZE += 1
                    record_for_db = prepare_data(record_, category,
                                                    country, entity_type, source_type, name, api_url, description)
                    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                    print("Stored record\n")
                    crawlers_functions.db_connection(query)

        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

def item_id(id):
    url = 'https://www.ipa.gov.pg/Api/Corp/SearchCorp'
    params = {
        'Term': id,
        'ExcludePending': 'true',
        'ExcludeNotReReg': 'false',
        'UseGenericSearch': 'false',
        'PaginationPageSize': 100,
        'PaginationCurrentPage': 1
    }

    max_retries = 3
    retry_count = 0
    data = None
    corp_ids = []

    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params)
            data = response.json()
            break  # Break out of the loop if successful
        except (requests.RequestException, json.JSONDecodeError) as e:
            print("Error occurred:", e)
            retry_count += 1
            time.sleep(60)
            if retry_count < max_retries:
                print("Retrying...")
            else:
                print("Maximum retry attempts reached")

    if data and "records" in data:
        # Retrieve the CorpId IDs from the response
        corp_ids = [item['CorpId'] for item in data['records']]
    
    return corp_ids
    

def data_range():
    # 1-10001 — to — 1-90948
    # 6-10001 — to — 6-343479    
    ranges = []
    ranges += [f"1-{i}" for i in range(10001, 90949)]
    ranges += [f"6-{i}" for i in range(10001, 343480)]
     
    return ranges
    

if __name__ == '__main__':
    '''
    Description: API Crawler for Papua New Guinea
    '''
    name = 'Investment Promotion Authority (IPA)'
    description = "This website is for the Investment Promotion Authority (IPA) of Papua New Guinea. It's a portal for searching for information related to businesses and corporations in Papua New Guinea. The IPA itself is a government agency responsible for promoting and facilitating investment in the country, and providing services such as business registration and licensing."
    entity_type = 'Company/Organisation'
    source_type = 'HTML'
    countries = 'Papua New Guinea'
    category = 'Official Registry'
    url = "https://www.ipa.gov.pg/corp/search.aspx"
    
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
