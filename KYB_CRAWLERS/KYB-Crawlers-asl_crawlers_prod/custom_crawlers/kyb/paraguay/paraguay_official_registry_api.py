"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

meta_data = {
    'SOURCE' :'Registro Único del Contribuyente (RUC)',
    'COUNTRY' : 'Paraguay',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ruc.com.py/", 
                        "Source Description": "Registro Único del Contribuyente (Unique Taxpayer Registry) in Paraguay, It is a unique identification number assigned to individuals and businesses for tax purposes by the tax authority of Paraguay, known as the Subsecretaría de Estado de Tributación (SET)."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.ruc.com.py/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Paraguay official registry"
}
    
paraguay_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  paraguay_crawler.get_requests_helper()
selenium_helper = paraguay_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=True,Nopecha=False)

try:
    driver.get('https://www.ruc.com.py/')
    time.sleep(5)
    cookies = driver.get_cookies()
    cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    arguments = sys.argv
    SEARCH_NUM = int(arguments[1]) if len(arguments)>1 else 80000001
    API = 'https://www.ruc.com.py/index.php/inicio/consulta_ruc'
    
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie_str,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
        }
    for i in range(SEARCH_NUM, 80133323):
        print(i)
        payload = f'buscar={i}'
        response = request_helper.make_request(API,method='POST',headers=headers,data=payload)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        if len(response.content) == 0:
            continue
        response_data = response.json()
        for data in response_data:
            NAME = data['c_razon_social']
            registration_number = data['c_ruc']
            OBJ={
                "name":NAME,
                "registration_number":registration_number,
            }
            OBJ =  paraguay_crawler.prepare_data_object(OBJ)
            ENTITY_ID = paraguay_crawler.generate_entity_id(OBJ['registration_number'])
            BIRTH_INCORPORATION_DATE =''
            ROW = paraguay_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            paraguay_crawler.insert_record(ROW)

    paraguay_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    paraguay_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    paraguay_crawler.db_log(log_data)    
