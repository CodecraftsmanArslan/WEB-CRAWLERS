import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import csv
# import dl_files

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
SOURCE = "Connecticut's Official State Website"
COUNTRY = ['Connecticut']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://drive.google.com/drive/folders/1IdDroORBVaKhbD-p1pPJphCoZvikYrKJ", 
                 "Source Description": "This website provides information on datasets available from the state of Connecticut related to business entities. The webpage includes descriptions and links to datasets in areas such as business entity data, demographics, economic indicators, and more. The datasets can be useful for businesses, researchers, and individuals interested in analyzing and understanding the business environment in Connecticut."}
IMAGES = []
INPUT_DIR = 'connecticut/input'
NAICS_DICT = json.load(open('connecticut/mapping/naics-codes.json'))

def get_naics_value(naic_sub_code):
    if naic_sub_code !='':
        naic_sub_code = str(int(float(naic_sub_code)))
        if naic_sub_code in NAICS_DICT:
            return NAICS_DICT[f'{naic_sub_code}']
        else:
            return ""
    return ""

# METHOD TO PARSE CSV
def parse_csv(fpath):
    print(f'processing {fpath}')
    reader = csv.DictReader(open(fpath,'r'))
    ROWS = []
    for row in reader:
        NAME = row['name']
        ENTITY_ID = shortuuid.uuid(f"{row['date_registration']}-{row['accountnumber']}-connecticut_kyb_crawler")
        BIRTH_INCORPORATION_DATE = [row["create_dt"]] if "create_dt" in row else []
        DATA = {
                    "name": row["name"],
                    "status": row["status"],
                    "registration_number": row["accountnumber"],
                    "registration_date": row["date_registration"],
                    "dissolution_date": row["dissolution_date"],
                    "incorporation_date": row["create_dt"],
                    "type": row["business_type"],
                    "crawler_name": "custom_crawlers.kyb.connecticut.connecticut_kyb_crawler",
                    "country_name": "Connecticut",
                    "company_fetched_data_status": "",
                    "additional_detail": [
                        {
                        "type": "naics_code",
                        "data": [
                                { "naics_code": row['naics_code'] if 'naics_code' in row else "", "naics_sub_code": get_naics_value(row["naics_sub_code"]) if 'naics_sub_code' in row else ""}
                             ]
                        }
                    ] if row['naics_code'] else [],
                    "addresses_detail": [
                        {
                        "type": "general_address",
                        "address": row["billingcountry"]+' '+row["billingcity"]+' '+row["billingstate"]+' '+row["billingstreet"]+' '+row["billingpostalcode"],
                        "description": "",
                        "meta_detail": {}
                        },
                           {
                        "type": "principal_office_address",
                        "address":row["office_jurisdiction_address"],
                        "description": "",
                        "meta_detail":
                            {
                            "office_jurisdiction_2": row["office_jurisdiction_2"],
                            "office_jurisdiction": row["office_jurisdiction"],
                            "office_jurisdiction_1": row["office_jurisdiction_1"],
                            "office_jurisdiction_4": row["office_jurisdiction_4"],
                             "office_in_jurisdiction_country": row["office_in_jurisdiction_country"]
                            }
                        } if row["office_jurisdiction_address"].strip() != '' in row else None,
                        {
                        "type": "postal_address",
                        "address": row["mailing_jurisdiction_address"],
                        "description": "",
                        "meta_detail": 
                            {
                            "mailing_jurisdiction_2": row["mailing_jurisdiction_2"],
                            "mailing_jurisdiction": row["mailing_jurisdiction"],
                            "mailing_jurisdiction_1": row["mailing_jurisdiction_1"],
                            "mailing_jurisdiction_4": row["mailing_jurisdiction_4"],
                             "mailing_jurisdiction_country": row["mailing_jurisdiction_country"]
                            }
                        } if row["mailing_jurisdiction_address"].strip() != '' in row else None,
                    ],
                    "meta_detail": {
                        "annual_report_due_date": row["annual_report_due_date"],
                        "citizenship": row["citizenship"],
                        "organization_owned_by_woman": row["woman_owned_organization"],
                        "organization_owned_by_veteran": row["veteran_owned_organization"],
                        "organization_owned_by_minority": row["minority_owned_organization"],
                        "organization_owned_by_lgbtqi": row["organization_is_lgbtqi_owned"],
                        "nature_of_control": row["total_authorized_shares"],
                        **({"survey_email_address": row["category_survey_email_address"]} if "category_survey_email_address" in row else {}),
                        "billing_unit": row["billing_unit"],
                        "organization_meeting_date": row["date_of_organization_meeting"],
                        "sub_status": row["sub_status"],
                        "began_transacting_connecticut": row["began_transacting_in_ct"],
                        "reason": row["reason_for_administrative"] if "reason_for_administrative" in row else "",
                        "country_of_formation": row["country_formation"]
                        
                    },
                    "contacts_detail": [
                            {
                                "type": "email",
                                "value": row["business_email_address"]
                            }
                    ]
                }
        DATA['addresses_detail'] = [e for e in DATA['addresses_detail'] if e ]
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE.replace("'", "''"),json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS

for fdir in os.listdir(INPUT_DIR):
    if fdir == '.DS_Store':
        continue
    for fcsv in os.listdir(f'{INPUT_DIR}/{fdir}'):
        if fcsv == '.DS_Store':
            continue
        fpath = f'{INPUT_DIR}/{fdir}/{fcsv}'
        data = parse_csv(fpath)
        insert_data(data)