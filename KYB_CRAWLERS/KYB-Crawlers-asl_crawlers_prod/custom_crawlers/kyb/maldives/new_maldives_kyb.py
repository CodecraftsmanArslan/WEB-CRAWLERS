"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from registeration_numbers import registeration_numbers
from dateutil import parser

meta_data = {
    'SOURCE' :'Business Portal,Government of Maldives',
    'COUNTRY' : 'Maldives',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://business.egov.mv/BusinessRegistry", 
                        "Source Description": "Official business registry provided by the government of Maldives. The website allows users to search for registered businesses and business owners in the Maldives using various search criteria such as company name, registration number, and owner name. "},
    'URL' : 'https://business.egov.mv/BusinessRegistry',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Maldives'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://business.egov.mv'

maldives_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  maldives_crawler.get_requests_helper()

def format_date(timestamp):
    try:
        datetime_obj = parser.parse(timestamp)
        return datetime_obj.strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return ""

def get_record_urls(query):
    urls = []
    url = f"{BASE_URL}/BusinessRegistry/SearchBusinessRegistry"
    response = request_helper.make_request(url, method="POST", data={"query": query})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        anchor_tags = soup.find_all('a', class_='btn_1 outline')
        for tag in anchor_tags:
            urls.append(tag.get('href'))
    return urls

def process_section(div, data):
    heading = div.find('h3').text.strip()
    designation_mapping = {
        "Managing Director": "managing_director",
        "Owner": "owner",
        "Board of Directors": "board_director",
        "Shareholders": "shareholder",
        "Business Names": "business_names",
        "Business Activities": "business_activities",
        "Permits": "permits",
        "Licenses": "licenses"
    }

    designation = designation_mapping.get(heading, None)
    if designation:
        if designation in ("managing_director", "owner"):
            name_ = div.find('p').text.strip()
            data["people_detail"].append({
                "designation": designation,
                "name": name_
            })
        elif designation in ("board_director", "shareholder"):
            step_elmemt = div.find_next('div', class_="step")
            table = step_elmemt.find('table')
            if table is not None:
                trs = table.find_all('tr')
                for tr in trs[1:]:
                    tds = tr.find_all('td')
                    meta_detail = {}
                    if designation == "shareholder":
                        meta_detail["joining_date"] = format_date(tds[1].text.strip())
                    data["people_detail"].append({
                        "designation": designation,
                        "name": tds[0].text.strip(),
                        "meta_detail": meta_detail
                    })
        elif designation in ("business_names", "business_activities", "permits", "licenses"):
            step_elmemt = div.find_next('div', class_="step")
            table = step_elmemt.find('table')
            if table is not None:
                trs = table.find_all('tr')
                for tr in trs[1:]:
                    tds = tr.find_all('td')
                    meta_detail = {}
                    if designation == "business_names":
                        meta_detail["number"] = tds[1].text.strip()
                        data["previous_names_detail"].append({
                            "name": tds[0].text.strip(),
                            "meta_detail": meta_detail
                        })
                    elif designation == "business_activities":
                        meta_detail["number"] = tds[1].text.strip()
                        data["additional_detail"].append({
                            "type": "business_activities",
                            "data": [{
                                "number": tds[0].text.strip(),
                                "activity": tds[1].text.strip(),
                                "state": tds[2].text.strip(),
                                "issued_date": format_date(tds[3].text.strip()),
                                "expiry_date": format_date(tds[4].text.strip()),
                                "business_name": tds[5].text.strip()
                            }]
                        })
                    elif designation == "permits":
                        meta_detail["number"] = tds[1].text.strip()
                        data["additional_detail"].append({
                            "type": "permit_information",
                            "data": [{
                                "permit_number": tds[0].text.strip(),
                                "name": tds[1].text.strip(),
                                "type": tds[2].text.strip(),
                                "status": tds[3].text.strip(),
                                "issued_date": format_date(tds[4].text.strip()),
                                "expiry_date": format_date(tds[5].text.strip())
                            }]
                        })
                    elif designation == "licenses":
                        meta_detail["number"] = tds[1].text.strip()
                        data["additional_detail"].append({
                            "type": "license_information",
                            "data": [{
                                "license_number": tds[0].text.strip(),
                                "type": tds[1].text.strip(),
                                "status": tds[2].text.strip(),
                                "issued_date": format_date(tds[3].text.strip()),
                                "expiry_date": format_date(tds[4].text.strip())
                            }]
                        })

def get_data(url):
    data = {
        "addresses_detail": [],
        "people_detail": [],
        "previous_names_detail": [],
        "additional_detail": []
    }
    response = request_helper.make_request(f"{BASE_URL}{url}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        name_element = soup.find('h1', class_='name')
        status_element = name_element.find('span')
        status = status_element.get_text(strip=True) if status_element else ""
        data["name"] = name_element.get_text(strip=True).replace(status, '')
        data["type"] = status.replace("[", "").replace("]", "")
        address = soup.find('p', class_='address').get_text(strip=True)
        data["addresses_detail"].append({
            "type": "general_address",
            "address": address
        })
        number_element = soup.find('p', class_='number').find('span', class_='')
        data["status"] = number_element.get_text(strip=True) if number_element else ""
        sme_element = soup.find('p', class_='smeClassification')
        reg_date = sme_element.find('span')
        data["registration_date"] = format_date(reg_date.get_text(strip=True).replace("Classified date:", "")) if reg_date is not None else ""
        data["business_scale"] = sme_element.get_text(strip=True).replace("SME Classification:", "").replace(data["registration_date"], "").replace("Classified date:", "") if sme_element is not None else ""
        container_element = soup.find('div', class_='add_bottom_15')
        divs = container_element.find_all('div', class_='form_title')
        for div in divs:
            process_section(div, data)
    return data

if len(sys.argv) > 1:
    start = sys.argv[1]
else:
    start = "SP18562021"

flag = True
try:
    for reg_num in registeration_numbers:
        if start != reg_num and flag: continue
        else: flag = False
        print('Record No:', reg_num)
        urls = get_record_urls(reg_num)
        for url in urls:
            DATA = get_data(url)
            DATA["registration_number"] = reg_num
            NAME = DATA.get('name')
            ENTITY_ID = maldives_crawler.generate_entity_id(company_name=NAME, reg_number=reg_num)
            BIRTH_INCORPORATION_DATE = ''
            DATA = maldives_crawler.prepare_data_object(DATA)
            ROW = maldives_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            maldives_crawler.insert_record(ROW)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    maldives_crawler.db_log(log_data)
    maldives_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    maldives_crawler.db_log(log_data)