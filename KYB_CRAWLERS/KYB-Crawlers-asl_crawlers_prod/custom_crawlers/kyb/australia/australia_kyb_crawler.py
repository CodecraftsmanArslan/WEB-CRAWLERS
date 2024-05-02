import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
from io import StringIO
import pandas as pd

# Load environment variables
load_dotenv()
INPUT_DIR = 'australia/input'
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
SOURCE = 'Australian Securities and Investments Commission (ASIC)'
COUNTRY = ['Australia']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.gov.au/data/dataset/7b8656f9-606d-4337-af29-66b89b2eeefb/resource/5c3914e6-413e-4a2c-b890-bf8efe3eabf2/download/company_202303.csv", 
                 "Source Description": "The Australian Securities and Investments Commission (ASIC) is an independent commission of the Australian Government tasked with regulating and overseeing Australia's financial markets and financial services providers . The ASIC's responsibilities include enforcing financial services and corporations laws, promoting informed investor participation in the market, and maintaining and improving market fairness, transparency and efficiency. The ASIC also oversees the registration of companies and manages the national business names register."}
IMAGES = []

def get_previous_names(ACN,csv_file):
    previous_names = []
    ff = open(csv_file, 'r', encoding='utf-8')
    reader = csv.DictReader(ff,delimiter='\t')
    for row in reader:
        if row['ACN'] == ACN and row['Current Name Indicator'] != 'Y':
            try:
                _NAME = row['Company Name']
            except:
                row['Company Name'] = row['\ufeffCompany Name']
            previous_names.append(row)
    ff.close()
    return previous_names

# METHOD TO PARSE CSV
def parse_csv(csv_file):
    f = open(csv_file, 'r', encoding='utf-8')
    reader = csv.DictReader(f,delimiter='\t')
    ROWS = []
    
    for row in reader:
        previous_names = []
        if row['Current Name Indicator'] == 'Y':
            previous_names = get_previous_names(row['ACN'],csv_file)
        else:
            continue
        
        try:
            NAME = row['Company Name']
        except:
            row['Company Name'] = row['\ufeffCompany Name']
            NAME = row['\ufeffCompany Name']

        BIRTH_INCORPORATION_DATE = [row["Date of Registration"].replace('/','-')]
        ENTITY_ID = shortuuid.uuid(f"{row['ACN']}-{row['State Registration number']}-{BIRTH_INCORPORATION_DATE[0]}-australia_kyb_crawler")
        
        DATA = {
                "name": row["Company Name"],
                "tax_number":row["ABN"],
                "status": row["Status"],
                "registration_number": row["ACN"],
                "registration_date": row["Date of Registration"],
                "dissolution_date": "",
                "type": row["Type"],
                "crawler_name": "custom_crawlers.kyb.australia_kyb_crawler",
                "country_name": "Australia",
                "company_fetched_data_status": "",
                **({"additional_detail": [
                    {
                        "type":"category_information", 
                        "data":[
                            {
                             "category":row["Class"],
                             "sub_category": row["Sub Class"],
                            }
                        ]
                    }
                 ]} if row["Class"].strip() or row["Sub Class"].strip() else {}),
                "meta_detail": {
                    
                    "previous_state":row["Previous State of Registration"],
                    "state_registration_number":row["State Registration number"],
                    "last_updated":row["Modified since last report"],
                    "current_name_indicator":row["Current Name Indicator"],
                    "aliases":row["Current Name"],
                    "aliases_start_date":row["Current Name Start Date"].replace('/','-')
                },
                "previous_names_detail": [{"name": prev["Company Name"]} for prev in previous_names]
              }
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)

        if len(ROWS) == 10:
            insert_data(ROWS)
            ROWS = []
            
    f.close()
    insert_data(ROWS)
    return None

# method to download file
def download_file(furl):
    print('Download file', furl)
    res = requests.get(furl)
    if res.status_code != 200:
        return None
    if res.status_code == 200:
        f = open(f'{INPUT_DIR}/data.csv','wb')
        content = res.content
        f.write(content)
        f.close()
        return f.name
    else: 
        print('Invalid response from server: ', res.status_code)
    return None

# Entry point
URL = 'https://data.gov.au/data/dataset/7b8656f9-606d-4337-af29-66b89b2eeefb/resource/5c3914e6-413e-4a2c-b890-bf8efe3eabf2/download/company_202303.csv'
download_file(URL)
parse_csv(f'{INPUT_DIR}/data.csv')
print('FINISHED')