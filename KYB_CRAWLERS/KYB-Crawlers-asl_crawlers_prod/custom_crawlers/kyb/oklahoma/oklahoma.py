"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import nopecha,os
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By

meta_data = {
    'SOURCE' :'Oklahoma Secretary of State, Business Services Division',
    'COUNTRY' : 'Oklahoma',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.sos.ok.gov/corp/corpInquiryFind.aspx", 
                        "Source Description": "The Oklahoma Secretary of State, Business Services Division, is a vital administrative arm of the Oklahoma state government. This division is entrusted with the responsibility of regulating, maintaining, and providing access to a wide range of services related to businesses and corporate entities operating within the state. It serves as a central hub for businesses seeking to establish, maintain, or modify their legal presence in Oklahoma."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.sos.ok.gov/corp/corpInquiryFind.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Oklahoma Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

oklahoma_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = oklahoma_crawler.get_requests_helper()
s =  oklahoma_crawler.get_requests_session()

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 1900000000
end_number = 4990000000

try:
    for number in range(start_number,end_number):
        print("\nsearch number =", number)
        URL = f'https://www.sos.ok.gov/corp/corpInformation.aspx?id={number}'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        response = request_helper.make_request(URL,headers=headers)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.content, 'html.parser')
        NAME = soup.find('h3').get_text(strip = True)

        dt_elements = soup.find_all("dt")
        dd_elements = soup.find_all("dd")
        data = {}
        for dt, dd in zip(dt_elements, dd_elements):
            key = dt.text.strip().replace(":", "")
            value = dd.text.strip()
            data[key] = value
        try:
            qualified_status = data.get('Qualified Flag','').split('\r\n')[0].strip()
            description = data.get('Qualified Flag','').split('\r\n')[1].replace('\n\n\n','').replace('  ','').strip()
        except:
            qualified_status, description = '',''
        
        #get additional_detail
        additional_detail = []
        if qualified_status != '':
            additional_detail.append({
                        "type":"qualified_flag",
                        "data":[
                            {
                                "qualified_status":qualified_status,
                                "description":description
                            }
                        ]
                    })

        try:
            status = data.get('Status','').split('\n\n\r\n')[0].strip()
            status_info = data.get('Status','').split('\n\n\r\n')[1].strip()
        except:
            status,status_info = "",""
        #get people_detail
        people_detail = []
        if data.get('Name','') != "":
            people_detail.append({
                        "designation":'registered_agent',
                        "name":data.get('Name',''),
                        'appointment_date':data.get('Effective','').replace('N/A',""),
                        "address":data.get('Address',''),
                        "postal_address":data.get('City, State , ZipCode','').replace('\xa0\r\n','').replace('  ','').strip()
                    })

        OBJ = {
                "name": NAME,
                'registration_number':data.get('Filing Number',''),
                'type':data.get('Corp type',''),
                "name_type": data.get('Name Type',''),
                "jurisdiction":data.get('Jurisdiction',''),
                "status": status,
                'status_info':status_info,
                'registration_date':data.get('Formation Date',''),
                "additional_detail":additional_detail,
                "people_detail": people_detail
            }
        
        OBJ =  oklahoma_crawler.prepare_data_object(OBJ)
        ENTITY_ID = oklahoma_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ''
        ROW = oklahoma_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        oklahoma_crawler.insert_record(ROW)

    oklahoma_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    oklahoma_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    oklahoma_crawler.db_log(log_data) 

