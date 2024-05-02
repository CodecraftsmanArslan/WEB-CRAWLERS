import requests
from bs4 import BeautifulSoup
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json

# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
def insert_data(row):
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
SOURCE = 'Securities and Exchange Commission (SEC) in the Philippines'
COUNTRY = ['Philippines']
CATEGORY = ['Company/SIE']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "http://cmprs.sec.gov.ph/", 
                 "Source Description": "Official directory of registered firms and individuals provided by the Securities and Exchange Commission (SEC) in the Philippines.The directory includes information such as the registered firm's name, address, and contact information, as well as the type of securities license held."}
IMAGES = []
# METHOD TO PARSE CSV

# Entry point main
BASE_URL = 'http://cmprs.sec.gov.ph'
res = requests.get(BASE_URL)
if res.status_code == 200:
    soup = BeautifulSoup(res.text,'lxml')
    div_list = soup.find('div', id='base-institution-list-grid')
    table = div_list.find('table')
    for tr in table.find_all('tr')[1:]:
        tds = tr.find_all('td')
        _id, name, licence_type, url = tds[0].text, tds[1].text, tds[2].text,tds[3].a.get('href')
        print('processing ', BASE_URL+url)
        res = requests.get(BASE_URL+url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'lxml')
            # extracting company details
            yw1 = soup.find('table',id='yw1')

            trs = yw1.find_all('tr')
            NAME, FORMER_NAME, CERT_REG_NUMBER, LICENCE_TYPE, LAST_ANUAL_FEE_PAYMENT = trs[0].td.text.strip(), trs[1].td.text.strip(), trs[2].td.text.strip(), trs[3].td.text.strip(), trs[4].td.text.strip()
            BIRTH_INCORPORATION_DATE = []
            ENTITY_ID = shortuuid.uuid(CERT_REG_NUMBER)
            # extracting people
            yw2 = soup.find('div',id='yw2')
            table = yw2.find('table')
            tbody = table.find('tbody')
            PEOPLE = []
            for tr in tbody.find_all('tr'):
                tds = tr.find_all('td')
                try:
                    p_name, p_cert_reg_no, p_licence_type, p_last_annual_payment_date = tds[1].text.strip(),tds[2].text.strip(),tds[3].text.strip(),tds[4].text.strip()
                    p = {
                        'name': p_name,
                        'certificate_registration_number': p_cert_reg_no,
                        'type': p_licence_type,
                        'last_annual_payment_date': p_last_annual_payment_date
                    }
                    PEOPLE.append(p)
                except:
                    pass
            
            DATA = {
                "name": NAME,
                "status": '',
                "registration_number": CERT_REG_NUMBER,
                "registration_date": '',
                "dissolution_date": '',
                "type": '',
                "crawler_name": "custom_crawlers.kyb.philippines.philippines_kyb_csv",
                "country_name": COUNTRY[0],
                "company_fetched_data_status": "",
                "meta_detail": {
                 "last_annual_fee": LAST_ANUAL_FEE_PAYMENT,
                 "licence_type": LICENCE_TYPE,
                 "former_name": FORMER_NAME
                },
                "people_detail": PEOPLE
              }
            ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
                json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
                SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
            insert_data(ROW)
else:
    print('Invalid response from server http_code:', res.status_code)
print('FINISHED')