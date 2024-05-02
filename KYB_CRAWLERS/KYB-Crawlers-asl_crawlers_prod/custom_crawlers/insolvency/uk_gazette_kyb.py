from base64 import encode
import pandas as pd
import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
from bs4 import BeautifulSoup
from time import sleep

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
BASE_URL = 'https://www.thegazette.co.uk'

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
SOURCE = "The Gazette"
COUNTRY = ["United Kingdom"]
CATEGORY = ["Bankruptcy/Insolvency/Liquidation"]
ENTITY_TYPE = "Company/Person"
SOURCE_DETAIL = {"Source URL": "https://www.thegazette.co.uk/insolvency", 
                 "Source Description": "The Gazette is the official public record of the United Kingdom government. The Gazette provides a range of services to individuals and businesses, such as company formation, probate and estate administration, and legal publishing. Given link is of list of notices given to person/company regarding insolvency/bankcruptcy."}
IMAGES = []


def crawl_details(urls):
    ROWS = []
    for url in urls:
        print('Processing ',f'{BASE_URL}{url}')
        notice_el = None
        retry_count = -1
        while notice_el is None:
            try:
                res = requests.get(f'{BASE_URL}{url}', headers=headers, proxies={
                                "http": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
                                "https": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
                                }, verify=False)
                soup = BeautifulSoup(res.text, 'lxml')
                notice_el = soup.find('div', {'class':'full-notice'})
            except:
                if retry_count>7:
                    break
                retry_count +=1
                print('Element not found, retrying.')
                sleep(3)

        # header = notice_el.find('header').text if notice_el.find('header') is not None else None
        content_el = notice_el.find('div', {'class':'content'})
        name_el = content_el.find('h5')
        NAME = name_el.text.strip() if name_el is not None else None
        DESCRIPTION = content_el.text.strip()
        meta_data_el = soup.find('dl', {'class':'metadata'})
        dts = meta_data_el.find_all('dt')
        dds = meta_data_el.find_all('dd')

        if NAME is None:
            NAME = notice_el.find('', {'property': 'gazorg:name'}).text if notice_el.find('', {'property': 'gazorg:name'}) is not None else ''

        NAME = NAME.strip()
        DAT = {}
        for i,dt in enumerate(dts):
            DAT[dts[i].text.strip().replace(':','')] =  dds[i].text.strip()
        
        if 'Company number' in DAT:
            DAT['Company number'] = DAT['Company number'].replace('Notice timeline for company number', '').strip()

        ID = DAT['Notice ID']
        # BIRTH_INCORPORATION_DATE = [row["Fecha de actuacion (1era firma)"]]
        ENTITY_ID = shortuuid.uuid(f'${NAME}-{ID}-{url}')
        DATA = {
                    "name": NAME,
                    "status": '',
                    "registration_number": DAT['Company number'] if 'Company number' in DAT else '',
                    "registration_date": '',
                    "dissolution_date": "",
                    "type": '',
                    "crawler_name": "custom_crawlers.insolvency.uk_gazette",
                    "country_name": COUNTRY[0],
                    "company_fetched_data_status": "",
                    "addresses_detail": [ 
                    ],
                    "meta_detail": {
                        'source_url': f'{BASE_URL}{url}',
                        'type': DAT['Type'],
                        'description': DESCRIPTION,
                        'publication_name': DAT['Edition'],
                        **({'publication_date': DAT['Publication date']} if 'Publication date' in DAT else {}),
                        **({'publication_date': DAT['Earliest publish date']} if 'Earliest publish date' in DAT else {}),
                        'notice_type': DAT['Notice type'],
                        'notice_code': DAT['Notice code'],
                        'notice_id': DAT['Notice ID']
                    }
                }
        BIRTH_INCORPORATION_DATE = ''

        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS



# data = crawl_details(['/notice/4317616'])

# Main execution entry point
MAIN_URL = 'https://www.thegazette.co.uk/insolvency/notice?text=&insolvency_corporate=G205010000&categorycode=-2&location-postcode-1=&location-distance-1=1&location-local-authority-1=&numberOfLocationSearches=1&start-publish-date=&end-publish-date=&edition=&london-issue=&edinburgh-issue=&belfast-issue=&sort-by=&results-page-size=100&results-page={}'
print('Processing ', MAIN_URL.format(1))

res = requests.get(
    MAIN_URL.format(1), headers=headers, proxies={
        "http": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
        "https": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
    }, verify=False)

if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'lxml')
    res_div = soup.find('div', id='search-results')
    search_result = res_div.find_all('article')
    next_el = soup.find('li', {'class':'next'})
    next_page_url = next_el.find('a').get('href')
    detail_page_urls = [res.find('a').get('href') for res in search_result]
    data = crawl_details(detail_page_urls)
    insert_data(data)
    while(next_page_url):
        print('Processing ', next_page_url)
        res = requests.get(next_page_url, headers=headers, proxies={
        "http": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
        "https": "http://44f6d73f85da47dea6cefe15706e51c8:@proxy.crawlera.com:8011/",
    }, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            res_div = soup.find('div', id='search-results')
            search_result = res_div.find_all('article')
            next_el = soup.find('li', {'class':'next'}) or None
            next_page_url = next_el.find('a').get('href') if next_el and next_el.find('a') is not None else None
            detail_page_urls = [res.find('a').get('href') for res in search_result]
            data = crawl_details(detail_page_urls)
            insert_data(data)
        else:
            print('Invalid response from server ', res.status_code)
else:
    print('Invalid response from server ', res.status_code)
print('FINISHED')