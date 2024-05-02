"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
import json
import string
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE': 'Federation of Yemen Chambers of Commerce and Industry (FYCCI)',
    'COUNTRY': 'Yemen',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://fycci-ye.org/?act=dalil&dsearch=&dfeaa=&gov=&lang=en",
                      "Source Description": "The Federation of Yemen Chambers of Commerce and Industry is a key leader in forging sustainable development strategies by building an effective and strong private sector capable of dealing with the changes in the surrounding environment."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://fycci-ye.org/?act=dalil&dsearch=&dfeaa=&gov=&lang=en'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Yemen Official Registry"
}

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv

start_number = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 2
end_number = 5194

yemen_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = yemen_crawler.get_requests_helper()

def get_data():
    for i in range(start_number, end_number):
        print(f"Scrapping data for reg no: {i} ")
        response = request_helper.make_request(url=f"https://fycci-ye.org/?act=dalil&did={i}&lang=en")
        data = response.text
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        trs = table.find_all('tr')

        all_data = {}
        for tr in trs:
            text_ = tr.text
            td = tr.find('td')
            key = text_.replace(td.text, '')
            all_data[key] = td.text
    
        name_ = all_data.get("Business Name", "")
        business_owner = all_data.get("Business Owner", "")
        category = all_data.get("Category", "")
        agencies = all_data.get("Agencies", "")
        goods = all_data.get("Goods", "")
        services = all_data.get("Services", "")
        jurisdiction = all_data.get("Governarate", "")
        place = all_data.get("Place", "")
        address = all_data.get("Address", "")
        phone_number = all_data.get("Phone", "")
        fax = all_data.get("Fax", "")
        email = all_data.get("Email", "")
        website = all_data.get("Website", "")
        registraion_number = i

        if address and place and jurisdiction:
            complete_address = f"{address}, {place}, {jurisdiction}"
        elif address and jurisdiction:
            complete_address = f"{address}, {jurisdiction}"
        elif place and jurisdiction:
            complete_address = f"{place}, {jurisdiction}"
        else:
            complete_address = f"{address} {place} {jurisdiction}"

        if goods and services:
            industries = f"{goods}, {services}"
        elif goods:
            industries = goods
        else:
            industries = services

        OBJ = {
            "registration_number": str(registraion_number),
            "name": name_,
            "people_detail": [
                {
                    "designation": "owner",
                    "name": business_owner
                }
            ],
            "addresses_detail": [
                {
                    "type": "general_address",
                    "address": complete_address
                }
            ],
            "industries": industries,
            "type": category,
            "contacts_detail": [
                {
                    "type": "phone_number",
                    "value": phone_number
                },
                {
                    "type": "fax",
                    "value": fax,
                },
                {
                    "type": "email",
                    "value": email
                },
                {
                    "type": "website",
                    "value": website
                }
            ],
            "agencies": agencies,
            "jurisdiction": jurisdiction
        }

        OBJ = yemen_crawler.prepare_data_object(OBJ)
        ENTITY_ID = yemen_crawler.generate_entity_id(OBJ['registration_number'], OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ''
        ROW = yemen_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
        yemen_crawler.insert_record(ROW)

    return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = get_data()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML"}
    yemen_crawler.db_log(log_data)
    yemen_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    yemen_crawler.db_log(log_data)
