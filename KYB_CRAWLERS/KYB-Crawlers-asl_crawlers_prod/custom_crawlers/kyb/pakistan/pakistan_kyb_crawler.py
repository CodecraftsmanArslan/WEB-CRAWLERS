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
SOURCE = 'SECP-Corporates'
COUNTRY = ['Pakistan']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://www.secp.gov.pk/data-and-statistics/corporates/", 
                 "Source Description": "SECP is responsible for the development of modern and efficient corporate sector and capital market based on sound regulatory principles."}
IMAGES = []
# METHOD TO PARSE CSV

MERGE_DATA = {}

# read input dir
for fcsv in os.listdir('pakistan/input'):
    print(f'processing {fcsv}')
    reader = csv.DictReader(open(f'pakistan/input/{fcsv}','r'))
    ROWS = []
    for row in reader:
        ALREADY_EXIST = False
        ENTITY_ID = shortuuid.uuid(f"{int(row['CUIN'])}-{row['CRO Name']}-pakistan_kyb_crawler")
        NAME = row['Company Name']
 
        REG_DATE = ''
        if 'Date of Incorporation' in row:
            REG_DATE = row['Date of Incorporation'].replace('/','-')
        elif 'Incorporation Date / Registration Date' in row:
            REG_DATE = row['Incorporation Date / Registration Date'].replace('/','-')
 
        BIRTH_INCORPORATION_DATE = [REG_DATE] if REG_DATE else []
        STATUS = ''
        
        if 'Date of Revocation of Licence' in row and fcsv.find('List-of-revoked-licence') != -1:
            STATUS = 'Licence Revoked'
        elif fcsv.find('List-of-Inactive-Companies') != -1:
            STATUS = 'Inactive'
        else:
            STATUS = ''
        

        if int(row['CUIN']) in MERGE_DATA:
            ALREADY_EXIST = True
        
        DATA = {
                "name": row["Company Name"],
                "status": STATUS,
                "registration_number": str(int(row["CUIN"])),
                "registration_date": REG_DATE,
                "dissolution_date": '',
                "type": row['Company Kind'] if 'Company Kind' in row else '',
                "crawler_name": "custom_crawlers.kyb.pakistan.pakistan_kyb_crawler",
                "country_name": "Pakistan",
                "company_fetched_data_status": "",
                "meta_detail": {
                    'place_registered': row['CRO Name'],
                    **({'date_of_revocation_of_licence': row['Date of Revocation of Licence']} if 'Date of Revocation of Licence' in row else {}),
                    **({'reasons_for_revocation_of_licence': row['Reasons for revocation of Licence']} if 'Reasons for revocation of Licence' in row else {})
                },
                "people_detail": [
                    {
                        'name': row['Auditor Name'] if 'Auditor Name' in row else "",
                        'designation': 'auditor',
                        'appointment_date': row['Auditor Appointment Date'] if 'Auditor Appointment Date' in row else "",
                    } if 'Auditor Name' in row else None
                ]
              }
        
        DATA['people_detail'] = [e for e in DATA['people_detail'] if e]
                
        if ALREADY_EXIST:
            DATA['meta_detail'] = {**MERGE_DATA[int(row['CUIN'])]['meta_detail'],**DATA['meta_detail']}
        else:
            MERGE_DATA[int(row['CUIN'])] = DATA
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        
        ROWS.append(ROW)
    insert_data(ROWS)
print('FINISHED')