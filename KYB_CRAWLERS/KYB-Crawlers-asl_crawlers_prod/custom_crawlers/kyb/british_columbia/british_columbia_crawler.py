import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import sys
sys.path.append('../')
from helper_functions import iso_to_utc
from time import sleep

BASE_URL = 'https://www.orgbook.gov.bc.ca/api/v4/search/topic/facets?q=*&inactive=&category:entity_type={}&credential_type_id=&page={}&revoked=false'

ENTITY_TYPES = {
    'S': 'Society',
    'BC': 'BC Company',
    'SP': 'Sole Proprietorship',
    'GP': 'General Partnership',
    'CP': 'Cooperative',
    'A':'Extraprovincial Company',
    'B': 'Extraprovincial',
    'LP':'Limited Partnership',
    'C':'Continuation In',
    'ULC':'BC Unlimited Liability Company',
    'XP':'Extraprovincial Limited Partnership',
    'QE':'CO 1897',
    'LL':'Limited Liability Partnership',
    'XS':'Extraprovincial Society',
    'LLC':'Limited Liability Company',
    'CUL':'Continuation In as a BC ULC',
    'QD':'CO 1890',
    'BEN':'Benefit Company',
    'LIC':'Licensed (Extra-Pro)',
    'MF': 'Miscellaneous Firm',
    'REG': 'Registraton (Extra-pro)',
    'XL': 'Extrapro Limited Liability Partnership',
    'PA': 'Private Act',
    'QA': 'CO 1860',
    'QC': 'CO 1878',
    'QB': 'CO 1862',
    'CS': 'Continued In Society',
    'FOR': 'Foreign Registration',
    'CC': 'BC Community Contribution Company',
    'XCP': 'Extraprovincial Cooperative',
    'EPR': 'Extraprovincial Registration'
}

# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()

def format_date(val):
    date = ""
    try:
        date = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S%z").date().strftime("%Y-%m-%d")
    except:
        pass
    return date
def insert_data(data):
    for row in data:
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,
                image,data,source,source_details,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
                '{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) 
                    DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', 
                    image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image 
                    THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}',is_format_updated='{13}'
                """.format(*row)
        cursor.execute(query)
        conn.commit()
        print('INSERTED RECORD')

def parse_json_data(objects, typeOfCompany):
    results = objects['results']
    RESULTS = []
    for result in results:
        source_id = result['source_id']
        names = result['names']
        business_number = ""
        business_name = ""
        registration_date = ""
        effective_date = ""
        additional_detail = []
        for name in names:
            if name['type'] == 'entity_name':
                business_name = name['text']
            elif name['type'] == 'business_number':
                business_number = name['text']
        for attribute in result['attributes']:
            if attribute['type'] == 'registration_date':
                registration_date = format_date(attribute['value']) if "value" in attribute else ""
                effective_date = format_date(attribute['last_updated']) if "last_updated" in attribute else ""
        registry_link = result['credential_type']['issuer']['url'] if "credential_type" in result and "issuer" in result['credential_type'] and "url" in result['credential_type']['issuer'] else ""
        credential_id = result['credential_set']['latest_credential_id'] if "credential_set" in result and "latest_credential_id" in result["credential_set"] else ""
        verification_link = f"https://www.orgbook.gov.bc.ca/entity/{source_id}/credential/{credential_id}"
        additional_detail.append({
            "type": "authority_links",
            "data": [{
                "registry_link": registry_link,
                "verification_link": verification_link
            }]
        })
        status = 'Active' if not result['inactive'] else 'Inactive'
        ENTITY_ID = shortuuid.uuid(f'{source_id}-{business_number}-british_columbia_crawler')
        COUNTRY = ['British Columbia']
        CATEGORY = ['Official Registry']
        NAME = business_name
        SOURCE = 'OrgBook British Columbia'
        ENTITY_TYPE = 'Company/Organization'
        SOURCE_DETAIL = {"Source URL": "https://www.orgbook.gov.bc.ca/search?q=%2a&category%3Aentity_type=&credential_type_id=&inactive=&page=1", 
                         "Source Description": "Official search engine for the OrgBook BC platform, which is a blockchain-based platform maintained by the Government of British Columbia, Canada. The website provides information on businesses, organizations, and credentials registered in British Columbia, and provides a range of relevant details such as the legal name, registration status, and contact information for each entity."}
        # BIRTH_INCORPORATION_DATE = [effective_date]
        BIRTH_INCORPORATION_DATE = ""
        IMAGES = []
        
        DATA = {
                "name": NAME,
                "status": status,
                "registration_number": business_number if business_number != "" else "",
                "registration_date": registration_date,
                "type": typeOfCompany,
                "crawler_name": "custom_crawlers.kyb.british_columbia_crawler",
                "country_name": COUNTRY[0],
                "company_fetched_data_status": "",
                "meta_detail": {
                    "incorporated_in":COUNTRY[0],
                    "incorporation_number": source_id,
                    "effective_date": effective_date if effective_date is not None and effective_date != "" else registration_date
                },
                "additional_detail": additional_detail
            }
        print(DATA)
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
            json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
            SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en', True]

        RESULTS.append(ROW)
    return RESULTS
        
for eTypeCode, eTypeName in ENTITY_TYPES.items():
    url = BASE_URL.format(eTypeCode,1)
    RETRY_COUNT = -1
    print('Processing', url)
    data = None
    while data is None:
        try:
            res = requests.get(url)
            data = res.json()
        except:
            print('Error while parsing json, http_error_code: ', res.status_code)
            print('Retrying after 10 seconds')
            sleep(10)
            if RETRY_COUNT > 30:
                break
            RETRY_COUNT += 1
            continue        
    if data:         
        objects = data['objects']    
        items = parse_json_data(objects, eTypeName)
        insert_data(items)
        next_page = objects['next']
        RETRY_COUNT = -1
        while next_page:
            print('Processing', next_page)
            try:
                res = requests.get(next_page)
                data = res.json()
                objects = data['objects']
            except:
                if RETRY_COUNT > 30:
                    break
                RETRY_COUNT += 1
                continue        
            items = parse_json_data(objects, eTypeName)
            insert_data(items)
            next_page = objects['next']
print('FINISHED')
