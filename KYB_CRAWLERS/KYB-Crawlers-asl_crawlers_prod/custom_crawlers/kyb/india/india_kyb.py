import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import pandas as pd
import requests, time
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os, re
import psycopg2
import json
import csv
import sys
from io import BytesIO
import gdown
from helper_functions import dmy_en_month_to_number
sys.path.append('../kyb')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
INPUT_DIR = 'input/'
# ZIP file url
SOURCE_URL = "https://data.gov.in/catalog/company-master-data"
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

# Constants
SOURCE = 'Open Government Data(OGD) Platform India'
COUNTRY = ['India']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.gov.in/catalog/company-master-data", 
                 "Source Description": "Open data portal maintained by the Government of India, and specifically focused on providing access to master data related to companies registered in India. The website provides a variety of datasets related to different aspects of company registration and operation in India, including information on the companies themselves, their legal status, and their financial performance."}
IMAGES = []

# method to download file
def download_file(url, filename):
    print('Downloading file')
    try:
        df = pd.read_csv(url, encoding='ISO-8859-1')
        df.to_csv(filename, index=False, encoding='ISO-8859-1') 
    except:
        time.sleep(10)
        response = requests.get(url)
        STATUS_CODE = response.status_code 
        gdown.download(url, filename, quiet=False) 
    print('DOWNLOADED')
    return None

# METHOD TO PARSE CSV
def parse_csv(csv_path):
    f = open(csv_path, encoding='ISO-8859-1', mode='r')
    reader = csv.DictReader(f)

    ROWS = []
    for row in reader:
        print(row)
        ENTITY_ID = shortuuid.uuid(f"{row['CORPORATE_IDENTIFICATION_NUMBER']}-{row['CORPORATE_IDENTIFICATION_NUMBER']}-india_kyb_crawler")
        NAME = row['Company_Name']
        BIRTH_INCORPORATION_DATE = [row["DATE_OF_REGISTRATION"]]
        additional_detail = []
        addresses_detail = []
        additional_detail.append({
            "type": "capital_information",
            "data": [{
                "capital": row['AUTHORIZED_CAP'] if 'AUTHORIZED_CAPITAL' in row else row['AUTHORIZED_CAP'],
                "paid_up_capital": row['PAIDUP_CAPITAL']
            }]
        })
        additional_detail.append({
            "type": "category_information",
            "data": [{
                "nature_of_control": row['COMPANY_CATEGORY'] if 'COMPANY_CATEGORY' in row else (row["Company_Category"] if 'Company_Category' in row else ""),
                "sub_category": row['Sub_Category']  if 'SUB_CATEGORY' in row else "",
                "company_sub_category": row['Company_sub_category'] if 'Company_sub_category' in row else ""
            }]
        })
        if row['Registered_Office_Address'] is not None and row['Registered_Office_Address'] != "Null" and row['Registered_Office_Address'] != "":
            addresses_detail.append({
                "type": "registered_office_address",
                "address": row['Registered_Office_Address'].replace("Null", "").replace("Unclassified", "") if row['Registered_Office_Address'] is not None else ""
            })
        meta_detail = {
            "industry_code": row['Industrial_Class'] if 'Industrial_Class' in row else row['INDUSTRIAL_CLASS'],
            "registrar_of_companies": row['REGISTRAR_OF_COMPANIES'],
            "last_year_AR": row['Latest_Year_AR'] if 'Latest_Year_AR' in row else row['LATEST_YEAR_ANNUAL_RETURN'],
            "last_year_BS": row['Latest_Year_BS'],
            "last_year_financial_statement": row['LATEST_YEAR_FINANCIAL_STATEMENT'] if 'LATEST_YEAR_FINANCIAL_STATEMENT' in row else ""
        }
        meta_detail = {key: value for key, value in meta_detail.items() if value != ''}
        DATA = {
                    "name": row['Company_Name'],
                    "status": row['Company_status'],
                    "registration_number": row['CORPORATE_IDENTIFICATION_NUMBER'],
                    "registration_date": row["DATE_OF_REGISTRATION"],
                    "type": row['Company_class'],
                    "jurisdiction": row['REGISTERED_STATE'],
                    "crawler_name": "custom_crawlers.kyb.india.india_kyb_crawler",
                    "country_name": "India",
                    "industries": row["PRINCIPAL_BUSINESS_ACTIVITY_AS_PER_CIN"],
                    "additional_detail": additional_detail,
                    "addresses_detail": addresses_detail,
                    "meta_detail": meta_detail,
                    **({"contacts_detail": [
                        {
                            "type": 'email',
                            'value': row['EMAIL_ADDR'],
                        }
                    ]} if 'EMAIL_ADDR' in row and row['EMAIL_ADDR'].strip() !='' else {})
                }
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    f.close()
    return ROWS

