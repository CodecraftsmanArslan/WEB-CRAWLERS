import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import requests
import shortuuid
import json
from bs4 import BeautifulSoup

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


# Fetching all sitemaps
BASE_URL = 'https://firmenbuch.at'
SITE_MAP_URL = 'https://firmenbuch.at/Sitemap/'
res = requests.get(SITE_MAP_URL)
soup = BeautifulSoup(res.text, 'lxml')
all_sitemap_links = soup.find_all('a', {'class': 'list-group-item small'})
all_sitemap_links = [atag.get('href') for atag in all_sitemap_links]

# fetch business details 
def fetch_item_details(url):
    res = requests.get(BASE_URL+url)
    print('Processing',BASE_URL+url)
    soup = BeautifulSoup(res.text, 'lxml')
    detail = soup.find(id='detail')
    h2 = detail.find_all('h2')  
    NAME = detail.h1.text.strip().replace('"','')
    ADDRESS = h2[0].text.strip()
    REGISTRATION_NUMBER = h2[1].text.strip().split(' ')[1]
    ENTITY_ID = shortuuid.uuid(f'{REGISTRATION_NUMBER}{ADDRESS}-austria_br_crawler')
    COUNTRY = ['Austria']
    CATEGORY = ['Official Registry']
    ENTITY_TYPE = 'Company/Organization'
    SOURCE_DETAIL = {"Source URL": "https://firmenbuch.at/Sitemap/", 
                    "Source Description": "Official Austrian Business Register, which is maintained by the Austrian Ministry of Justice. The website provides a range of information on businesses registered in Austria, including details on the company name, legal form, registration number, and other relevant information."}
    BIRTH_INCORPORATION_DATE = []
    IMAGES = []
    
    DATA = {
            "name": NAME,
            "status": "",
            "registration_number": REGISTRATION_NUMBER,
            "registration_date": "",
            "dissolution_date": "",
            "type": "",
            "crawler_name": "custom_crawlers.kyb.austria_br_crawler",
            "country_name": COUNTRY[0],
            "meta_detail": {
                "incorporated_in": COUNTRY[0],
            },
            "addresses_detail": [{
                "address": ADDRESS
            }]
        }
    

    ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
        json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
        'Austrian Business Register',json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en', True]
    return ROW

# crawling sitemaps
for a in all_sitemap_links:
    print('Processing',BASE_URL+a)
    res = requests.get(BASE_URL+a)
    soup = BeautifulSoup(res.text, 'lxml')
    page_links = [li.a.get('href') for li in soup.find_all('li',{'class': 'overview-element'})]
    data = [fetch_item_details(item_url) for item_url in page_links]
    insert_data(data)
print('FINISHED')