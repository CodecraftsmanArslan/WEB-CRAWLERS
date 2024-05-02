"""Set System Path"""
import sys
from pathlib import Path
"""Import required library"""
import json, os
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from CustomCrawler import CustomCrawler
load_dotenv()

arguments = sys.argv
PAGE_NUMBER = int(arguments[1]) if len(arguments)>1 else 1

DATA_SIZE = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

ENV =  {
            'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')            
        }

meta_data = {
    'SOURCE' :"New Hampshire Secertary of State",
    'COUNTRY' : "New Hampshire",
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://quickstart.sos.nh.gov/online/BusinessInquire/LandingPageBusinessSearch", 
                        "Source Description": "Online tool that allows users to search for businesses registered in New Hampshire. The website is provided by the New Hampshire Secretary of States office and allows users to search for businesses by name, identification number, registered agent, and more."},
    'URL' : 'https://quickstart.sos.nh.gov/online/BusinessInquire/LandingPageBusinessSearch',
    "SOURCE_TYPE":"HTML"
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "New Hampshire Official Registry"
}

def prepare_data_object(record):
    '''
    Description: This method is prepare data the whole data and append into an dictionary
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''
    # preparing addresses_detail dictionary object
    addresses_detail = dict()
    addresses_detail["type"]= "general_address"
    addresses_detail["address"]= record[-3].replace("'","").replace("%","%%")
    
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['aliases'] = record[4].replace("'","")
    meta_detail['source_url'] = record[1].replace("'","")
    previous_names_details = [
        {
        'name' : record[3].replace("'","")
        } if record[3].replace("'","") != "" else None
    ]
    previous_names_details = [c for c in  previous_names_details if c ]
    # prepare addintiona detail object
    
    people_detail = [
        {
        "designation":"registered_agent",
        "name":record[-2].replace("'","")
        } if record[-2].replace("'","") != "N/A" else None
    ]
    people_detail = [c for c in people_detail if c]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","").replace('\"',""),
        "status": record[-1],
        "registration_number": record[2],
        "registration_date": "",
        "dissolution_date": "",
        "type": record[-4],
        "crawler_name": "crawlers.custom_crawlers.kyb.new_hampshire.new_hampshire_new",
        "country_name": "New Hampshire",
        "company_fetched_data_status": "",
        "people_detail":people_detail,
        "previous_names_detail":previous_names_details,
        "addresses_detail": [addresses_detail],
        "meta_detail": meta_detail
    }

    return data_obj

try:
    newhampshire_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
    request_helper =  newhampshire_crawler.get_requests_helper()
    get_url = 'https://quickstart.sos.nh.gov/online/BusinessInquire/LandingPageBusinessSearch'
    res = request_helper.make_request(get_url, method='Get')
    cookies_dict = res.cookies.get_dict()
    pidx = PAGE_NUMBER
    is_page_counted = False
    
    STATUS_CODE = res.status_code
    DATA_SIZE = len(res.content)
    CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'

    while True:
        body = {
            "sortby": "BusinessID",
            "stype": "a",
            "pidx": str(pidx)
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": f"ASP.NET_SessionId={cookies_dict['ASP.NET_SessionId']}"
        }
        post_url = 'https://quickstart.sos.nh.gov/online/BusinessInquire/BusinessSearchList'
        data_res = request_helper.make_request(post_url, headers=headers, data=body,method='POST')
        # Wait for the page to load
        all_data = []
        soup = BeautifulSoup(data_res.content, 'html.parser')
        table = soup.find_all('table')[0]
        if not is_page_counted:
            page_count = soup.find('li',class_ = 'pageinfo').text.split(',')[0].split('of')[-1].strip()
            is_page_counted = True
        
        if pidx == int(page_count):
            break
        
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            cpname_ = tds[0].get_text(strip = True)
            try:
                source_url  = 'https://quickstart.sos.nh.gov'+tds[0].find('a').get('href')
                reg_num = tds[1].get_text(strip = True)
                aliases = tds[2].get_text(strip = True)
                previous_name =tds[3].get_text(strip = True)
                type_ = tds[4].get_text(strip = True)
                address = tds[5].get_text(strip = True)
                registered_agent = tds[6].get_text(strip = True)
                status = tds[7].get_text(strip = True)
            except:
                source_url,reg_num, aliases, = " ", " ", " ",
            all_data.append([cpname_, source_url,reg_num,aliases,previous_name, type_, address, registered_agent, status])
        
        for data in all_data:
            NAME = data[0]
            ENTITY_ID = newhampshire_crawler.generate_entity_id(data[2])
            BIRTH_INCORPORATION_DATE = ""
            DATA = prepare_data_object(data)
            ROW = newhampshire_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,DATA)
            
            newhampshire_crawler.insert_record(ROW)
            pidx += 1
            print('Page number:', pidx)
    newhampshire_crawler.end_crawler()
    
    log_data = {"status": 'success',
                     "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    newhampshire_crawler.logger.log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    newhampshire_crawler.db_log(log_data)

