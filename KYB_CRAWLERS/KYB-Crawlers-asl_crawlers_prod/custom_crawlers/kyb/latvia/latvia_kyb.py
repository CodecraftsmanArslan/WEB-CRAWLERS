"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Latvijas Republikas Uzņēmumu reģistrs',
    'COUNTRY' : 'Latvia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ur.gov.lv/en/", 
                        "Source Description": "The Register of Enterprises of the Republic of Latvia registers companies, traders, their branches and representative offices and changes in their founding documents, and carries out other activities provided for in legislation."},
    'URL' : 'https://www.ur.gov.lv/en/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Latvia'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://www.ur.gov.lv'

latvia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  latvia_crawler.get_requests_helper()

def get_range():
    for i in range(1, 10000000000):
        yield f"{i:012d}"

def get_officers(id):
    people_detail = []
    url = f"https://info.ur.gov.lv/api/legalentity/api/{id}/persons/officers?lang=LV&fillForeignerData=true"
    response = request_helper.make_request(url)
    json_data = response.json()
    if 'records' in json_data:
        for record in json_data['records']:
            meta_detail = {
                "person_code": record.get('personCode'),
                "representation": record.get('representationTypeText'),
                "note": record.get('notes'),
            }
            people_detail.append({
                "name": record.get('fullname'),
                "designation": f"{record.get('officerInstitutionTypeText')} {record.get('positionText')}",
                "appointment_date": record.get('dateFrom'),
                "meta_detail": meta_detail
            })
    return people_detail

def get_members(id):
    people_detail = []
    url = f"https://info.ur.gov.lv/api/legalentity/api/{id}/persons/members?lang=LV&page=0&pageSize=5&fillForeignerData=true&printout=true"
    response = request_helper.make_request(url)
    json_data = response.json()
    if 'items' in json_data:
        for record in json_data['items']:
            meta_detail = {
                "share_%%": record.get('sharePercent'),
                "shares": record.get('value'),
                "nominal_value":f"{record.get('shareValue')} {record.get('currencyCode')}",
                "total": f"{record.get('shareCount')} {record.get('currencyCode')}",
                "note": record.get('notes'),
            }
            people_detail.append({
                "designation": 'member',
                "name": record.get('name'),
                "appointment_date": record.get('dateFrom'),
                "meta_detail": meta_detail
            })
    return people_detail

def get_beneficiaries(id):
    additional_detail = []
    beneficial_owner = []
    url = f"https://info.ur.gov.lv/api/legalentity/api/{id}/persons/beneficiaries?lang=LV&fillForeignerData=true"
    response = request_helper.make_request(url)
    json_data = response.json()
    if 'records' in json_data:
        for record in json_data['records']:
            beneficial_owner.append({
                "start_date": record.get('dateFrom'),
                "person_code": record.get('personCode'),
                "residency": record.get('residesCountryText'),
                "nationality": record.get('citizenCountryText')
            })
        additional_detail.append({
            "type": "beneficial_owner",
            "data":beneficial_owner
        })

    return additional_detail

def get_industries(reg_num):
    url = f"https://info.ur.gov.lv/api/legalentity/api/{reg_num}/paid-information?lang=LV"
    response = request_helper.make_request(url)
    json_data = response.json()
    if 'businessAreas' in json_data and 'workAreas' in json_data['businessAreas']:
        industries = json_data['businessAreas']['workAreas'].replace('\r\n', ' ') if json_data['businessAreas']['workAreas'] is not None else ""
        return industries
    return ""

def get_urls(keyword, page_number):
    urls = []
    url = f"https://www.ur.gov.lv//en/search-results/?search={keyword}&filter=1"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Length": "11",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "www.ur.gov.lv",
        "Origin": "https://www.ur.gov.lv",
        "Referer": "https://www.ur.gov.lv/en/search-results/?search=abcde&filter=1",
        "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Ur-Language": "en-US",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    json_data = {"page": page_number}
    response = request_helper.make_request(url, method="POST", headers=headers, json=json_data)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        anchor_tags = soup.find_all('a')
        for anchor_tag in anchor_tags:
            urls.append(anchor_tag.get('href'))
    return urls

