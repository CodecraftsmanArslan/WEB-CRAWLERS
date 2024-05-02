from base64 import encode
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
from bs4 import BeautifulSoup
sys.path.append('../kyb')
# from helper_functions import dmy_en_month_to_number

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'custom_crawlers/kyb/chile/input/'
BASE_URL = 'https://datos.gob.cl/km/dataset/registro-de-empresas-y-sociedades'

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
        # print('INSERTED RECORD')


# Constants
SOURCE = 'Open Data portal, Government of Chile'
COUNTRY = ['Chile']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://datos.gob.cl/km/dataset/registro-de-empresas-y-sociedades",
                 "Source Description": "Open Data portal of the Government of Chile, and is specifically focused on providing access to data related to businesses and companies registered in Chile. The website provides a variety of datasets related to different aspects of business registration and operation in Chile, including information on the companies themselves, their legal status, and their financial performance."}
IMAGES = []

# method to download file
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

# method to download file


def download_file(ftype, furl):
    print('Downloading file ', furl)
    res = requests.get(f'{furl}')
    if res.status_code == 200:
        file_path = os.path.join(INPUT_DIR, f'{ftype}.csv')
        with open(file_path, 'wb') as f:
            f.write(res.content)
        return file_path
    else:
        print('Invalid response from server: ', res.status_code)
    return None


# METHOD TO PARSE CSV
def parse_csv(csv_path):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f, delimiter=';')
    ROWS = []
    for row in reader:
        ID = row['\ufeffID']
        NAME = row['Razon Social']
        BIRTH_INCORPORATION_DATE = [row["Fecha de actuacion (1era firma)"]]
        ENTITY_ID = shortuuid.uuid(
            f'{ID}-{BIRTH_INCORPORATION_DATE[0]}-chile_kyb')
        DATA = {
            "name": NAME,
            "status": '',
            "registration_number": ID,
            "registration_date": BIRTH_INCORPORATION_DATE[0],
            "dissolution_date": "",
            "type": '',
                    "crawler_name": "custom_crawlers.kyb.chile.chile_kyb",
                    "country_name": COUNTRY[0],
                    "company_fetched_data_status": "",
                    "addresses_detail": [
                        {
                            "type": "business_address",
                            "address": f"{row['Comuna Social']}, {row['Region Social']}",
                            "description": "",
                            "meta_detail": {
                                # "city": row['CR_Region_Name_EN'],
                                "country": COUNTRY[0],
                            }
                        },
                        {
                            "type": "tax_address",
                            "address": f"{row['Comuna Tributaria']}, {row['Region Tributaria']}",
                            "description": "",
                            "meta_detail": {
                                # "city": row['CR_Region_Name_EN'],
                                "country": COUNTRY[0],
                            }
                        },
            ],
            "meta_detail": {
                        **({"tax_id_number": row["RUT"].strip()} if row["RUT"].strip() != '' else {}),
                        **({"trade_code": row["Codigo de sociedad"].strip()} if row["Codigo de sociedad"].strip() != '' else {}),
                        **({"capital": row["Capital"].strip()} if row["Capital"].strip() != '' else {}),
                        **({"governing_law": row["Tipo de actuacion"].strip()} if row["Tipo de actuacion"].strip() != '' else {}),
                        **({"approval_date": row["Fecha de aprobacion x SII"].strip()} if row["Fecha de aprobacion x SII"].strip() != '' else {}),
                        **({"approval_month": row["Mes"].strip()} if row["Mes"].strip() != '' else {}),
                        **({"approval_year": row["Anio"].strip()} if row["Anio"].strip() != '' else {}),
                        **({"last_registration_date": row["Fecha de registro (ultima firma)"].strip()} if row["Fecha de registro (ultima firma)"].strip() != '' else {}),

            }

        }
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE),
               json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(
                   IMAGES), json.dumps(DATA).replace("'", "''"),
               SOURCE, json.dumps(SOURCE_DETAIL).replace(
                   "'", "''"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'en', True]
        ROWS.append(ROW)

    f.close()
    return ROWS


# Main execution entry point
MAIN_URL = 'https://datos.gob.cl/km/dataset/registro-de-empresas-y-sociedades'
res = requests.get(MAIN_URL)
if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'lxml')
    lis = soup.find_all('li', {'class': 'media'})
    for li in lis:
        fname = li.a.h4.text.strip()
        dl_link = li.find('a', {'title': 'Download'}).get('href')
        csv_path = download_file(fname, f"{dl_link}")
        data = parse_csv(csv_path)
        insert_data(data)
else:
    print('Invalid response from server ', res.status_code)
