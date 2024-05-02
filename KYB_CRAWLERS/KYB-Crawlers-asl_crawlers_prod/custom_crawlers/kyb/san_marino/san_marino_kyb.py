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
SOURCE = "The San Marino Economic Development Agency - Chamber of Commerce"
COUNTRY = ["San Marino"]
CATEGORY = ["Official Registry"]
ENTITY_TYPE = "Company/Organization"
SOURCE_DETAIL = {"Source URL": "https://www.camcom.sm/en/business-directory/", 
                 "Source Description": "It is a joint-stock company with mixed public and private capital, which supports foreign entrepreneurs and investors and assists local businesses in their internationalisation strategies."}
IMAGES = []
BASE_URL = 'https://www.camcom.sm'

def crawl_details(ITEMS):
    ROWS = []
    for ITEM in ITEMS:
        url = ITEM['url']
        card = None
        retry_count = -1
        while card is None:
            print('Processing ',f'{BASE_URL}{url}')
            res = requests.get(f'{BASE_URL}{url}', headers=headers)
            soup = BeautifulSoup(res.text, 'lxml')
            card = soup.find(id='ts-camcom-card-single')
            if card is not None:
                break
            else:
                retry_count += 1
                print('Element not found retrying.')
                if retry_count>2:
                    break
                sleep(1)
        
        if card is not None:
            box_content_el = card.find('div',{'class':'info-box-content'})
            title_el = box_content_el.find('h4',{'class':'info-box-title'})
            NAME = title_el.text.strip()

            info_el = box_content_el.find('div',{'class':'info-box-inner'})
            i_soup  = BeautifulSoup(str(info_el.prettify()).replace('<br/>','^&*'),'lxml')
            arr = [i.strip().replace('  ','').replace('\n','') for i in i_soup.text.split('^&*')]
            arr = list(filter(None, arr))
            ADDRESS = arr[0].strip()
            del arr[0]
            OBJ = {}
            for e in arr:
                [key, value, *any] = e.split(':')
                key = key.lower().replace(':','').strip()
                if any == []:
                    OBJ[key] =value.strip()
                else:
                    OBJ[key] =any[0].strip()
            
            OBJ['name'] = NAME
            OBJ['address'] = ADDRESS
            body_el = card.find('div',{'class':'wd-tab-content-wrapper'})
            keys_els = body_el.find_all('strong')
            values_els = body_el.find_all('p')

            for i,key_el in enumerate(keys_els):
                key = keys_els[i].text.strip().lower().replace(' ','_')
                value = values_els[i].text.strip()
                OBJ[key] = value
            ENTITY_ID = shortuuid.uuid(f'{BASE_URL}{url}')
            ADDRESS = OBJ['address']

        else:
            NAME = ITEM['title']
            ADDRESS = ITEM['address']
            ENTITY_ID = shortuuid.uuid(f'{BASE_URL}{url}')
            OBJ = ITEM

        BIRTH_INCORPORATION_DATE = []
        DATA = {
                    "name": NAME,
                    "status": '',
                    "registration_number": OBJ['coe'] if 'coe' in OBJ else '',
                    "registration_date": '',
                    "dissolution_date": "",
                    "type": '',
                    "crawler_name": "custom_crawlers.kyb.san_marino_kyb",
                    "country_name": COUNTRY[0],
                    "company_fetched_data_status": "",
                    "addresses_detail": [
                        {
                            "type": "general_address",
                            "address": OBJ['address']
                        } if OBJ['address'].strip()!='' else {}
                    ],
                    "meta_detail": {
                        'source_url': f'{BASE_URL}{url}',
                        **({'trade_code': OBJ['codice_ateco_principale']} if 'codice_ateco_principale' in OBJ else {}),
                        **({'description': OBJ['descrizione']} if 'descrizione' in OBJ else {}),
                        **({'number_of_employees': OBJ['numero_dipendenti']} if 'numero_dipendenti' in OBJ else {})
                    },
                    "contacts_detail": [
                        {
                            'type': 'telephone_number',
                            'value': OBJ['telefono'] if 'telefono' in OBJ else '',
                        } if 'telefono' in OBJ and OBJ['telefono'] is not None else '',
                        {
                            'type': 'fax_number',
                            'value': OBJ['fax'] if 'fax' in OBJ else '',
                        } if 'fax' in OBJ and OBJ['fax'] is not None else '',
                        {
                            'type': 'website_link',
                            'value': OBJ['sito_web'] if 'sito_web' in OBJ else '',
                        }  if 'sito_web' in OBJ and OBJ['sito_web'] is not None else ''
                    ],
                    "additional_detail":[
                        {
                            'type': 'capital_information',
                            'data': [
                                {
                                    'capital': OBJ['capitale_sociale'] if 'capitale_sociale' in OBJ else '',
                                    'turnover_range': OBJ['fascia_di_fatturato'] if 'fascia_di_fatturato' in OBJ else ''
                                }
                            ],
                        } if 'capitale_sociale' in OBJ or 'fascia_di_fatturato' in OBJ else ''
                    ]
                }
        DATA['additional_detail'] = [p for p in  DATA['additional_detail'] if p]
        DATA['contacts_detail'] = [a for a in  DATA['contacts_detail'] if a]
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
        ROWS.append(ROW)
    return ROWS



