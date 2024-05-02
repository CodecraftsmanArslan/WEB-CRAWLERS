"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Saint Lucia Companies and Intellectual Property Office (CIPO)',
    'COUNTRY' : 'Saint Lucia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "http://efiling.rocip.gov.lc/", 
                        "Source Description": "Saint Lucia Companies and Intellectual Property Office (CIPO) is the government agency responsible for the registration and administration of companies and intellectual property in Saint Lucia. The CIPO is tasked with maintaining the official records and documentation related to companies registered in Saint Lucia. It handles the incorporation and registration of companies, the filing of annual returns, and the administration of intellectual property rights such as trademarks and patents."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'http://efiling.rocip.gov.lc/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Saint Lucia Official Registry"
}

saint_lucia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
s =  saint_lucia_crawler.get_requests_session()

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
start_year = int(arguments[1]) if len(arguments)>1 else 1943

arguments2 = sys.argv
start_num = int(arguments2[2]) if len(arguments2)> 2 else 1

API_URL = 'http://efiling.rocip.gov.lc/api/1.0/services/loadInfoProc'
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "efiling.rocip.gov.lc",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

combinations = []
for year in range(start_year, 2023):
    for letter in ['B', 'C']:
        for number in range(start_num, 1000):
            formatted_number = '{:03d}'.format(number)
            combinations.append(f"{year}/{letter}{formatted_number}")

try:
    for number in combinations:
        print('\nSearch_number',number)
        PAYLOAD = {"input":f"key=0,query={number}","name":"EntitySearch"}
        respone = s.post(API_URL,headers=HEADERS, json=PAYLOAD)

        SATAUS_CODE = respone.status_code
        DATA_SIZE = len(respone.content)
        CONTENT_TYPE = respone.headers['Content-Type'] if 'Content-Type' in respone.headers else 'N/A'
        api_data = respone.json()
        if len(api_data)==0:
            continue
        for data in api_data['rows']:
            people_detail = []
            if data.get('Directors',''):
                people_detail.append({
                                        "designation":'director',
                                        "name":data.get('Directors','')
                                    })
            
            if data.get('Shareholders',''):
                people_detail.append({
                                    "designation":'shareholder',
                                    "name":data.get('Shareholders','')
                                })
            
            address_detail = []
            if data.get('PrincipalOfficeAddress',''):
                address_detail.append({
                                "type": "general_address",
                                "address": data.get('PrincipalOfficeAddress','') if data.get('PrincipalOfficeAddress','') else ''
                            })
            OBJ = {
                    'name':data.get('EntityName',''),
                    'registration_number':data.get('EntityNumber',''),
                    'status':data.get('StatusName','') if data.get('StatusName','') else '',
                    'registration_date':data.get('DateOfIncorporation','').split('T')[0] if data.get('DateOfIncorporation','') else '',
                    'type':data.get('TypeName','') if data.get('TypeName','') else '',
                    "profit_status":data.get('ProfitStatus','') if data.get('ProfitStatus','') else '',
                    "addresses_detail": address_detail,
                    "people_detail":people_detail
                }

            OBJ =  saint_lucia_crawler.prepare_data_object(OBJ)
            ENTITY_ID = saint_lucia_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ''
            ROW = saint_lucia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            saint_lucia_crawler.insert_record(ROW)

    saint_lucia_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":"",  "crawler":"HTML"}
    saint_lucia_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    saint_lucia_crawler.db_log(log_data) 