def get_key_value_pair(soup):
    data = {}
    dt_elements = soup.find_all('dt')
    for dt in dt_elements:
        key = dt.text.strip(':').replace('\r\n', '').replace(':','').strip()
        dd = dt.find_next_sibling('dd')
        if dd:
            value = dd.text.strip()
            data[key] = value
    return data

def get_data(reg_num):
    item = {}
    people_detail = []
    addresses_detail = []
    fillings_detail = []
    additional_detail = []
    previous_names_detail = []
    response = request_helper.make_request(f"https://www.ur.gov.lv/en/legal-entity/?id={reg_num}")
    if response and response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        name_element = soup.find('div', class_="page-header-title")
        if name_element is None:
            return None
        item["name"] = name_element.find_next('h1').text.replace('\"', '')
        previous_name_element = soup.find('div', class_="page-header-sub-title")
        previous_name = previous_name_element.find_next('ul').text.replace("%", "%%") if previous_name_element is not None else ""
        previous_names_detail.append({
            "name": previous_name
        })
        data = get_key_value_pair(soup)
        addresses_detail.append({
            'type': 'general_address',
            'address': data.get('Address')
        })
        item["registration_number"] = data.get('Registration number')
        item["sepa_creditor_identifier"] = data.get('SEPA Creditor Identifier')
        item["registration_date"] = data.get('Registered on').replace('.', '-') if data.get('Registered on') is not None else ""
        item["removed_on"] = data.get('Removed on')
        item["type"] = data.get('Type')
        item["register"] = data.get('Register')
        item["declarations"] = data.get('Declarations')
        pledges_table_ele = soup.find('h2', string='Commercial pledges')
        pledges_table = pledges_table_ele.find_next('table')
        if pledges_table is not None:
            tbody = pledges_table.find('tbody')
            trs = tbody.find_all('tr')
            for tr in trs:
                ems = tr.find_all('em')
                meta_detail = {"renew_or_removal": ems[2].text}
                fillings_detail.append({
                    "filing_code": ems[0].text.replace("\n\r\n", "").replace("  ", "").replace("\r\n", "").replace("\n", ""),
                    "date": ems[1].text,
                    "meta_detail": meta_detail
                })
        reg_ = f"{str(reg_num)[1:-1].zfill(9)}"
        additional_detail.extend(get_beneficiaries(reg_))
        people_detail.extend(get_members(reg_))
        people_detail.extend(get_officers(reg_))
        item["industries"] = get_industries(reg_)
        item["previous_names_detail"] = previous_names_detail
        item["addresses_detail"] = addresses_detail
        item["fillings_detail"] = fillings_detail
        item["people_detail"] = people_detail
        item["additional_detail"] = additional_detail
        return item

try:
    # flag = True
    # start_char = sys.argv[1] if len(sys.argv) > 1 else "a"
    # characters = list(range(ord('a'), ord('z') + 1)) + list(range(ord('0'), ord('9') + 1))
    # for char in characters:
    #     if chr(char) != start_char and flag:
    #         continue
    #     else:
    #         flag = False
    #     page_number = 1
    #     while True:
    #         urls = get_urls(chr(char), page_number)
    #         if len(urls) == 0: break
    #         else: page_number += 1
    #         for url in urls:
    #             registration_number = url.split('=')[-1]
    #             print(f"Character: {chr(char)} Registration Number: {registration_number}")
    #             data = get_data(registration_number)
    #             if data is None: continue
    #             ENTITY_ID = latvia_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
    #             BIRTH_INCORPORATION_DATE = ''
    #             DATA = latvia_crawler.prepare_data_object(data)
    #             ROW = latvia_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
    #             latvia_crawler.insert_record(ROW)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for registration_number in range(start, 100000000000):
        print(f"Record No: {registration_number}")
        data = get_data(registration_number)
        if data is None: continue
        ENTITY_ID = latvia_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
        BIRTH_INCORPORATION_DATE = ''
        DATA = latvia_crawler.prepare_data_object(data)
        ROW = latvia_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
        latvia_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    latvia_crawler.db_log(log_data)
    latvia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    latvia_crawler.db_log(log_data)