import requests
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import requests
import shortuuid
import json
import math

URL = 'https://www.shab.ch/api/v1/archive/public?includeContent=false&pageRequest.page={}&pageRequest.size=500&tenant=shab'
type_url = 'https://www.shab.ch/api/v1/tenants/shab/archive-rubrics'
# Load environment variables
load_dotenv()

def get_paged_url(i):
    return URL.format(i)

type_codes = (requests.get(type_url)).json()
# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()

COUNTRY = ['Switzerland']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://www.shab.ch/#!/search/archive",
                 "Source Description": "Official platform of the Swiss Official Gazette of Commerce (SOGC), which provides access to the official registry of Swiss companies and legal entities."}
BIRTH_INCORPORATION_DATE = []
IMAGES = []

# Paging trap handle
EMPTY_COUNT = -1


def get_name_from_json(data,code, subcode):
    for item in data:
        if item['code'] == code:
            if subcode is None:
                return item['name']['en']
            for subitem in item['subRubrics']:
                if subitem['code'] == subcode:
                    return f"{item['name']['en']}/{subitem['name']['en']}"
    return ""

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


def parse_name_address(line):
    [*name, city_or_state] = line.strip().split(',')
    NAME = ', '.join(name)
    ADDRESS = city_or_state.strip()
    return NAME, ADDRESS


def parse_content(content, URL):
    ROWS = []
    for r in content:
        NAME, ADDRESS = parse_name_address(r['title'])
        ID = r['id']
        ENTITY_ID = shortuuid.uuid(f'{ID}{r["title"]}-swiss_sogc_crawler')
        source_url = URL
        DATA = {"name": NAME,
                "status": "",
                "registration_number": "",
                "registration_date": "",
                "dissolution_date": "",
                "type":  "",
                "crawler_name": "custom_crawlers.kyb.switzerland.swiss_sogc_crawler",
                "country_name": COUNTRY[0],
                "company_fetched_data_status": "",
                "meta_detail": {
                    "municipality": ADDRESS,
                },
                "additional_detail": [
                    {
                        "type": get_name_from_json(type_codes,r['heading'],r['subheading']),
                        "data": [
                            {
                                "publication_date": r['publicationTime'],
                                "publication_number": ID,
                                "source_url": source_url,
                            }
                        ]
                    }
                ]
                }

        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE),
               json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(
                   IMAGES), json.dumps(DATA).replace("'", "''"),
               'Swiss Official Gazette of Commerce (SOGC)', json.dumps(SOURCE_DETAIL).replace(
                   "'", "''"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'en', True]
        ROWS.append(ROW)
    insert_data(ROWS)


# Get basic page
res = requests.get(get_paged_url(1))
data = res.json()
last_page_index = math.ceil(data['total']/500)
content = data['content']
parse_content(content, get_paged_url(1))

for i in range(2, last_page_index+1):
    print(get_paged_url(i))
    res = requests.get(get_paged_url(i))
    data = res.json()
    content = data['content']
    if len(content) == 0:
        if EMPTY_COUNT > 5:
            break
        EMPTY_COUNT += 1
    parse_content(content, get_paged_url(i))
