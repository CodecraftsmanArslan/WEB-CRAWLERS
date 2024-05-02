import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
import os
import csv
import sys
import json
import psycopg2
import requests
import shortuuid
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from dotenv import load_dotenv
from datetime import datetime
import math
import time
sys.path.append('../kyb')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'maldives/input/'
# ZIP file url
SOURCE_URL = "https://eip.fia.gov.tw/data/BGMOPEN1.zip"
# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
def insert_data(data):
    query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*data)
    if data[1] !='': 
        print("Record Inserted!")
        cursor.execute(query)
        conn.commit()

# Constants
SOURCE = 'Department of Commerce, Ministry of Economic Affairs'
COUNTRY = ['Taiwan']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://eip.fia.gov.tw/data/BGMOPEN1.zip", 
                 "Source Description": "Official open data portal of the Taiwan government, which provides access to a wide range of data resources related to various fields such as economy, finance, transportation, health, and more.The platform offers free and open access to valuable data resources that can be used by individuals, organizations, and businesses for research, planning, and decision-making."}
IMAGES = []

# method to download file
def download_file(filename):
    print('Downloading file')
    filename = 'input/BGMOPEN1.csv'
    response = requests.get(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=180,
            verify=False, proxies={
                "http": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
                "https": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
            })
    STATUS_CODE = response.status_code
    if not os.path.exists(filename):
        z = ZipFile(BytesIO(response.content))            
        z.extractall("input/")
        print('DOWNLOADED')
    else:
        print("FILE EXISTS!")


translation_count = 0


# METHOD TO PARSE CSV
def parse_csv(csv_path):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f)
    
    ROWS = []
    entry_count = 0
    for row in reader: 
        NAME = row['營業人名稱']
        BIRTH_INCORPORATION_DATE = []
        ENTITY_ID = shortuuid.uuid(f"{row['統一編號']}-{NAME}-taiwan_kyb_crawler")

        INDUSTRY_DATA = [
            {
                "industry_code": row[f'行業代號{i}'],
                "name": row[f'名稱{i}'].replace("'", "''")
            } for i in range(1, 4) if row[f'行業代號{i}']
        ]
  
        DATA = {
            "name": NAME,
            "status": "",
            "registration_number": row['統一編號'],
            "registration_date": "",
            "dissolution_date": "",
            "type": row['組織別名稱'],
            "crawler_name": "custom_crawlers.kyb.taiwan.taiwan_kyb_crawler",
            "country_name": "Taiwan",
            "company_fetched_data_status": "",
            "meta_detail": {
                "aliases": row['營業人名稱'],
                "head_office_registration_number": row['總機構統一編號'],
                "capital": row['資本額'],
                "uniform_invoice": row['使用統一發票'],
            },
            "addresses_detail": [
                {
                    "type": "primary_address",
                    "address": f"{row['營業地址']}",
                    "description": "",
                }
            ] if row['營業地址'].strip()  else [],
            
        }
        additional_detail = []
        if INDUSTRY_DATA:
            additional_detail.append({
                    "type": "industry_details",
                    "data": INDUSTRY_DATA
                })
            DATA["additional_detail"] = additional_detail
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
        insert_data(ROW)
    f.close()
    return ROWS

# Main execution entry point
if __name__ == '__main__':
    print('Processing:')
    filename = 'input/BGMOPEN1.csv'
    fpath = download_file(filename)
    data = parse_csv(filename)
    print(data)