"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

meta_data = {
    'SOURCE' :'Istanbul Chamber of Commerce (ICOC)',
    'COUNTRY' : 'Turkey',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://bilgibankasi.ito.org.tr/en/data-bank/company-details", 
                        "Source Description": "Istanbul Chamber of Commerce (ICOC) operates with the vision of increasing its members' share in international trade, guiding them through global economic developments, and contributing to the rise of Turkey as a regional power. ICOC is aware of its crucial role regarding the need to respond to the structural and current issues faced by the private sector, enhance Turkey''s international trade power, and provide a safe and stable development environment for the national economy."},
    'URL' : 'https://bilgibankasi.ito.org.tr/en/data-bank/company-details',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Turkey Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://bilgibankasi.ito.org.tr/en/data-bank/company-details'

turkey_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  turkey_crawler.get_selenium_helper()

def key_value_pair(table_row):
    item = {}
    for row in table_row:
        divs = row.find_all('div')
        item[divs[0].text] = divs[1].text
    return item

def find_table(soup, keyword):
    div = soup.find('div', string=keyword)
    if div:
        sibling_div = div.find_next_sibling('div')
        tables = sibling_div.find_all('table')
        if len(tables) >= 2:
            return tables[1]
    return None

def get_partners(soup):
    people_detail = []
    table = find_table(soup, 'Partners')
    if table is not None is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            meta_detail = {'capital': tds[3].text} if tds[3] and tds[3].text != '' else {}
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'partner',
                'meta_detail': meta_detail
            })
    return people_detail

def get_former_partners(soup):
    people_detail = []
    table = find_table(soup, 'Former Partners')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            meta_detail = {'capital': tds[3].text} if tds[3] and tds[3].text != '' else {}
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'former_partner',
                'meta_detail': meta_detail
            })
    return people_detail

def get_authorized_persons(soup):
    people_detail = []
    table = find_table(soup, 'Authorised Persons')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'authorized_person',
                'termination_date': tds[3].text if tds[3].text != '/0/0/0' else ''
            })
    return people_detail

def get_member_of_board(soup):
    people_detail = []
    table = find_table(soup, 'Member of Board')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            meta_detail = {'capital': tds[3].text} if tds[3] and tds[3].text != '' else {}
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'board_member',
                'meta_detail': meta_detail
            })
    return people_detail

def get_former_members_of_board(soup):
    people_detail = []
    table = find_table(soup, 'Former Members of Board')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            meta_detail = {'capital': tds[3].text} if tds[3] and tds[3].text != '' else {}
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'former_board_member',
                'meta_detail': meta_detail
            })
    return people_detail

def get_former_authorized_persons(soup):
    people_detail = []
    table = find_table(soup, 'Former Authorised Persons')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            people_detail.append({
                'name': f"{tds[0].text} {tds[1].text}",
                'designation': tds[2].text if tds[2] and tds[2].text != '' else 'former_athorized_person',
                'termination_date': tds[3].text if tds[3].text != '0/0/0' else ''
            })
    return people_detail

def get_former_company_title(soup):
    previous_name_details = []
    table = find_table(soup, 'Former Company Title')
    if table is not None:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            # meta_detail = {'number': tds[0].text} if tds[0] and tds[0].text != '' else {}
            previous_name_details.append({
                'name': f"{tds[1].text} {tds[1].text}",
                # 'meta_detail': meta_detail
            })
    return previous_name_details

def get_data(soup):
    item = {}
    additional_detail = []
    addresses_detail = []
    contact_detail = []
    previous_name_details = []
    people_detail = []
    company_details_div = soup.find('div', class_='company-details-page')
    table_row = company_details_div.find_all('div', class_='table-row')
    data = key_value_pair(table_row)
    item['status'] = data.get('Status')
    item['registration_number'] = data.get('Register No')
    item['chamber_registration_number'] = data.get('Chamber Registration No')
    item['central_registration_system_number'] = data.get('Central Registration System No')
    item['name'] = data.get('Company Title')
    general_address = data.get('Business Address')
    if general_address != "":
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address
        })
    phone_number = data.get('Phone Number')
    if phone_number != "":
        contact_detail.append({
            'type': 'phone_number',
            'value': phone_number
        })
    fax_number = data.get('Fax Number')
    if fax_number != "":
        contact_detail.append({
            'type': 'fax_number',
            'value': fax_number
        })
    webpage = data.get('Webpage')
    if webpage != "":
        contact_detail.append({
            'type': 'webpage',
            'value': webpage
        })
    item['registration_date'] = data.get('Date of Registration').replace('/', '-') if data.get('Date of Registration') else ''
    item['main_contract_registry_date'] = data.get('Registry Date of the Main Contract').replace('/', '-') if data.get('Registry Date of the Main Contract') else ''
    item['tax_id_available'] = data.get('Tax Number')
    item['capital'] = data.get('Capital')
    item['industries'] = data.get('Occupational Group')
    nace_code = data.get('Nace Code').split('-') if data.get('Nace Code') and '-' in data.get('Nace Code') else ''
    if len(nace_code) == 2:
        additional_detail.append({
            'type': 'nace_code',
            'data': [{
                'code': nace_code[0],
                'description': nace_code[1]
            }]
        })
    
    people_detail.extend(get_partners(company_details_div))
    people_detail.extend(get_former_partners(company_details_div))
    people_detail.extend(get_authorized_persons(company_details_div))
    people_detail.extend(get_member_of_board(company_details_div))
    people_detail.extend(get_former_members_of_board(company_details_div))
    people_detail.extend(get_former_authorized_persons(company_details_div))
    previous_name_details.extend(get_former_company_title(company_details_div))
    item['additional_detail'] = additional_detail
    item['addresses_detail'] = addresses_detail
    item['contacts_detail'] = contact_detail
    item['previous_names_detail'] = previous_name_details
    item['people_detail'] = people_detail
    return item

try:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for registration_number in range(start, 999999):
        for retry in range(3):
            driver = selenium_helper.create_driver(headless=True, Nopecha=False)
            try:
                print(f"Record No: {registration_number}")
                wait = WebDriverWait(driver, 30)
                driver.get(BASE_URL)
                input_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="k-content"]//input')))
                input_box.clear()
                input_box.send_keys(registration_number)
                submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="k-content"]//button')))
                submit_btn.click()
                table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'k-grid-table')))
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                trs = tbody.find_elements(By.TAG_NAME, 'tr')
                for i in range(len(trs)):
                    table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'k-grid-table')))
                    tbody = table.find_element(By.TAG_NAME, 'tbody')
                    trs = tbody.find_elements(By.TAG_NAME, 'tr')
                    if len(trs) == 1:
                        break
                    trs[i].click()
                    time.sleep(3)
                    company_details_page = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'company-details-page')))
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    data = get_data(soup)
                    if data is not None and data.get('name') is not None and data.get('registration_number') is not None:
                        ENTITY_ID = turkey_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
                        BIRTH_INCORPORATION_DATE = ''
                        DATA = turkey_crawler.prepare_data_object(data)
                        ROW = turkey_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
                        turkey_crawler.insert_record(ROW)
                    back_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'back-link')))
                    back_btn.click()
                break
            except (TimeoutException, ElementClickInterceptedException) as e:
                driver.quit()
                print(f'Timeout occurred {retry+1} retry again in 10 seconds.')
                time.sleep(10)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    turkey_crawler.db_log(log_data)
    turkey_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    turkey_crawler.db_log(log_data)