# Main execution entry point
if __name__ == '__main__':
    URLs = [
        'https://drive.google.com/file/d/1FOTll2U_I7G0rOwLBwltG29S1lbRYsSU/view?usp=sharing',
        'https://drive.google.com/file/d/1CIFHo3BJ0xBxnWGRRswHkfeubEeCSa1x/view?usp=sharing',
        'https://drive.google.com/file/d/105-O9gssJ0Aokkkpx9bppBNotfZzzqPf/view?usp=sharing',
        'https://drive.google.com/file/d/1-IiRbXoe1_GMUsZNh9-_wYuywepK-M-3/view?usp=sharing',
        'https://drive.google.com/file/d/1EMgOWnxTKmbRdyL8skW758etjewlLwTE/view?usp=sharing',
        'https://drive.google.com/file/d/1v0UxIgG7V5fwEe0pAnX_Cw0gVOEvd3aB/view?usp=sharing',
        'https://drive.google.com/file/d/1ygDWAh0flRYc84_s-RXkMZO7EbtTLTvH/view?usp=sharing',
        'https://drive.google.com/file/d/1Ubws1p_8tNEj__ltqrU4f7LTWFN3YGyj/view?usp=sharing',
        'https://drive.google.com/file/d/1Fsi-Rj8LSaJ2jZ5auANxaG30xJc6WIVb/view?usp=sharing',
        'https://drive.google.com/file/d/195Dk6cASE9EzBxJAN9fv5O82dSGnx2dt/view?usp=sharing',
        'https://drive.google.com/file/d/1_oZbzfhUmPlR9-90kxixL_fEuAki4Fi0/view?usp=sharing',
        'https://drive.google.com/file/d/1FYcjhKDvHjkg_xSzT5VxirNS-rBwogmP/view?usp=sharing',
        'https://drive.google.com/file/d/1AiLYnw-z1TPQvtbygufImdZPthl5LjpP/view?usp=sharing',
        'https://drive.google.com/file/d/1Fy72r5sspXnxh6nwTob_hF533wvXD2OH/view?usp=sharing',
        'https://drive.google.com/file/d/1Wv9gcbapqd08xrB-BbyJG5_Wz1FXDG8c/view?usp=sharing',
        'https://drive.google.com/file/d/1PahrsouFc7bhmplHSTYF57i1Yp2-09Gm/view?usp=sharing',
        'https://drive.google.com/file/d/1WPFaWc-W3cSBU1e7VNAt3D0FDx-qrr-Y/view?usp=sharing',
        'https://drive.google.com/file/d/1vz3bI-GCaGbeADkfHB7Z1P8aKTTeJHQ8/view?usp=sharing',
        'https://drive.google.com/file/d/1dsbC3JFDFg_UMoX0GODgP5a0PZH-lRRw/view?usp=sharing',
        'https://drive.google.com/file/d/1j7cjO3V20lvIltcvoS1RR99InHG3huom/view?usp=sharing',
        'https://drive.google.com/file/d/1wKMsgFlg1wZb8CXrasglg5jOeAW3WXa6/view?usp=sharing',
        'https://drive.google.com/file/d/1QFcnaQ5bkgjExzfpVFv_9GDu5bABp4Uv/view?usp=sharing',
        'https://drive.google.com/file/d/1DBsk6_n16LlZoZL1QeRJOKpUUKh7ut85/view?usp=sharing',
        'https://drive.google.com/file/d/1F1CiBMR5_SRjeL0ZJwGlHRkF49jKxNUG/view?usp=sharing',
        'https://drive.google.com/file/d/1AIJ22FCb4PIiAEdcDItpdxSTptVRkUD7/view?usp=sharing',
        'https://drive.google.com/file/d/1VKchs226Cf5TH4lmEW-v09vtmPgTro0b/view?usp=sharing',
        'https://drive.google.com/file/d/1FtBJzIMxW8q2SvPjsYfIHwqfEFAjjUeN/view?usp=sharing',
        'https://drive.google.com/file/d/1JNvdqNETEIA3x3kJB2vB2TURyCBMK7Qp/view?usp=sharing',
        'https://drive.google.com/file/d/17de3rr-4DK-BKzEFNj8oiyY5-aJV-he1/view?usp=sharing',
        'https://drive.google.com/file/d/1QvjgM6lS05SvMFYgm5mrKtFnUz1VJKpz/view?usp=share_link',
        'https://drive.google.com/file/d/19j49Ry-CyWHOi8cdAPR1p_LyqLbszRxF/view?usp=share_link',
        'https://drive.google.com/file/d/1HH3bzhkXHzR5ZSsYL0iXey_BgIqrJ092/view?usp=share_link',
        'https://drive.google.com/file/d/1OzxoapP4L6fYoNIyBCd-RN9-WLGKBT_i/view?usp=sharing',
        'https://drive.google.com/file/d/1tS7g52yZCOkxlTtsu1_mBQWVywruzJri/view?usp=share_link',
        'https://drive.google.com/file/d/1gUmNRhpH167EiQjMk_7XdN3xYfSeAE9N/view?usp=share_link',
        'https://drive.google.com/file/d/1oLIrfAhxg3hqp6tvCbT8mXiLMyFJpqMd/view?usp=share_link',
        'https://drive.google.com/file/d/1E44-7dFGWK_Av5xPIgHPNrLxe3fzsAxC/view?usp=share_link'
    ]

    print('PROCESSING:')
    prefix_url = 'https://drive.google.com/uc?/export=download&id={}&confirm=t'
    filename = 'input/file.csv'
    for url in URLs:
        file_id = url.split('/')[-2]
        download_url = prefix_url.format(file_id)
        print(download_url)
        fpath = download_file(download_url, filename)
        data = parse_csv(filename)
        insert_data(data)
        print('RECORDS INSERTED')
    
    os.remove(filename)
    print('FILE DELETED')
    
