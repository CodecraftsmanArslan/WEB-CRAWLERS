import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
from bs4 import BeautifulSoup
import csv
from io import StringIO

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
        cursor.execute(query)
        conn.commit()
        print('INSERTED RECORD')



SOURCE = 'Official Data Platform, Government of Romania'
COUNTRY = ['Romania']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.gov.ro/dataset/firme-inregistrate-la-registrul-comertului-pana-la-data-de-07-ianuarie-2023", 
                 "Source Description": "The data.gov.ro portal was created in 2013 as part of international open data efforts, with the aim of centralizing open data published by Romanian institutions according to the principles and standards in the field. The dataset on this page contains information on the companies registered in Romania up to January 7, 2023. The dataset includes various details about the registered companies such as their name, address, registration date, and other related information."}
BIRTH_INCORPORATION_DATE = []
IMAGES = []


STATUSES_MAP = json.load(open('romania/mapping/mapping.json'))

def get_status_value(status_code):
    try:
        value = STATUSES_MAP[status_code]
        return value
    except KeyError:
        return f'No mapping found for {status_code}.'
    
def parse_csv(csv_str):
    reader = csv.DictReader(StringIO(csv_str),delimiter='^')
    ROWS = []
    for row in reader:
        license_number = row['COD_INMATRICULARE']
        ENTITY_ID = shortuuid.uuid(f'{license_number}-{row["CUI"]}-romania_kyb_crawler')
        NAME = row['DENUMIRE']
        statuses =  row['STARE_FIRMA'].split(',')
        STATUS = get_status_value(statuses[0])
        statuses = statuses[1:]
        DATA = {
                "name": row['DENUMIRE'],
                "status": STATUS,
                "registration_number": row['CUI'],
                "registration_date": "",
                "dissolution_date": "",
                "type": "",
                "crawler_name": "custom_crawlers.kyb.romania_kyb_crawler",
                "company_fetched_data_status": "",
                **({"addresses_detail": [
                    {
                        "type": "general_address",
                        "address": row['ADRESA_COMPLETA'],
                        "description": "",
                        "meta_detail": {
                            **({'country': row['ADR_TARA']}),
                            **({'city': row['ADR_LOCALITATE']}),
                            **({'state': row['ADR_JUDET']}),
                            **({'street_name': row['ADR_DEN_STRADA']}),
                            **({'street_number': row['ADR_DEN_NR_STRADA']}),
                            **({'block': row['ADR_BLOC']}),
                            **({'stair_case': row['ADR_SCARA']}),
                            **({'floor': row['ADR_ETAJ']}),
                            **({'apartment': row['ADR_APARTAMENT']}),
                            **({'postal_code': row['ADR_COD_POSTAL']}),
                            **({'district': row['ADR_SECTOR']})
                        }
                    },
                ]} if 'ADRESA_COMPLETA' in row else {}),
                **({"additional_detail": [
                                        {
                                            "type": "firm_statuses",
                                            "data": [{'firm_status': get_status_value(e), 'status_code': e} for e in statuses if e]
                                        }
                ]} if len(statuses)>0 else {}),
                "meta_detail": {
                    "european_registration_number": row['EUID'],
                    **({"license_number": row['COD_INMATRICULARE']}),
                }
            }
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS

URL = 'https://data.gov.ro/dataset/firme-inregistrate-la-registrul-comertului-pana-la-data-de-07-ianuarie-2023'
res = requests.get(URL)
soup = BeautifulSoup(res.text, 'lxml')
script = soup.find('script', {'type': 'application/ld+json'})
script = json.loads(script.text)
CSV_FILES =  [g['schema:url'] for g in script['@graph'] if g['schema:name'].find('.csv') != -1]
for cfile in CSV_FILES:
    if cfile.find('nomenclator_stari_firma.csv') !=-1:
        continue
    print('Downloading csv', cfile)
    res = requests.get(cfile)
    content = res.content
    try:
        content = content.decode('cp1252')
    except UnicodeDecodeError:
        try:
            content = content.decode('latin-1')
        except:
            try:
                content = content.decode('utf-8')
            except:
                try:
                    content = content.decode('utf-16-le')
                except:
                    content = content.decode('utf-32-le')
    ROWS = parse_csv(content)
    insert_data(ROWS)
print('FINISHED')