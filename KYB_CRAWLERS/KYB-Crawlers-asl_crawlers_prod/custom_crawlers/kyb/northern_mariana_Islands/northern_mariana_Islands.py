"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import random, requests
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Commonwealth of the Northern Mariana Islands (CNMI) - Saipan Chamber of Commerce',
    'COUNTRY' : 'Northern Mariana Islands',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://business.saipanchamber.com/list/search?sa=true", 
                        "Source Description": "The Saipan Chamber of Commerce is a non-profit organisation whose mission is to empower our enterprises as a resource, advocate, and connector for Saipan''s private sector."},
    'URL' : 'https://business.saipanchamber.com/list/search?sa=true',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Northern Mariana Islands'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

north_mariana_isl_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  north_mariana_isl_crawler.get_requests_helper()

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

try:
    base_url = "https://business.saipanchamber.com/list/searchalpha/_?q=_&o=&"
    response = make_request(base_url) 
    STATUS_CODE = response.status_code
    DATA_SIZE = len(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    href_tags = soup.select("#gzns .card-header a")
    urls = [a['href'] for a in href_tags if 'href' in a.attrs]
    for url in urls:
        item = {}
        addresses_detail = []
        contact_detail = []
        people_detail = []
        res = make_request(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        NAME = soup.find('h1', class_='fl-heading').text.strip().replace('%', '%%')
        item['name'] = NAME

        category_div = soup.find('div', class_='gz-details-categories')
        if category_div:
            p_elements = category_div.find_all('p')
            category_text = ', '.join(p.get_text(strip=True) for p in p_elements)
            item['category'] = category_text

        address_li = soup.find('li', class_='gz-card-address')
        if address_li:
            address_spans = address_li.find_all('span')
            address = ' '.join(span.get_text(strip=True) for span in address_spans)
            addresses_detail.append({
                'type': 'general_address',
                'address': address,
            })
        phone_numnber = soup.find('li', class_='gz-card-phone')
        if phone_numnber is not None:
            contact_detail.append({
                'type': 'phone_number',
                'value': phone_numnber.text.strip()
            })
        fax_number = soup.find('li', class_='gz-card-fax')
        if fax_number is not None:
            contact_detail.append({
                'type': 'fax_number',
                'value': fax_number.text.strip()
            })
        website_element = soup.find('li', class_='gz-card-website')
        website = website_element.find('a')['href'] if website_element and website_element.find('a') else None
        if website is not None:
            contact_detail.append({
                'type': 'website',
                'value': website
            })
        social_media_ele = soup.find('li', class_='gz-card-social')
        social_media_hrefs = social_media_ele.find_all('a') if social_media_ele else []
        for index, social_href in enumerate(social_media_hrefs):
            contact_detail.append({
                'type': f'social_media_{index+1}',
                'value': social_href['href']
            })
        item['working_hours'] = soup.find('div', class_='gz-details-hours').text.replace('Hours:', '').replace('\n', '').strip() if soup.find('div', class_='gz-details-hours') else ''
        item['driving_directions'] = soup.find('div', class_='gz-details-driving').text.replace('Driving Directions:', '').replace('\n', '').strip() if soup.find('div', class_='gz-details-driving') else ''
        item['about_us'] = soup.find('div', class_='gz-details-about').text.replace('About Us', '').replace('\n', ' ').strip() if soup.find('div', class_='gz-details-about') else ''
        iframe = soup.find('div', class_='gz-details-video').find('iframe') if soup.find('div', class_='gz-details-video') else None
        if iframe:
            item['url'] = iframe['src']
        ul_element = soup.find('ul', class_='gz-highlights-list')
        if ul_element:
            li_elements = ul_element.find_all('li')
            item['activity'] = ', '.join(li.get_text(strip=True) for li in li_elements)
        map_element = soup.find('div', class_='gz-map').find('iframe') if soup.find('div', class_='gz-map') else None
        if map_element:
            item['pin_location'] = map_element['src']

        contact_elements = soup.find_all('div', class_='gz-rep-card')
        for contact_ele in contact_elements:
            cell_phone_element = contact_ele.find('span', string='Phone:')
            cell_phone = cell_phone_element.find_next_sibling('span').text.strip() if cell_phone_element else ''
            phone_number_element = contact_ele.find('span', string='Cell Phone:')
            phone_number = phone_number_element.find_next_sibling('span').text.strip() if phone_number_element else ''
            contact_person_name = contact_ele.find('div', class_='gz-member-repname').text.strip() if contact_ele.find('div', class_='gz-member-repname') else ''
            if contact_person_name != '':
                meta_detail = {'mobile_number': cell_phone} if cell_phone != '' else {}
                people_detail.append({
                    'name': contact_person_name,
                    'designation': contact_ele.find('div', class_='gz-member-reptitle').text.strip() if contact_ele.find('div', class_='gz-member-reptitle') else '',
                    'phone_number': phone_number,
                    # 'fax': '',
                    'meta_detail': meta_detail,
                    'postal_address': contact_ele.find('a', class_='gz-rep-card-add').text.strip().replace('\n', ' ') if contact_ele.find('a', class_='gz-rep-card-add') else ''
                })
        item['registration_number'] = ''
        item['people_detail'] = people_detail
        item['contacts_detail'] = contact_detail
        item['addresses_detail'] = addresses_detail
        ENTITY_ID = north_mariana_isl_crawler.generate_entity_id(company_name=NAME, reg_number='')
        BIRTH_INCORPORATION_DATE = ''
        DATA = north_mariana_isl_crawler.prepare_data_object(item)
        ROW = north_mariana_isl_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
        north_mariana_isl_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    north_mariana_isl_crawler.db_log(log_data)
    north_mariana_isl_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    north_mariana_isl_crawler.db_log(log_data)
