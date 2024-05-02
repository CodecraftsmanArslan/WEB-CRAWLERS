import tabula
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv

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
SOURCE = 'Securities and Exchange Commission (SEC) in the Philippines'
COUNTRY = ['Philippines']
CATEGORY = ['Company/SIE']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://www.sec.gov.ph/registered-firms-individuals-and-statistics/registered-firms-and-individuals/#gsc.tab=0", 
                 "Source Description": "Official directory of registered firms and individuals provided by the Securities and Exchange Commission (SEC) in the Philippines.The directory includes information such as the registered firm's name, address, and contact information, as well as the type of securities license held."}
IMAGES = []
# METHOD TO PARSE CSV

# read input dir for csvs and parse them
for fcsv in os.listdir('philippines/input'):
    print(f'processing {fcsv}')
    reader = csv.DictReader(open(f'philippines/input/{fcsv}','r',encoding='cp1252'))
    ROWS = []
    for row in reader:
        print(row)
        NAME = row['COMPANY NAME'] if 'COMPANY NAME' in row else ''
        ENTITY_ID = shortuuid.uuid(NAME)
        REG_DATE = row['DATE OF PERMIT TO SELL'] if 'DATE OF PERMIT TO SELL' in row else ''
        BIRTH_INCORPORATION_DATE = [REG_DATE] if REG_DATE else []
        DATA = {
                "name": NAME,
                "status": row['STATUS'] if 'STATUS' in row else '',
                "registration_number": '',
                "registration_date": '',
                "dissolution_date": '',
                "type": row['CLASSIFICATION'] if 'CLASSIFICATION' in row else '',
                "crawler_name": "custom_crawlers.kyb.philippines.philippines_kyb_csv",
                "country_name": COUNTRY[0],
                "company_fetched_data_status": "",
                "meta_detail": {
                }
              }
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    insert_data(ROWS)
print('FINISHED')