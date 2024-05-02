"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from datetime import datetime
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil import parser
from selenium.webdriver.support.ui import Select

meta_data = {
    'SOURCE' :'North Carolina Secretary of State, Business Registration Division',
    'COUNTRY' : 'North Carolina',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.sosnc.gov/online_services/search/by_title/_Annual_Report", 
                        "Source Description": "The Secretary of State for North Carolina is an elected state executive position in the North Carolina state government. The secretary is a member of the Council of State and the head of the Department of the State, which oversees economic and business-related operations of the state government. The department provides the initial infrastructure for corporate organizations, addresses fraud by providing accurate and timely information, and issues professional credentials."},
    'URL' : 'https://www.sosnc.gov/online_services/search/by_title/_Annual_Report',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'North Carolina'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

north_carolina_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  north_carolina_crawler.get_requests_helper()
selenium_helper =  north_carolina_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False)

def pdf_link(id):
    try:
        response = request_helper.make_request(url="https://www.sosnc.gov/online_services/imaging/download_ivault_pdf", method="POST", data= {'ID': id})
        data = response.json()
        if data['fileName'] != "":
            return f"https://www.sosnc.gov/online_services/imaging/download/{data['fileName']}"
    except:
        pass
    return ""

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def get_fillings(url):
    fillings_detail = []
    response = request_helper.make_request(url)
    if response is not None:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', 'FilingsTable')
        if table is not None:
            tbody = table.find('tbody')
            if tbody is not None:
                trs = tbody.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')
                    meta_detail = {'is_accepted': tds[1].text.strip()}
                    a_element = tds[0].find('a', class_='ImageLink')
                    if a_element:
                        report_id = a_element.get('id')
                        file_url = pdf_link(report_id)
                    else:
                        file_url = ''
                    fillings_detail.append({
                        'file_url': file_url,
                        'filing_type': tds[2].text.strip(),
                        'filing_code': tds[3].text.strip(),
                        'meta_detail': meta_detail,
                        'date': tds[4].text.strip().replace('/', '-') if len(tds) > 4 and tds[4] else '',
                    })
    return fillings_detail

def get_officers(soup):
    people_detail = []
    if soup:
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            a_element = paragraph.find('a')
            designation = paragraph.find('span', class_="greenLabel").text.strip()
            name = ' '.join(a_element.text.strip().split())
            id = a_element['onclick'].split("'")[1]
            address = paragraph.find('span', class_="greenLabel").find_next_sibling('span').get_text().strip()
            # meta_detail = {'profile_link': f"https://www.sosnc.gov/?id={id}"} if len(a_element['onclick'].split("'")) >=3 else {}
            people_detail.append({
                'designation': designation,
                'name': name,
                'address': str(' '.join(address.split())).replace(name, ''),
                # 'meta_detail': meta_detail
            })
    return people_detail

def find_section(soup, target_text):
    h2 = soup.find('h2', string=lambda text: text and target_text.lower() in text.lower())
    if h2:
        section = h2.find_parent('section')
        if section:
            return section
    return []

def get_prev_legal_name(soup, text):
    prev_legal_name = ''
    try:
        for span in soup.find_all('span'):
            if text in span.get_text(strip=True):
                prev_legal_name+= ' ' +span.find_next_sibling('span').text.strip().replace('\n', '').replace('  ', '')
    except:
        pass
    return prev_legal_name


def get_next_sibling(soup, text):
    try:
        for span in soup.find_all('span'):
            if text in span.get_text(strip=True):
                return span.find_next_sibling('span').text.strip().replace('\n', '').replace('  ', '')
    except:
        pass
    return ''

