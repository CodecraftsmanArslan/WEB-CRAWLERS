import requests
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import requests
import shortuuid
import json

URLS = {
    'Finance': 'https://www.mass.gov/doc/financialtxt/download',
    'Corporation': 'https://www.mass.gov/doc/corporationstxt/download',
    'Insurance': 'https://www.mass.gov/doc/insurancetxt/download'
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


def download_and_parse(url):
    res = requests.get(url)
    content = res.content
    lines = content.split(b'\r\n')
    REGISTRATION_NUMBER = ''
    SOURCE = 'Official Website of the Government of Massachusetts'
    COUNTRY = ['Massachusetts']
    CATEGORY = ['Official Registry']
    ENTITY_TYPE = 'Company/Organization'
    SOURCE_DETAIL = {"Source URL": "https://www.mass.gov/doc/corporationstxt/download", 
                    "Source Description": "The dataset contains information on domestic and foreign corporations and limited liability companies (LLCs) registered with the Massachusetts Secretary of State's Office, including the entity name, identification number, date of incorporation, and principal office address."}
    BIRTH_INCORPORATION_DATE = []
    IMAGES = []
    ROWS = []
    for line in lines:
        try:
            line = line.decode()
        except UnicodeDecodeError:
            line = line.decode('cp1252')
        
        if line:
            [*name, city_or_state] = line.strip().split(',')
            name  = ', '.join(name)
            
        NAME = name
        ADDRESS = city_or_state.strip()
        ENTITY_ID = shortuuid.uuid(f'{NAME}-{ADDRESS}-massachusetts_gov_crawler')
        DATA = {
                "name": NAME,
                "status": "",
                "registration_number": "",
                "registration_date": "",
                "dissolution_date": "",
                "type": "",
                "crawler_name": "custom_crawlers.kyb.massachusetts_gov_crawler",
                "country_name": COUNTRY[0],
                "company_fetched_data_status": "",
                "meta_detail": {
                    "state_city": ADDRESS,
                }
            }

        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
        json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
        SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS

for cat, url in URLS.items():
    print(cat, url)
    data = download_and_parse(url)
    insert_data(data)

print('FINISHED')
