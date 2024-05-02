"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import traceback,sys
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By

meta_data = {
    'SOURCE' :'Ministry of Legal Affairs - Intellectual Property and Commerce Office (ABIPCO)',
    'COUNTRY' : 'Antigua And Barbuda',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://abipco.gov.ag/", 
                        "Source Description": "The Antigua and Barbuda Intellectual Property and Companies Office falls under the Ministry of Legal Affairs which originally formed part of the High Court was established as a separate Department with the responsibility for the day to day administration of companies, business names, trademarks, industrial designs, geographic indications, and other types of intellectual property."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://abipco.gov.ag/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Antigua And Barbuda Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

antigua_barbuda_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = antigua_barbuda_crawler.get_selenium_helper()
s =  antigua_barbuda_crawler.get_requests_session()


API_URL = 'https://abipco.gov.ag/api/1.0/services/loadInfoProc'
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://abipco.gov.ag",
    "Referer": "https://abipco.gov.ag/efile/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
arguments = sys.argv
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
start_char = sys.argv[1] if len(sys.argv) > 1  else "a"
start_index = alphabets.index(start_char)

try:
    for char in range(start_index, len(alphabets)):
        word = alphabets[char]
        print('\nAlphabetic charter =', word)
        payload = {"input":f"key=0,query={char}","name":"EntitySearch"}
        response = s.post(API_URL,headers=headers,json=payload)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        api_data = response.json()
        for data in api_data['rows']:
            OBJ = {
                "name":data['EntityName'],
                "type":data.get('TypeName','') if data.get('TypeName','') else '',
                "registration_number":data.get('EntityNumber',''),
                "industries":data.get('registry','') if data.get('registry','') else '',
                'registration_date':data.get('DateOfIncorporation','').split('T')[0] if data.get('DateOfIncorporation','') else "",
                'status':data.get('StatusName','') if data.get('StatusName','') else '',
                "addresses_detail":[
                    {
                        "type":"general_address",
                        "address":data.get('PrincipalOfficeAddress','') if data.get('PrincipalOfficeAddress','') else ''
                    }
                ],
            }
            OBJ =  antigua_barbuda_crawler.prepare_data_object(OBJ)
            ENTITY_ID = antigua_barbuda_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = OBJ['registration_date']
            ROW = antigua_barbuda_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            antigua_barbuda_crawler.insert_record(ROW)

    antigua_barbuda_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    antigua_barbuda_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    antigua_barbuda_crawler.db_log(log_data) 
