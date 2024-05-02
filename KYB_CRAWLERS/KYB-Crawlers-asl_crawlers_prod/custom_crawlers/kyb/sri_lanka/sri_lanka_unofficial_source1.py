"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import pytesseract, requests
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from PIL import Image
from io import BytesIO
import pandas as pd
import random

meta_data = {
    'SOURCE' : 'listcompany, Business Directory',
    'COUNTRY' : 'Sri Lanka',
    'CATEGORY' : 'Unofficial Source',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.listcompany.org/Sri_Lanka_Country.html", 
                        "Source Description": "The source includes a vast list of companies, a huge directory of suppliers, distributors, importers, exporters, dealers, manufacturers, and business information about company profile, email, address, and other relevant details."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.listcompany.org/Sri_Lanka_Country.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Sri Lanka Unofficial Source 1"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

srilanka_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = srilanka_crawler.get_requests_helper()

def get_proxy_list():
    response = request_helper.make_request("https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/username/direct/-/")
    data = response.text
    lines = data.strip().split('\n')
    proxy_list = [line.replace('\r', '') for line in lines]
    return proxy_list

proxy_list = get_proxy_list()

def make_request(url, method="GET", headers={}, timeout=10, max_retries=10, retry_interval=10, json=None):
    for attempt in range(max_retries + 1):
        random.shuffle(proxy_list)
        for proxy in proxy_list:
            if len(proxy.split(':')) == 4:
                host, port, username, password = proxy.split(':')
                proxies = {
                    'http': f'http://{username}:{password}@{host}:{port}',
                    'https': f'http://{username}:{password}@{host}:{port}',
                }
                try:
                    response = requests.request(method, url, headers=headers, timeout=timeout, json=json, proxies=proxies)
                    if response.status_code == 200:
                        return response
                except:
                    pass
                print(f"Request with proxy failed retry in 10 seconds...")
                time.sleep(10)
        if attempt < max_retries:
            print(f"Waiting for retry in {retry_interval} seconds...")
            time.sleep(retry_interval)

def get_image_text(url):
    try:
        response = request_helper.make_request(url)
        image = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(image)
        return text
    except:
        return ''

def get_next_sibling(soup, text):
    try:
        for strong in soup.find_all('strong'):
            if text in strong.get_text(strip=True):
                return strong.find_next_sibling('span').text.strip()
    except:
        pass
    return ''

def get_telephone_num(soup, keyword):
    for strong in soup.find_all('strong'):
        if keyword in strong.get_text(strip=True):
            span = strong.find_next_sibling('span')
            img_tag = span.find('img')
            if img_tag:
                src = img_tag['src']
                if src != '':
                    return get_image_text(f"https://www.listcompany.org{src}")
    return ''

def get_main_product(soup):
    additional_detail = []
    data = []
    a_tags = soup.find('span').find_all('a')
    for strong in soup.find_all('strong'):
        if 'Main Products' in strong.get_text(strip=True):
            span_tag = strong.find_next_sibling('span')
            a_tags = span_tag.find_all('a')
            for a_tag in a_tags:
                url = a_tag['href']
                name = a_tag.get_text()
                data.append({
                    'product': name,
                    'url': f"https://www.listcompany.org{url}" if url != '' else ''
                })           
            
    additional_detail.append({
        'type': 'products_information',
        'data': data
    })
    return additional_detail

def get_related_products(soup):
    for span_element in soup.find_all('span'):
        if 'Related\xa0Product' in span_element.get_text(strip=True):
            parent_div = span_element.find_parent('div', class_='all-head')
            if parent_div:
                return parent_div.find_next_sibling('div').text.strip()
    return ''

def get_data(soup):
    item = {}
    addresses_detail = []
    contacts_detail = []
    additional_detail = []
    people_detail = []
    item['registration_number'] = ''
    item['name'] = soup.select_one("div.main h1").text.strip() if soup.select_one("div.main h1") else ''
    item['company_description'] = soup.find('div', class_='the08').get_text().replace('\r\n', ' ').replace('Company\xa0Description','').replace('\n', '') if soup.find('div', class_='the08') else ''
    item['country'] = get_next_sibling(soup, 'Country/Region')
    general_address = get_next_sibling(soup, 'Address')
    if general_address != '':
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address
        })
    operational_address = get_next_sibling(soup, 'Operational Address')
    if operational_address != '':
        addresses_detail.append({
            'type': 'operational_address',
            'address': operational_address
        })
    item['type'] = get_next_sibling(soup, 'Business Type')
    item['business_location'] = get_next_sibling(soup, 'Location')

    item['year_established'] = get_next_sibling(soup, 'Year Established')
    item['main_markets'] = get_next_sibling(soup, 'Main Markets')
    
    contact_person_name = get_next_sibling(soup, 'Contact Person')
    contact_person_job_title = get_next_sibling(soup, 'Job Title')
    contact_person_department = get_next_sibling(soup, 'Department')
    telephone = get_telephone_num(soup, 'Telephone')
    mobilephone = get_telephone_num(soup, 'Mobilephone')
    fax_number = get_telephone_num(soup, 'Fax Number')
    contact_person_address = get_next_sibling(soup, 'Zip/Post Code')

    if contact_person_name != '':
        meta_detail = {
            'mobile_number': mobilephone,
            'department': contact_person_department
        }
        people_detail.append({
            'name': contact_person_name,
            'designation': contact_person_job_title,
            'phone_number': telephone,
            'fax_number': fax_number,
            'meta_detail': meta_detail,
            'postal_address': contact_person_address
        })

    website = get_next_sibling(soup, 'Website')
    if website != '':
        contacts_detail.append({
            'type': 'website',
            'value': website
        }) 
    item['total_employees'] = get_next_sibling(soup, 'Number Of Employess')
    item['total_revenue'] = get_next_sibling(soup, 'Total Revenue')
    item['related_products'] = get_related_products(soup)
    ceo_name = get_next_sibling(soup, 'Legal Representative / CEO')
    if ceo_name != '':
        people_detail.append({
            'designation': 'Legal representative / CEO',
            'name': ceo_name
        })
    trade_capacity = get_next_sibling(soup, 'Trade Capacity')
    item['trade_capacity'] = trade_capacity if trade_capacity.replace('-', '').strip() != "" else ""
    production_capacity = get_next_sibling(soup, 'Production Capacity')
    item['production_capacity'] = production_capacity if production_capacity.replace('-', '').strip() != "" else ""
    item['r&d_capacity'] = get_next_sibling(soup, 'R&D Capacity')
    item['avg_lead_time'] = get_next_sibling(soup, 'Average Lead Time')
    item['year_exports_started'] = get_next_sibling(soup, 'Year Start Exporting')
    quality_control = get_next_sibling(soup, 'Quality Control')
    quality_control_total_staff = get_next_sibling(soup, 'No. of QC Staff')
    if quality_control != '' and quality_control_total_staff != '':
        additional_detail.append({
            'type': 'quality_control',
            'data': [{
                'quality_control': quality_control,
                'quality_control_total_staff': quality_control_total_staff
            }]
        })
    item['certificates'] = get_next_sibling(soup, 'Certificates')
    item['contract_manufacturing'] = get_next_sibling(soup, 'Contract Manufacturing')
    item['registered_capital'] = get_next_sibling(soup, 'Registered Capital')
    item['total_annual_sales_volume'] = get_next_sibling(soup, 'Total Annual Sales Volume')
    additional_detail.extend(get_main_product(soup))
    item['addresses_detail'] = addresses_detail
    item['contacts_detail'] = contacts_detail
    item['additional_detail'] = additional_detail
    item['people_detail'] = people_detail
    return item

try:
    start_url_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_url_num = int(sys.argv[2]) if len(sys.argv) > 2 else 3889

    df = pd.read_csv("company_urls.csv")
    for i, urls in enumerate(df.iterrows(), 1):

        if i < start_url_num:
            continue
        if i > end_url_num:
            break

        company_url = urls[1][0]
        print("Company url:", company_url)
        res = make_request(company_url)

        if res is not None:
            company_soup = BeautifulSoup(res.text, 'html.parser')
            OBJ = get_data(company_soup)
            OBJ =  srilanka_crawler.prepare_data_object(OBJ)
            ENTITY_ID = srilanka_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = srilanka_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            srilanka_crawler.insert_record(ROW)
            
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    srilanka_crawler.db_log(log_data)
    srilanka_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    srilanka_crawler.db_log(log_data)
