import pandas as pd
import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
import sys
sys.path.append('../kyb')
from helper_functions import dmy_en_month_to_number

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'maldives/input/'
# Xlsx files urls
FILES_URLS = {
    'Companies':'https://business.egov.mv/BusinessRegistry/ExportToExcel/3',
    'Sole Proprietorship': 'https://business.egov.mv/BusinessRegistry/ExportToExcel/10',
    'Partnership': 'https://business.egov.mv/BusinessRegistry/ExportToExcel/4',
    'Cooperative Society': 'https://business.egov.mv/BusinessRegistry/ExportToExcel/5'
}
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

# Constants
SOURCE = 'Business Portal,Government of Maldives'
COUNTRY = ['Maldives']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://business.egov.mv/BusinessRegistry", 
                 "Source Description": "Official business registry provided by the government of Maldives. The website allows users to search for registered businesses and business owners in the Maldives using various search criteria such as company name, registration number, and owner name."}
IMAGES = []

# method to download file
def download_file(ftype, furl):
    print('Downloading file', ftype)
    res = requests.get(furl, headers=headers)
    if res.status_code == 200:
        f = open(f'{INPUT_DIR}{ftype}.xlsx','wb')
        f.write(res.content)
        f.close()
        return f.name
    else: 
        print('Invalid response from server: ', res.status_code)
    return None

# method to convrt xlsx to formatted csv
def convert_xlsx_to_csv(f_in_path,f_out_name):
    df = pd.read_excel(f_in_path,engine='openpyxl')
    os.unlink(f_in_path)
    df.drop(index=df.index[0], axis=0, inplace=True)
    df.drop(index=df.index[0], axis=0, inplace=True)
    df.to_csv(f'{INPUT_DIR}{f_out_name}.csv',header=False)
    return f'{INPUT_DIR}{f_out_name}.csv'

# METHOD TO PARSE CSV
def parse_csv(csv_path, ftype):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f)
    ROWS = []
    for row in reader:
        ENTITY_ID = shortuuid.uuid(f'{row["Number"]}{row["RegisteredDate"]}-maldives_kyb_crawler')
        NAME = row['CompanyName'] if 'CompanyName' in row else row['Name']
        BIRTH_INCORPORATION_DATE = [dmy_en_month_to_number(row["RegisteredDate"])]
        DATA = {
                    "name": NAME,
                    "status": row["State"],
                    "registration_number": row["Number"],
                    "registration_date": dmy_en_month_to_number(row["RegisteredDate"]),
                    "dissolution_date": "",
                    "type": row["CompanyType"] if "CompanyType" in row else ftype,
                    "crawler_name": "custom_crawlers.kyb.maldives.maldives_kyb_crawler",
                    "country_name": COUNTRY[0],
                    "company_fetched_data_status": "",
                    "meta_detail": {          
                    },
                    "people_detail": [
                        {
                            "designation": "Managing Director",
                            "name": row["ManagingDirector"].strip().replace('  ',' ').replace('  ',' ')
                        } if "ManagingDirector" in row else None,

                        {
                            'designation': 'Owner',
                            "name":  row["OwnerName"].strip().replace('  ',' ').replace('  ',' ')
                        } if "OwnerName" in row else None,

                        {
                            'designation': 'Managing Partner',
                            'name':  row["ManagingPartner"].strip().replace('  ',' ').replace('  ',' ')
                        } if "ManagingPartner" in row else None
                    ]
                }
        
        DATA['people_detail'] = [p for p in DATA['people_detail'] if p]

        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    f.close()
    return ROWS

# Main execution entry point
for ftype, furl in FILES_URLS.items():
    print('Processing:',ftype, furl)
    fpath = download_file(ftype, furl)
    csv_path = convert_xlsx_to_csv(fpath, ftype)
    data = parse_csv(csv_path,ftype)
    insert_data(data)