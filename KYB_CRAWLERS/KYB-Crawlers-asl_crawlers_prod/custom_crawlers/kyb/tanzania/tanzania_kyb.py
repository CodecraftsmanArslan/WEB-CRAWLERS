"""Set System Path"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Business Registrations and Licensing Agency (BRELA)',
    'COUNTRY' : 'Tanzania',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ors.brela.go.tz/orsreg/searchbusinesspublic", 
                        "Source Description": "The Business Registration and Licensing Agency (BRELA) was established under the Law of Government Agencies No.30 of 1997 and was officially launched on December 3, 1999 under the Ministry of Industry and Trade.The responsibilities of the Business Registration and Licensing Agency (BRELA) are as specified in the Establishment Order No.38 of Government Announcement no.294 dated 08/10/1999."},
    'URL' : 'https://ors.brela.go.tz/orsreg/searchbusinesspublic',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Tanzania'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

tanzania_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  tanzania_crawler.get_requests_helper()

def get_data(reg_num):
    url = "https://ors.brela.go.tz/orsreg/list/search/businesspublic.json"
    headers = {
        "Host": "ors.brela.go.tz",
        "Origin": "https://ors.brela.go.tz",
        "Referer": "https://ors.brela.go.tz/orsreg/searchbusinesspublic",
    }
    json_data = {
        "object_type": "ET-BUSINESS",
        "bn_number": reg_num,
        "PageSize": 10,
        "PageNumber": 1
    }
    response = request_helper.make_request(url, method="POST", headers=headers, json=json_data)
    if response is not None and response.status_code == 200:
        return response.json()
    else:
        print("POST request failed with status code:", response.status_code)

try:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 100000 #523035
    for reg_num in range(start, 599999):
        print('Registration No:', reg_num)
        records = get_data(reg_num)
        if records is not None and 'Records' in records:
            for data in records['Records']:
                if len(data) >= 12:
                    addresses_detail = []
                    registration_number = data[2]
                    NAME = data[5]
                    address = data[12]
                    if address is not None and address != "":
                        addresses_detail.append({
                            'type': 'general_address',
                            'address': address.replace('NONE', '').replace('none', '').replace('None', '').replace('Null', '').replace('NULL', '').replace('null', '').replace(', ,', ',').replace('  ', '')
                        })
                    status = data[11]
                    OBJ = {
                        'registration_number': registration_number,
                        'name': NAME.replace("%","%%"),
                        'status': status,
                        'addresses_detail': addresses_detail
                    }
            
                    OBJ =  tanzania_crawler.prepare_data_object(OBJ)
                    ENTITY_ID = tanzania_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
                    NAME = OBJ['name']
                    BIRTH_INCORPORATION_DATE = ""
                    ROW = tanzania_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                    tanzania_crawler.insert_record(ROW)  
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    tanzania_crawler.db_log(log_data)
    tanzania_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    tanzania_crawler.db_log(log_data)