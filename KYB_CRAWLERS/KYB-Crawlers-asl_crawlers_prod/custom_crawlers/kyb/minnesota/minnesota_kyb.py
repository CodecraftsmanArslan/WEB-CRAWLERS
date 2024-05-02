"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Minnesota Secretary of State',
    'COUNTRY' : 'Minnesota',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://mblsportal.sos.state.mn.us/Business/BusinessSearch?BusinessName=%%2A&IncludePriorNames=False&Status=Active&Type=Contains", 
                        "Source Description": "The Minnesota Secretary of State is the governmental office tasked with overseeing business registration and related services in the state. Their responsibilities include verifying the availability of business names, accepting and processing articles of incorporation or organization, maintaining a database of registered businesses, and ensuring compliance with state laws and regulations regarding business formation and operation."},
    'URL' : 'https://mblsportal.sos.state.mn.us/Business/BusinessSearch?BusinessName=%%2A&IncludePriorNames=False&Status=Active&Type=Contains',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Minnesota'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://mblsportal.sos.state.mn.us'

minnesota_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  minnesota_crawler.get_requests_helper()

def get_range():
    for i in range(0, 1000000):
        yield i

    for i in range(1, 10000000000):
        yield f"{i:012d}"

def find_table(soup,keyword):
    th_element = soup.find('th', string=lambda text: keyword in text if text is not None else "")
    if th_element:
        return th_element.find_parent('table')

def get_urls(file_number):
    urls = []
    url = f"https://mblsportal.sos.state.mn.us/Business/BusinessSearch?FileNumber={file_number}&IncludePriorNames=False&Status=Active&Type=Contains"
    response = request_helper.make_request(url)
    if response is not None and response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='selectable')
        if table is not None:
            anchor_tags = table.find_all('a')
            for anchor_tag in anchor_tags:
                urls.append(anchor_tag.get('href'))
    return urls

def get_key_value_pair(soup):
    key_value_pair = {}
    dls = soup.find_all('dl')
    for dl in dls:
        key_value_pair[dl.find('dt').text] = dl.find('dd').text
    return key_value_pair

def get_fillings_detail(soup):
    fillings_detail = []
    th_elements = soup.find_all('th', string=lambda text: 'Filing Date' in text if text is not None else "")
    for element in th_elements:
        table = element.find_parent('table')
        if table is not None:
            trs = table.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) == 4:
                    date = tds[1].text.replace('/', '-').strip() if tds[1].text is not None else ""
                    title = tds[2].text.strip()
                    effective_date = tds[3].text.replace('/', '-').strip() if len(tds) > 3 and tds[3].text is not None else ""
                    meta_detail = {'effective_date': effective_date} if effective_date != "" else {}
                    fillings_detail.append({
                        'title': title,
                        'date': date,
                        'meta_detail': meta_detail
                    })
                elif len(tds) == 2:
                    date = tds[0].text.replace('/', '-').strip() if tds[0].text is not None else ""
                    title = tds[1].text.strip()
                    fillings_detail.append({
                        'title': title,
                        'date': date,
                    })
    return fillings_detail

def get_markholder(soup):
    additional_detail = []
    table = find_table(soup, 'Markholder')   
    if table is not None:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) == 2:
                additional_detail.append({
                    'type': 'markholder_information',
                    'data': [{
                        'name': tds[0].text.strip(),
                        'address': tds[1].text.strip().replace('  ', '').replace('\r\n', ' ')
                    }]
                })
    return additional_detail

def get_data(url):
    item = {}
    people_detail = []
    addresses_detail = []
    fillings_detail = []
    additional_detail = []
    response = request_helper.make_request(f"{BASE_URL}{url}")
    if response is not None and response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data = get_key_value_pair(soup)
        spans = soup.find_all('span', class_='navbar-brand')
        item["name"] = spans[1].text.replace("%", "%%") if len(spans) > 1 and spans[1].text is not None else ""
        item["type"] = data.get('Business Type', '')
        item["governing_law"] = data.get('MN Statute', '')
        item["registration_number"] = data.get('File Number', '')
        item["jurisdiction"] = data.get('Home Jurisdiction', '')
        item["registration_date"] = data.get('Filing Date', '').replace("/", "-")
        item["status"] = data.get('Status', '')
        item["renewal_due_date"] = data.get('Renewal Due Date', '').replace('/', '-')
        item["mark_type"] = data.get('Mark Type', '')
        office_address = data.get('Registered Office Address', '')
        if office_address != "":
            addresses_detail.append({
                "type": "office_address",
                "address": office_address
            })
        registered_agent_name = data.get('Registered Agent(s)', '')
        if registered_agent_name != "" and registered_agent_name.strip() != "(Optional) Currently No Agent":
            people_detail.append({
                'designation': 'registered_agent',
                'name': registered_agent_name
            })
        principal_address = data.get('Principal Executive Office Address', '')
        if principal_address != "":
            addresses_detail.append({
                'type': 'executive_office_address',
                'address': principal_address
            })
        manager_td_element = soup.find('dt', string='Manager')
        if manager_td_element:
            people_detail.append({
                'designation': 'manager',
                'name': manager_td_element.find_next('dd').get_text(),
                'address': manager_td_element.find_next('address').get_text()
            })
        fillings_detail.extend(get_fillings_detail(soup))
        additional_detail.extend(get_markholder(soup))
        item["people_detail"] = people_detail
        item["addresses_detail"] = addresses_detail
        item["fillings_detail"] = fillings_detail
        item["additional_detail"] = additional_detail
        return item
        

if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 0

try:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1   
    for file_number in range(start, 9999999999999):
        print("File number:", file_number)
        urls = get_urls(file_number)
        for url in urls:
            data = get_data(url)
            if data is None: continue
            ENTITY_ID = minnesota_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
            BIRTH_INCORPORATION_DATE = ''
            DATA = minnesota_crawler.prepare_data_object(data)
            ROW = minnesota_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
            minnesota_crawler.insert_record(ROW)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    minnesota_crawler.db_log(log_data)
    minnesota_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    minnesota_crawler.db_log(log_data)
