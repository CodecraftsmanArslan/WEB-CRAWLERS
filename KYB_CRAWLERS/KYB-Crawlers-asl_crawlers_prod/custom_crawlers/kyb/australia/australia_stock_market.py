import requests
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import math
from time import sleep

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

SOURCE = "Australian Securities Exchange"
COUNTRY = ['Australia']
CATEGORY = ['Stock Market']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://www2.asx.com.au/markets/trade-our-cash-market/directory", 
                 "Source Description": "ASX is an integrated exchange offering listings, trading, clearing, settlement, technical and information services, technology, data and other post-trade services."}

FORMAT = 'HTML'
IMAGES = []


BASE_API_URL = 'https://asx.api.markitdigital.com/asx-research/1.0/companies/directory?page={}&itemsPerPage={}&order=ascending&orderBy=companyName&includeFilterOptions=false&recentListingsOnly=false'
KEY_STATS_API_URL = 'https://asx.api.markitdigital.com/asx-research/1.0/companies/{}/key-statistics'
ABOUT_API_URL = 'https://asx.api.markitdigital.com/asx-research/1.0/companies/{}/about'
PEERS_API_URL = 'https://asx.api.markitdigital.com/asx-research/1.0/companies/{}/peers?height=350&width=480'
ANNOUNCEMENT_API_URL = 'https://asx.api.markitdigital.com/asx-research/1.0/companies/{}/announcements'


def parse_json(data):
    if 'items' in data['data']:
        data = data['data']['items']
        ROWS = []
        for record in data:
            symbol = record['symbol']
            industry = record['industry']
            dateListed = record['dateListed']
           
            url = KEY_STATS_API_URL.format(symbol)
            print('processing ',url)
            key_stats_res = requests.get(url)
            key_stats_json = key_stats_res.json()

            url = ANNOUNCEMENT_API_URL.format(symbol)
            print('processing ',url)
            announcements_res = requests.get(url)
            announcements_json = announcements_res.json()

            url = ABOUT_API_URL.format(symbol)
            print('processing ',url)
            about_res = requests.get(url)
            about_json = about_res.json()

            
            displayName = record['displayName'] if 'displayName' in record else about_json['data']['displayName']

            NAME = displayName
            BusinessId = key_stats_json['data']['isin']
            ENTITY_ID = shortuuid.uuid(f'{symbol}-{NAME}-{BusinessId}')
            FORMATION_DATE = dateListed
            BIRTH_INCORPORATION_DATE = [FORMATION_DATE] if FORMATION_DATE else []

            DATA = {
                    "name": NAME,
                    "status": "",
                    "registration_number": BusinessId,
                    "registration_date": dateListed,
                    "dissolution_date": "",
                    "type": industry,
                    "crawler_name": "custom_crawlers.australia.australia_stock_market",
                    "country_name": "Australia",
                    "company_fetched_data_status": "",
                    "meta_detail": {
                            **({"capital": record['marketCap']} if 'marketCap' in record else {}),
                            "industry_type": record['industry'],
                            "listed_date": dateListed,
                            **({"average_volume": key_stats_json['data']['volumeAverage']} if 'volumeAverage' in key_stats_json['data'] else {}),	
                            "52_week_range": f"${key_stats_json['data']['priceFiftyTwoWeekLow']} - ${key_stats_json['data']['priceFiftyTwoWeekHigh']}",                  
                            "shares_on_issue": key_stats_json['data']['numOfShares'],
                            **({"revenue": key_stats_json['data']['incomeStatement'][0]['revenue']} if 'incomeStatement' in key_stats_json['data'] and len(key_stats_json['data']['incomeStatement'])>0 else {}),
                            **({"net_profit": key_stats_json['data']['incomeStatement'][0]['netIncome']} if 'incomeStatement' in key_stats_json['data'] and len(key_stats_json['data']['incomeStatement'])>0 else {}),
                            **({"cash_flow": key_stats_json['data']['cashFlow']} if 'cashFlow' in key_stats_json['data'] else {}),
                            "announcement_details": [{'announcementType': announcement['announcementType'],'date':announcement['date'],'headline':announcement['headline'], 'isPriceSensitive':announcement['isPriceSensitive'],'document_url': f"https://cdn-api.markitdigital.com/apiman-gateway/ASX/asx-research/1.0/file/{announcement['documentKey']}?access_token=1"} for announcement in announcements_json['data']['items']],
                            "people_details": '',
                            "address": '',
                            "share_registry": '',
                            'source_url': url

                    }, 
                    "addresses_detail": [
                            {
                                "type": "office_address",
                                "address": about_json['data']['addressContact']['address'],
                                "description": "Head office address",
                                "phone": about_json['data']['addressContact']['phone'],
                                "fax": about_json['data']['addressContact']['fax'],
                                "meta_detail": None
                            } if 'addressContact' in about_json['data'] else None,
                            {
                                "type": "address_share_registry",
                                "address": about_json['data']['addressShareRegistry']['address'],
                                "description": "Share registry address",
                                "phone": about_json['data']['addressShareRegistry']['phone'],
                                "attention": about_json['data']['addressShareRegistry']['attention'],
                                "meta_detail": None
                            } if 'addressShareRegistry' in about_json['data'] else None,
                    ],
                    "people_detail": [
                            {
                                "type": "directors",
                                "data": [{"name": director['name'],"title": director['title']} for director in about_json['data']['directors']] if 'directors' in about_json['data'] else []
                            },
                            {
                                "type": "secretaries",
                                "data": [{"name": sec['name'],"title": sec['title']} for sec in about_json['data']['secretaries']] if 'secretaries' in about_json['data'] else []
                            }
                        ]
            }
            
            ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE.replace("'", "''"),json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]       
            ROWS.append(ROW)
        return ROWS



# MAIN Execution
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
START_PAGE = 0
PER_PAGE = 250

url = BASE_API_URL.format(START_PAGE, PER_PAGE)
print('processing ',url)
try:
    res = requests.get(url,headers=headers)
except:
    sleep(30)
    try:
        res = requests.get(url,headers=headers)
    except:
        pass

if res.status_code == 200:
    records = res.json()
    TOTAL_RECORDS = int(records['data']['count'])
    NUM_PAGES = math.ceil((TOTAL_RECORDS/PER_PAGE))
else:
    print('Invalid response from server')
data = parse_json(records)
insert_data(data)

for i in range(1, NUM_PAGES):
    url = BASE_API_URL.format(i, PER_PAGE)
    print(f'Processing', url)
    try:
        res = requests.get(url)
    except:
        continue
    if res.status_code == 200:
        records = res.json()
        print(len(records['data']['items']))
        data = parse_json(records)
        insert_data(data)
    else:
        print('Invalid response from server')
        sleep(10)
        continue