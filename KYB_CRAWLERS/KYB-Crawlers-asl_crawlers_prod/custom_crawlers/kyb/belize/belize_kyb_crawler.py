import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
from nodejs import node, npm

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'belize/input/'

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
SOURCE = 'Belize Companies & Corporate Affairs Registry'
COUNTRY = ['Belize']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://obrs.bccar.bz/bereg/searchbusinesspublic", 
                 "Source Description": "Official website of Belize Companies and Corporate Affairs Registry (BCCAR). The BCCAR is the main government agency responsible for the registration and regulation of businesses and corporations in Belize. The search tool allows members of the public to search for information about registered businesses and corporations, including the name and status of the entity, as well as any documents that have been filed with the registry."}
IMAGES = []

# METHOD TO PARSE CSV
def parse_csv(csv_path):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f)
    ROWS = []
    for row in reader:
        NAME = row['name']
        BIRTH_INCORPORATION_DATE = [row["reg_date"]]
        ENTITY_ID = shortuuid.uuid(f"{row['reg_number']}-belize_kyb_crawler")
        BUSINESS_ENTITY_TYPE_STR = row["business_entity_type_str"] if  row["business_entity_type_str"] != 'null' else ""
        BUSINESS_ENTITY_SUBTYPE = row["business_entity_subtype"] if row["business_entity_subtype"] != 'null' else ""
        addresses_detail = []
        meta_detail = {
            "aliases": row["foreign_name"].replace("null", "") if row["foreign_name"] is not None else ""
        }
        if row['reg_address'] is not None and row['reg_address'] != "":
            addresses_detail.append({
                "type": "general_address",
                "address": row['reg_address']
            })
        meta_detail = {key: value for key, value in meta_detail.items() if value != ''}
        DATA = {
                "name": NAME,
                "status": row["state"],
                "registration_number": row["reg_number"],
                "registration_date": row["reg_date"],
                "type": BUSINESS_ENTITY_SUBTYPE,
                "category": BUSINESS_ENTITY_TYPE_STR.strip(),
                "crawler_name": "custom_crawlers.kyb.belize.belize_kyb_crawler",
                "country_name": COUNTRY[0],
                "meta_detail": meta_detail,
                "addresses_detail": addresses_detail
            }
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    f.close()
    return ROWS

# MAIN exe

if os.path.isdir('belize/input/node_modules'):
    code = node.call(['belize/input/index.js'])
else:
    os.chdir('belize/input')
    print('node_modules not found')
    npm.call(['install'])
    os.chdir('../../')
    print(os.curdir)
    code = node.call(['belize/input/index.js'])
data = parse_csv(f'{INPUT_DIR}belize-data.csv')
insert_data(data)
print('FINISHED')