# data = crawl_details(['/notice/4317616'])

# Main execution entry point

MAIN_URL = 'https://www.camcom.sm/annuario-imprese/ricerca/?text-impresa=%20%20%20&text-ragsoc=&text-address=&text-castle=&text-coe=&text-ateco=&your-page={}&your-per_page=20'

print('Processing ', MAIN_URL.format(1))
res = requests.get(MAIN_URL.format(1), headers=headers)
if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'lxml')
    card_list_c_el = soup.find(id='ts-camcom-card-list')
    card_list = card_list_c_el.find_all('div',{'class':'vc_column-inner'})

    ITEMS = []
    for card in card_list:
        info_el = card.find('div',{'class':'info-box-content'})
        title = info_el.find('h4',{'class':'info-box-title'}).text.strip()
        line_info_el = info_el.find('div',{'class':'line-info-content'})
        i_soup  = BeautifulSoup(str(line_info_el.prettify()).replace('<br/>','^&*'),'lxml')
        arr = [i.strip().replace('  ','').replace('\n','') for i in i_soup.text.split('^&*')]
        arr = list(filter(None, arr))
        ADDRESS = arr[0].strip() if len(arr)>0 else ''
        if len(arr)>0:
            del arr[0]
        card_link = card.find('a',{'class':'btn-color-primary'}).get('href')
        OBJ = {'title':title,'address':ADDRESS, 'url':card_link}
        for e in arr:
            [key, value, *any] = e.split(':')
            key = key.lower().replace(':','').replace('.','').strip()
            if any == []:
                OBJ[key] =value.strip()
            else:
                OBJ[key] =any[0].strip()
        ITEMS.append(OBJ)
    
    data = crawl_details(ITEMS)
    insert_data(data)
    pagin_div = soup.find('div',{'class':'ts-camcom-pagination'})
    pagin_ul = pagin_div.find('ul')
    n = len(pagin_ul.find_all('li'))
    for i in range(2,n+1):
        print('Processing ', MAIN_URL.format(i))
        res = requests.get(MAIN_URL.format(i), headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            card_list_c_el = soup.find(id='ts-camcom-card-list')
            card_list = card_list_c_el.find_all('div',{'class':'vc_column-inner'}) if card_list_c_el is not None else []
            ITEMS = []
            for card in card_list:
                info_el = card.find('div',{'class':'info-box-content'})
                title = info_el.find('h4',{'class':'info-box-title'}).text.strip()
                line_info_el = info_el.find('div',{'class':'line-info-content'})
                i_soup  = BeautifulSoup(str(line_info_el.prettify()).replace('<br/>','^&*'),'lxml')
                arr = [i.strip().replace('  ','').replace('\n','') for i in i_soup.text.split('^&*')]
                arr = list(filter(None, arr))
                ADDRESS = arr[0].strip() if len(arr)>0 else ''
                if len(arr)>0:
                    del arr[0]
                card_link = card.find('a',{'class':'btn-color-primary'}).get('href')
                OBJ = {'title':title,'address':ADDRESS, 'url':card_link}
                for e in arr:
                    [key, value, *any] = e.split(':')
                    key = key.lower().replace(':','').replace('.','').strip()
                    if any == []:
                        OBJ[key] =value.strip()
                    else:
                        OBJ[key] =any[0].strip()
                ITEMS.append(OBJ)

            data = crawl_details(ITEMS)
            insert_data(data)
else:
    print('Invalid response from server ', res.status_code)
print('FINISHED')