def get_data(soup, url):
    people_detail = []
    addresses_detail = []
    additional_detail = []
    fillings_detail = []
    previous_names_detail = []
    item = {}
    item['name'] = get_next_sibling(soup, "Legal Name")
    item['type'] = soup.find('h2', class_='section-title').text.strip() if soup.find('h2', class_='section-title') is not None else ''
    prev_legal_name = get_prev_legal_name(soup, "Prev Legal Name")
    prev_home_state_name = get_next_sibling(soup, "Prev Home State Name")
    if prev_legal_name != "":
        previous_names_detail.append({
            'name': prev_legal_name
        })
    if prev_home_state_name != "":
        previous_names_detail.append({
            'name': prev_home_state_name
        })
    item['registration_number'] = get_next_sibling(soup, "SosId:")
    item['status'] = get_next_sibling(soup, "Status:")
    item['incorporation_date'] = format_date(get_next_sibling(soup, "Date Formed:"))
    item['jurisdiction'] = get_next_sibling(soup, "State of Incorporation:")
    item['fiscal_month'] = get_next_sibling(soup, "Fiscal Month:")
    item['citizenship'] = get_next_sibling(soup, "Citizenship:")
    item['annual_report_due_date'] = get_next_sibling(soup, "Annual Report Due Date:")
    item['annual_report_status'] = get_next_sibling(soup, "Annual Report Status:")
    registered_agent = get_next_sibling(soup, "Registered Agent:")
    if registered_agent != "" and registered_agent != "Not Listed":
        people_detail.append({
            'designation': 'registered_agent',
            'name': registered_agent
        })
    item['aliases'] = get_next_sibling(soup, "Home State Name")
    mailing_address = get_next_sibling(soup, "Mailing")
    general_address = get_next_sibling(soup, "Principal Office")
    registered_address = get_next_sibling(soup, "Reg Office")
    registered_mailing_address = get_next_sibling(soup, "Reg Mailing")
    if mailing_address != "":
        addresses_detail.append({
            'type': 'mailing_address',
            'address': mailing_address.replace('\r', '')
        })
    if general_address != "":
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address.replace('\r', '')
        })
    if registered_address != "":
        addresses_detail.append({
            'type': 'registered_address',
            'address': registered_address.replace('\r', '')
        })
    if registered_mailing_address != "":
        addresses_detail.append({
            'type': 'registered_mailing_address',
            'address': registered_mailing_address.replace('\r', '')
        })
    officer_section = find_section(soup, 'Officers')
    if officer_section:
        people_detail.extend(get_officers(officer_section))
    stock_class = get_next_sibling(soup, "Class:")
    share = get_next_sibling(soup, "Shares:")
    par_value = get_next_sibling(soup, "Par Value")
    if stock_class != "" and stock_class is not None:
        additional_detail.append({
            'type': 'stock_info',
            'data':[{
                'class': stock_class,
                'share': share,
                'par_value': par_value
            }]
        })
    professions_span = find_section(soup, 'Professions')
    item['services'] = professions_span.find('ul').text.strip() if professions_span else ''
    company_official_section = find_section(soup, 'Company Officials')
    people_detail.extend(get_officers(company_official_section))
    if 'javascript:void(0)' not in url:
        fillings_detail.extend(get_fillings(url))
    item['additional_detail'] = additional_detail
    item['addresses_detail'] = addresses_detail
    item['people_detail'] = people_detail
    item['fillings_detail'] = fillings_detail
    item['previous_names_detail'] = previous_names_detail
    return item

try:
    url = "https://www.sosnc.gov/online_services/search/by_title/_Business_Registration"
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end_number = int(sys.argv[2]) if len(sys.argv) > 1 else 2999999
    for i in range(start_number, end_number):
        record_num = str(i).zfill(7)
        print(f"Record: {record_num}")
        driver.get(url)
        time.sleep(6)
        select_element = driver.find_element(By.ID, 'Words')
        select = Select(select_element)
        select.select_by_value('SOSID')
        search_box = driver.find_element(By.ID, 'SearchCriteria')
        search_box.send_keys(record_num)
        submit_btn = driver.find_element(By.ID, 'SubmitButton')
        submit_btn.click()
        wait = WebDriverWait(driver, 30)
        try:
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'double')))
        except:
            continue
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        anchor_element = tbody.find_element(By.TAG_NAME, 'a')
        data_action = anchor_element.get_attribute('data-action')
        action_div = tbody.find_element(By.CLASS_NAME, 'ActionDiv')
        report_btn = action_div.find_elements(By.TAG_NAME, 'a')[-1]
        filling_href = report_btn.get_attribute('href')
        response = request_helper.make_request(f"https://www.sosnc.gov/{data_action}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser') 
            data = get_data(soup, filling_href)
            ENTITY_ID = north_carolina_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
            BIRTH_INCORPORATION_DATE = ''
            DATA = north_carolina_crawler.prepare_data_object(data)
            ROW = north_carolina_crawler.prepare_row_for_db(ENTITY_ID, data.get('name').replace("%","%%"), BIRTH_INCORPORATION_DATE, DATA)
            north_carolina_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    north_carolina_crawler.db_log(log_data)
    north_carolina_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    north_carolina_crawler.db_log(log_data)
