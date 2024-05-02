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
INPUT_DIR = 'ecuador/input/'
# Xlsx files urls
FILES_URLS = {
    'directorio_companias':'https://mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx'
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
SOURCE = 'Superintendencia de Compañías, Valores y Seguros (Superintendency of Companies, Securities and Insurance)'
COUNTRY = ['Ecuador']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf", 
                 "Source Description": "Official directory of companies registered in Ecuador. The directory is maintained by the Superintendencia de Compañías, Valores y Seguros (Superintendency of Companies, Securities and Insurance), which is a government agency responsible for overseeing and regulating the financial sector in Ecuador. The directory includes a list of registered companies and businesses operating in Ecuador, as well as their contact information and financial statements."}
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
    df.drop(index=df.index[0], axis=0, inplace=True)
    df.to_csv(f'{INPUT_DIR}{f_out_name}.csv',header=False, index=False)
    return f'{INPUT_DIR}{f_out_name}.csv'

# METHOD TO PARSE CSV
def parse_csv(csv_path, ftype):
    f = open(csv_path, 'r')
    reader = csv.DictReader(f)
    ROWS = []
    for row in reader:
        NAME =  row["NOMBRE"]
        RUC = row["RUC"]
        ENTITY_ID = shortuuid.uuid(f'{RUC}-{NAME}-{row["FECHA_CONSTITUCION"]}-crawlers.kyb.ecuador.ecuador_kyb')
        BIRTH_INCORPORATION_DATE = [row["FECHA_CONSTITUCION"].replace('/', '-')]
        people_detail = [
                        {
                            "name": row["REPRESENTANTE"],
                            "designation": row["CARGO"]
                        } if row["REPRESENTANTE"] != "" else None
                    ]
        people_detail =  [ c for c in people_detail if c ]       
        
        DATA = {
                    "name": NAME,
                    "status": row["SITUACIÓN LEGAL"],
                    "registration_number": RUC,
                    "registration_date": row["FECHA_CONSTITUCION"].replace("/", "-"),
                    "dissolution_date": "",
                    "type": row["TIPO"],
                    "crawler_name": "custom_crawlers.kyb.ecuador.ecuador_kyb",
                    "country_name": "Ecuador",
                    "company_fetched_data_status": "",
                    "additional_detail": [
                        {
                        "type": "trade_codes",
                        "data": [
                            {
                            "trade_code": row["CIIU NIVEL 1"],
                            "trade_code_6": row["CIIU NIVEL 6"]
                            }
                        ]
                        }
                    ],
                    "meta_detail": {
                        "file": row['EXPEDIENTE'],
                        "subscribed_capital": row["CAPITAL SUSCRITO"],
                        "last_year_balance": row["ÚLTIMO BALANCE"]
                    },
                    "contacts_detail":[
                        {
                            "type":"phone_number",
                            "value": row["TELÉFONO"],
                        }
                    ],
                    "addresses_detail": [
                            {
                                "type": "general_address",
                                "address": f'{row["NÚMERO"]}, {row["CALLE"]}, {row["BARRIO"]}, {row["INTERSECCIÓN"]}, {row["CANTÓN"]}, {row["PROVINCIA"]}, {row["REGIÓN"]}, {row["PAÍS"]}',
                                "description": "",
                                "meta_detail": {
                                        "country_of_origin": row["PAÍS"],
                                        "region": row["REGIÓN"],
                                        "province": row["PROVINCIA"],
                                        "canton": row["CANTÓN"],
                                        "cuidad": row["CIUDAD"],
                                        "number": row["NÚMERO"],
                                        "intersection": row["INTERSECCIÓN"],
                                        "barrio": row["BARRIO"],
                                        "street": row['CALLE']
                                }
                            }
                    ],
                    "people_detail": people_detail
                }
        
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
    # fpath = download_file(ftype, furl)
    # csv_path = convert_xlsx_to_csv(fpath, ftype)
    csv_path = 'ecuador/input/directorio_companias.csv'
    data = parse_csv(csv_path,ftype)
    insert_data(data)