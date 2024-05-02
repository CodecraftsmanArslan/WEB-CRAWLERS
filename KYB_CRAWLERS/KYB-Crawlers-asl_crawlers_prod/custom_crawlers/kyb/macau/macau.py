"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Government of the Macau Special Administrative Region, China',
    'COUNTRY' : 'Macau S.A.R',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.io.gov.mo/pt/entities/priv/cat/commercial", 
                        "Source Description": "Official directory of gambling companies operating in Macau, China. The website is provided by the government of the Macau Special Administrative Region and lists both local and foreign companies involved in the gambling industry in Macau. The directory includes information such as the company's name, address, and contact information, as well as the nature of their gambling activities."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.io.gov.mo/pt/entities/priv/cat/commercial'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Macau S.A.R Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

macau_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  macau_crawler.get_requests_helper()

arguments = sys.argv
PAGE_NUM = int(arguments[1]) if len(arguments)>1 else 1

try:
    for page_num in range(PAGE_NUM,61):
        print("page_num",page_num)
        url = f'https://www.io.gov.mo/pt/entities/priv/cat/commercial/?p={page_num}'
        print(url)
        response  = request_helper.make_request(url)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table',class_=  'table')
        rows = table.find_all('tr')
        base_url  = 'https://bo.io.gov.mo'
        for row in rows[1:]:
            cells = row.find_all('td')
            name = cells[0].get_text(strip = True)
            bon = cells[1].get_text(strip = True)
            try:
                file_url = base_url+cells[1].find('a').get('href')
            except: 
                file_url = ""
            publication_date = cells[2].get_text(strip = True).replace("/","-")
            
            OBJ = {
                "name":name,
                "bo_no":bon,
                "publication_date":publication_date,
                "file_url":file_url
            }
            OBJ =  macau_crawler.prepare_data_object(OBJ)
            ENTITY_ID = macau_crawler.generate_entity_id(OBJ)
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = macau_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            macau_crawler.insert_record(ROW)

    macau_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    macau_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    macau_crawler.db_log(log_data) 