
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
import requests
import zipfile

# Load environment variables
load_dotenv()

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
        if row[1] != '':
            cursor.execute(query)
            conn.commit()
            print('INSERTED RECORD: ', i)

# Constants
SOURCE = 'Open Data Portal of the Singapore Government'
COUNTRY = ['Singapore']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.gov.sg/dataset/entities-with-unique-entity-number", 
                 "Source Description": "The platform provides comprehensive information related to the UENs of specific business entities such as the legal name, address, registration date, status, and more. The UEN is a unique identifier assigned to all companies and other types of business entities registered in Singapore. This particular dataset provides a list of all the entities that have been assigned a UEN in Singapore."}
IMAGES = []
INPUT_DIR = f'{os.getcwd()}/input'

# METHOD TO PARSE CSV
def parse_csv(fpath):
    print(f'processing {fpath}')
    reader = csv.DictReader(open(fpath,'r'))
    ROWS = []
    for row in reader:
        if not row.get('entity_name'):
            continue
        
        NAME = row['entity_name']
        ENTITY_ID = shortuuid.uuid(f"{row['uen']}-singapore_kyb_crawler")
        BIRTH_INCORPORATION_DATE = [row["uen_issue_date"]] if "uen_issue_date" in row else []
        STREET_NAME = row['reg_street_name'] if row['reg_street_name'] != 'na' else ""
        POSTTEL_CODE = row['reg_postal_code'] if row['reg_postal_code'] != 'na' else ""
        ADDRESS = f"{STREET_NAME}, {POSTTEL_CODE}"
        
        address_detail = [
                        {
                        "type": "registration_address",
                        "address": ADDRESS if ADDRESS != ", " else "",
                        "description": "",
                        # "meta_detail": 
                        #         {
                        #             "street_name": row["reg_street_name"] if row["reg_street_name"] != 'na'  else "",
                        #             "postal_code": row["reg_postal_code"] if row["reg_postal_code"] != 'na' else "",
                        #         }
                        } if ADDRESS != ", " else None
                    ]
        address_detail = [c for c in address_detail if c]

        DATA = {
                    "name": NAME,
                    "status": row["uen_status"],
                    "registration_number": row['uen'],
                    "registration_date": row["uen_issue_date"],
                    "dissolution_date": '',
                    "type": row["entity_type"],
                    "crawler_name": "custom_crawlers.kyb.singapore.singapore_kyb_crawler",
                    "country_name": "Singapore",
                    "company_fetched_data_status": "",
                    "addresses_detail": address_detail,
                    "meta_detail": {
                        "legal_authority": row["issuance_agency_id"]
                    }
                }
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE.replace("'", "''"),json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS



BASE_URL = 'https://data.gov.sg/dataset/entities-with-unique-entity-number'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def download_and_unzip_file():
    os.makedirs(INPUT_DIR, exist_ok=True)
    print('Download Zip File')
    
    res = requests.get('https://data.gov.sg/dataset/1434a08c-5a81-4453-9d7a-ed7a76c1869c/download', headers=HEADERS)
    print(res.status_code)
    f = open(f'{INPUT_DIR}/data.zip','wb')
    f.write(res.content)
    f.close()
    with zipfile.ZipFile(f'{INPUT_DIR}/data.zip', 'r') as zip_ref:
        zip_ref.extractall(INPUT_DIR)
    
    try:
        os.unlink(f'{INPUT_DIR}/metadata-entities-with-unique-entity-number.txt')
        os.unlink(f'{INPUT_DIR}/data.zip')
    except:
        print('errror while deleting files')


# Main entry
download_and_unzip_file()
# crawl downlaoded files

for fcsv in os.listdir(f'{INPUT_DIR}'):
    if fcsv == '.DS_Store':
        continue
    fpath = f'{INPUT_DIR}/{fcsv}'
    data = parse_csv(fpath)
    print(len(data))
    insert_data(data)