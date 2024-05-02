import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
from io import StringIO

# Load environment variables
load_dotenv()
INPUT_DIR = 'australia/input'
URL = 'https://data.gov.au/data/dataset/ab7eddce-84df-4098-bc8f-500d0d9776d1/resource/d98a113d-6b50-40e6-b65f-2612efc877f4/download/afs_lic_202305.csv'

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
def insert_data(data):
    i = 0
    for row in data:
        i += 1
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,
                image,data,source,source_details,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
                '{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) 
                    DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', 
                    image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image 
                    THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}',is_format_updated='{13}'
                """.format(*row)
        cursor.execute(query)
        conn.commit()
        print('INSERTED RECORD ', i)

# Constants
SOURCE = 'Australian open government data'
COUNTRY = ['Australia']
CATEGORY = ['Financial Services']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.gov.au/data/dataset/ab7eddce-84df-4098-bc8f-500d0d9776d1/resource/d98a113d-6b50-40e6-b65f-2612efc877f4/download/afs_lic_202305.csv", 
                 "Source Description": "Data.gov.au is the central source of Australian open government data. Anyone can access the anonymised public data published by federal, state and local government agencies."}

IMAGES = []
# METHOD TO PARSE CSV
def parse_csv(csv_file):
    f = open(csv_file, 'r', encoding='cp1252')
    reader = csv.DictReader(f,delimiter=',')    
    ROWS = []
    for row in reader:
        NAME = row['AFS_LIC_NAME']
        BIRTH_INCORPORATION_DATE = [row["AFS_LIC_START_DT"].replace('/','-')]
        REGISTRATION_NUMBER = row["AFS_LIC_ABN_ACN"]
        ENTITY_ID = shortuuid.uuid(f"{row['AFS_LIC_NUM']}-{NAME}-{BIRTH_INCORPORATION_DATE[0]}")
        DATA = {
                "name": NAME,
                "status": '',
                "registration_number": REGISTRATION_NUMBER,
                "registration_date": row["AFS_LIC_START_DT"].replace('/','-'),
                "dissolution_date": "",
                "type": '',
                "crawler_name": "custom_crawlers.kyb.australia_financial_services",
                "country_name": "Australia",
                "company_fetched_data_status": "",
                "meta_detail": {
                    'register_name': row['REGISTER_NAME'],
                    'license_number': row['AFS_LIC_NUM'],
                    'license_start_date': row['AFS_LIC_START_DT'].replace('/','-'),
                    'previous_license_number': row['AFS_LIC_PRE_FSR'],
                    'address': f"{row['AFS_LIC_ADD_LOCAL']}, {row['AFS_LIC_ADD_STATE']}, {row['AFS_LIC_ADD_PCODE']}, {row['AFS_LIC_ADD_COUNTRY']}, ({row['AFS_LIC_LAT']}, {row['AFS_LIC_LNG']})",
                    'license_condition': row['AFS_LIC_CONDITION'],
                    'source_url': URL
                },
                "addresses_detail": [
                            {
                                "type": "office_address",
                                "address": f"{row['AFS_LIC_ADD_LOCAL']}, {row['AFS_LIC_ADD_STATE']}, {row['AFS_LIC_ADD_PCODE']}, {row['AFS_LIC_ADD_COUNTRY']}, ({row['AFS_LIC_LAT']}, {row['AFS_LIC_LNG']})",
                                "description": "Office address",
                                "locality": row['AFS_LIC_ADD_LOCAL'],
                                "state": row['AFS_LIC_ADD_STATE'],
                                "postal_code": row['AFS_LIC_ADD_PCODE'],
                                "country": row['AFS_LIC_ADD_COUNTRY'],
                                "latitude": row['AFS_LIC_LAT'],
                                "longitude": row['AFS_LIC_LNG']
                            }
                ],
              }
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS


# method to download file
def download_file(furl):
    print('Download file', furl)
    res = requests.get(furl)
    if res.status_code != 200:
        return None
    if res.status_code == 200:
        f = open(f'{INPUT_DIR}/finance_data.csv','wb')
        content = res.content
        f.write(content)
        f.close()
        return f.name
    else: 
        print('Invalid response from server: ', res.status_code)
    return None

# Entry point
download_file(URL)
data = parse_csv(f'{INPUT_DIR}/finance_data.csv')
print('Total records to insert ',len(data))
insert_data(data)
print('FINISHED')
exit(0)