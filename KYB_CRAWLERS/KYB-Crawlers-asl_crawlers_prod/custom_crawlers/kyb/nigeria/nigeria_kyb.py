"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Federal Ministry of Commerce and Tourism -  Corporate Affairs Commission (CAC)',
    'COUNTRY' : 'Nigeria',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ecitibiz.interior.gov.ng/Expatriate/CompanyVerification", 
                        "Source Description": ""},
    'URL' : 'https://ecitibiz.interior.gov.ng/Expatriate/CompanyVerification',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Nigeria'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://business.egov.mv'

nigeria_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  nigeria_crawler.get_requests_helper()

def get_data(keyword):
    data = []
    url = "https://ecitibiz.interior.gov.ng/Expatriate/CompanyVerificationList"
    form_data = {
        "CompanyName": keyword
    }
    headers = {
        "Authority": "ecitibiz.interior.gov.ng",
        "Method": "POST",
        "Path": "/Expatriate/CompanyVerificationList",
        "Scheme": "https",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Length": "13",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://ecitibiz.interior.gov.ng",
    }
    response = request_helper.make_request(url, method="POST", data=form_data, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'myTable'})
        headers = table.find_all('th')
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            value_key_pair = {}
            tds = tr.find_all('td')
            for td, th in zip(tds, headers):
                value_key_pair[th.text] = td.text
            data.append(value_key_pair)
    else:
        print("Request failed with status code:", response.status_code)
    return data

try:
    records = get_data('_')
    for data in records:            
        DATA = {
            'registration_number': data.get('RC Number'),
            'name': data.get('Company Name'),
            'status': data.get('Company STATUS'),
            'industries': data.get('Company Sector'),
            'addresses_detail': [{
                'type': 'general_address',
                'address': data.get('Address')
            }] if data.get('Address') != "" and data.get('Address') is not None else []
        }
        ENTITY_ID = nigeria_crawler.generate_entity_id(company_name=data.get('Company Name'), reg_number=data.get('RC Number'))
        BIRTH_INCORPORATION_DATE = ''
        DATA = nigeria_crawler.prepare_data_object(DATA)
        ROW = nigeria_crawler.prepare_row_for_db(ENTITY_ID, data.get('Company Name'), BIRTH_INCORPORATION_DATE, DATA)
        nigeria_crawler.insert_record(ROW)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    nigeria_crawler.db_log(log_data)
    nigeria_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    nigeria_crawler.db_log(log_data)