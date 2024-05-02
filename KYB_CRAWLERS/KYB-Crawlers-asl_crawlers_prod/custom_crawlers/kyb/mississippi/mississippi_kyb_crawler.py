import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import math
from time import sleep

# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
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

SOURCE = "Mississippi Secretary of State's Office"
COUNTRY = ['Mississippi']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://corp.sos.ms.gov/corpreporting/Corp/BusinessSearch3", 
                 "Source Description": "Official website of Mississippi Secretary of State's office that allows users to conduct customized searches of the state's corporations database. It provides information on businesses registered in Mississippi by name, entity type, registered agent, and more."}
IMAGES = []

def parse_json(data):
    if 'Data' in data:
        data = data['Data']
        ROWS = []
        for record in data:
            NAME = record['BusinessName']
            BusinessId = record['BusinessId']
            ENTITY_ID = shortuuid.uuid(f'{BusinessId}-{SOURCE}-{COUNTRY[0]}')
            FORMATION_DATE = record["FormationDate"][:record["FormationDate"].find('T')] if record['FormationDate'] else ""
            BIRTH_INCORPORATION_DATE = [FORMATION_DATE] if FORMATION_DATE else []

            ADDITIONAL_DETAIL = [{
                                "type": "naics_code",
                                "data": [
                                    {
                                        "naics_code1": record.get("NAICSCode1"),
                                        "naics_code2": record.get("NAICSCode2"),
                                        "naics_code3": record.get("NAICSCode3")
                                    }
                                ]
                            } if record.get("NAICSCode1") != "" or record.get("NAICSCode2") != "" or record.get("NAICSCode3") != "" else ""
            ]
            address_line1 = str(record.get("AddressLine1", "")).replace("NULL","")
            city = record.get("City", "")
            county = record.get("County", "")
            state_code = record.get("StateCode", "")
            postal_code = record.get("PostalCode", "")

            address = f"{address_line1 or ''} {city or ''} {county or ''} {state_code or ''} {postal_code or ''}".strip()

            ADDRESSES_DETAIL =  [{
                                "type": "general_address",
                                "address": address,
                            } if address != "" else None
            ]
            
            ADDRESSES_DETAIL = [e for e in ADDRESSES_DETAIL if e ]
            ADDITIONAL_DETAIL = [e for e in ADDITIONAL_DETAIL if e ]
            
            if record['Status'] == 'Undefined':
                status = ""
            else:
                status = record['Status']
            
            DATA = {
                "name": NAME,
                "status": status,
                "registration_number": BusinessId,
                "registration_date": FORMATION_DATE,
                "dissolution_date": "",
                "type": record["EntityType"],
                "crawler_name": "custom_crawlers.kyb.mississippi.mississippi_kyb_crawler",
                "country_name": "Mississippi",
                "company_fetched_data_status": "",
                "meta_detail": {
                        "aliases":record['OtherNames'] if record['OtherNames'] != None else '',
                        "domicile_type": record['DomicileType'],
                },
                "additional_detail": ADDITIONAL_DETAIL,
                "addresses_detail": ADDRESSES_DETAIL
            }

            ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE.replace("'", "''"),json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
            
            ROWS.append(ROW)
        return ROWS

# MAIN Execution
BASE_API_URL = 'https://corp.sos.ms.gov/corpreporting/Dataset/PublicSearch'
PER_PAGE = 500
PAYLOAD = {
            'sort': 'BusinessName-asc',
            'page': 1,
            'pageSize': PER_PAGE,
            'group':'',
            'filter': ''
        }
try:
    res = requests.post(BASE_API_URL, PAYLOAD)
except:
    sleep(30)
    try:
        res = requests.post(BASE_API_URL, PAYLOAD)
    except:
        pass
    
if res.status_code == 200:
    records = res.json()
    TOTAL_RECORDS = int(records['Total'])
    NUM_PAGES = math.ceil((TOTAL_RECORDS/PER_PAGE))
else:
    print('Invalid response from server')

data = parse_json(records)
insert_data(data)
for i in range(2, NUM_PAGES+1):
    print(f'Processing page: {i}/{NUM_PAGES+1}')
    PAYLOAD["page"] = i
    try:
        res = requests.post(BASE_API_URL, PAYLOAD)
    except:
        sleep(30)
        try:
            res = requests.post(BASE_API_URL, PAYLOAD)
        except:
            continue
    
    if res.status_code == 200:
        records = res.json()
        data = parse_json(records)
        insert_data(data)
    else:
        print('Invalid response from server')
        sleep(10)
        continue