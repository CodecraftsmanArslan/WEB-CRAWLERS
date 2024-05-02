"""Import required Library"""
import csv
import os
import json
import psycopg2
import requests
import shortuuid
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'saudi_arabia/input/'
BASE_URL = 'https://od.data.gov.sa'

# Load environment variables
load_dotenv()
# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
def insert_data(data):
    for row in data:
        query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*row)
        if row[1] !='': 
            cursor.execute(query)
            conn.commit()
            print('INSERTED RECORD')

# Constants
SOURCE = 'Open Data portal, Government of Saudi Arabia'
COUNTRY = ['Saudi Arabia']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://od.data.gov.sa/Data/en/dataset/commercial-registration", 
                 "Source Description": "Official platform provided by the government of Saudi Arabia that offers access to open data related to commercial entities and businesses registered in the country. The platform provides information on commercial entities including name, address, registration date, economic activity, and other details obtained from the Ministry of Commerce."}
IMAGES = []

# method to download file
def download_file(ftype, furl):
    print('Download page', ftype)
    res = requests.get(furl, verify=False)
    if res.status_code != 200:
        return None
    soup = BeautifulSoup(res.text, 'lxml')
    download_link = soup.find('a',{'class':'resource-url-analytics'}).get('href')
    print('Found Download URL', download_link)
    res = requests.get(f'{BASE_URL}{download_link}', headers=headers, verify=False)
    if res.status_code == 200:
        f = open(f'{INPUT_DIR}{ftype}.csv','wb')
        f.write(res.content)
        f.close()
        return f.name
    else: 
        print('Invalid response from server: ', res.status_code)
    return None

# method to convrt xlsx to formatted csv
def convert_xlsx_to_csv(f_in_path,f_out_name):
    print('converting XLSX to CSV')
    df = pd.read_excel(f_in_path,engine='openpyxl')
    os.unlink(f_in_path)
    df.to_csv(f'{INPUT_DIR}{f_out_name}.csv',index=False)
    return f'{INPUT_DIR}{f_out_name}.csv'

# METHOD TO PARSE CSV
def parse_csv(csv_path):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f)
    ROWS = []
    count = 0
    for row in reader:
        NAME = row['Commercial_Name']
        eng_name = row['Commercial_Name']
        BIRTH_INCORPORATION_DATE = [row["CR_Issue_Date_GR"].replace('/','-')] if row['CR_Issue_Date_GR'] != " " else []
        ENTITY_ID = shortuuid.uuid(f'{row["CR_Number"]}-{row["CR_Issue_Date_GR"]}-saudi_arabia_kyb_crawler')
        DATA = {
                    "name": eng_name,
                    "status": '',
                    "registration_number": row["CR_Number"],
                    "registration_date": row["CR_Issue_Date_GR"].replace('/','-'),
                    "dissolution_date": "",
                    "type": row["CR_Legal_Structure"] if "CR_Legal_Structure" in row else '',
                    "crawler_name": "custom_crawlers.kyb.saudi_arabia.saudi_arabia_kyb_crawler",
                    "country_name": COUNTRY[0],
                    "company_fetched_data_status": "",
                    "addresses_detail": [
                        {
                            "type": "business_address",
                            "address": f"{row['CR_Type']}, {row['CR_Region_Name_EN']}, {row['CR_Region_Name_AR']}",
                            "description": "",
                            "meta_detail": {
                                "region": row['CR_Region_Name_EN'],
                                "country": COUNTRY[0],
                            }
                        },
                    ],
                    "meta_detail": {
                       "main_company_registration_number": row["Main_CR_Number"].strip().replace('.0','') if row["Main_CR_Number"].strip() != '' else '',
                       "aliases": row['Commercial_Name'],
                       "branch_type": row["CR_Type"]
                    }

                }
        ROW = [ENTITY_ID, eng_name.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
        if len(ROWS) == 50:
            insert_data(ROWS)
            ROWS = []
    insert_data(ROWS)
    f.close()
    return ROWS

# Main execution entry point

MAIN_URL = 'https://od.data.gov.sa/Data/en/dataset/commercial-registration'

res = requests.get(MAIN_URL, verify=False)
soup = BeautifulSoup(res.text, 'lxml')
table = soup.find('table',id='tblResources')
resource_items = table.find_all('tr',{'class':'resource-item'})

for ritem in resource_items:
    if ritem.a.span.get('data-format') == 'csv':
        fname = ritem.a(text=True, recursive=False)[1].strip()
        csv_path = download_file(fname, f"{BASE_URL}{ritem.a.get('href')}")
        parse_csv(csv_path)
