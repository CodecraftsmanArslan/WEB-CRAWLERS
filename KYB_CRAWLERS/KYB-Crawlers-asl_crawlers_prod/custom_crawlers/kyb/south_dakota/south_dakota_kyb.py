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
from dateutil import parser
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'South Dakota Secretary of State, Business Services Division',
    'COUNTRY' : 'South Dakota',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://sosenterprise.sd.gov/BusinessServices/Business/FilingSearch.aspx", 
                        "Source Description": "The South Dakota Secretary of State (SD SOS) is responsible for a wide range of duties, including business filings, corporations, trademarks, campaign finance reports and lobbyist registration. The South Dakota Secretary of State Business Services Division is the chief elections officer of South Dakota, and is responsible for overseeing all federal, state, and local election activity in South Dakota."},
    'URL' : 'https://sosenterprise.sd.gov/BusinessServices/Business/FilingSearch.aspx',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'South Dakota'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

display = Display(visible=0,size=(800,600))
display.start()
south_dakota_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  south_dakota_crawler.get_requests_helper()
selenium_helper =  south_dakota_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=True)

def wait_for_captcha_to_be_solved(browser):
        time.sleep(3)
        if len(browser.find_elements(By.XPATH, '//iframe[@title="reCAPTCHA"]')) > 0:
            while True:
                try:
                    iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                    browser.switch_to.frame(iframe_element)
                    wait = WebDriverWait(browser, 10000)
                    print('trying to resolve captcha')
                    wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
                    print("Captcha has been Solved")
                    # Switch back to the default content
                    browser.switch_to.default_content()
                    return browser
                except:
                    print('captcha solution timeout error, retrying...')    

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def get_sibling(keyword, soup):
    try:
        return soup.find("span", string=keyword).parent.find_next_sibling().find_next_sibling().text.strip()
    except:
        return ""
    
def get_span(soup, id):
    try:
        span = soup.find('span', {'id': id})
        if span:
            return span.text
        else:
            return ""
    except:
        return ""

def get_history(soup):
    fillings_detail = []
    div_element = soup.find('div', 'ctl00_MainContent_divHistorySummary')
    if div_element is not None:
        table = div_element.find('table')
        if table is not None:
            trs = table.find_all('tr')
            for tr in trs:
                tds = tr.find('td')
                a_tag = tds[2].find('a')
                file_url = a_tag['href'] if a_tag is not None else ''
                filing_code = a_tag.text if a_tag is not None else ''
                fillings_detail.append({
                    'filing_type': tds[0].text,
                    'title': tds[0].text,
                    'date': format_date(tds[1].text),
                    'filing_code': filing_code,
                    'file_url': file_url,
                    'description': tds[3].text
                })
    return fillings_detail

def get_data(main_page, soup):
    item = {}
    people_detail = []
    addresses_detail = []
    additional_detail = []
    previous_names_detail = []
    item['registration_number'] = get_span(soup, 'ctl00_MainContent_txtBusinessID')
    item['name'] = get_span(soup, 'ctl00_MainContent_txtName')
    item['type'] = get_span(soup, 'ctl00_MainContent_txtSubType')
    item['status'] = get_span(soup, 'ctl00_MainContent_txtStatus')
    item['jurisdiction'] = get_span(soup, 'ctl00_MainContent_txtFormation')
    term_of_duration = get_span(soup, 'ctl00_MainContent_txtDuration') # Expires - 04/12/2035
    status_will = term_of_duration.split('-')[0] if '-' in term_of_duration and len(term_of_duration.split('-')) >= 2 else term_of_duration
    additional_detail.append({
        'type': 'term_of_duration',
        'data': [{
            'status_will': status_will,
            'date': format_date(term_of_duration.split('-')[-1]) if '-' in term_of_duration and len(term_of_duration.split('-')) >= 2 else ''
        }]
    })
    item['initial_filing_date'] = format_date(get_span(soup, 'ctl00_MainContent_txtInitialDate'))
    item['inactive_date'] = format_date(get_span(soup, 'ctl00_MainContent_txtInactiveDate'))
    general_address = get_span(soup, 'ctl00_MainContent_txtOfficeAddresss')
    if general_address != "":
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address
        })
    item['shares'] = get_span(soup, 'ctl00_MainContent_txtOptional1')
    agent_name = get_span(soup, 'ctl00_MainContent_lblAgentName')
    agent_address = get_span(soup, 'ctl00_MainContent_txtAgentAddress')
    agent_mailing_address = get_span(soup, 'ctl00_MainContent_txtAgentAddressMail')
    people_detail.append({
        'designation': 'registered_agent',
        'name': agent_name.replace('NO AGENT', ''),
        'address': agent_address,
        'postal_address': agent_mailing_address
    })
    item['people_detail'] = people_detail
    item['fillings_detail'] = get_history(soup)
    main_soup = main_page.find('div', class_='ctl00_MainContent_SearchResultList')
    if main_soup is not None:
        table = main_soup.find('table')
        if table is not None:
            tr = table.find('tr', class_='odd')
            tds = tr.find_all('td')
            item['name_type'] = tds[3].text
    item['aliases'] = get_span('ctl00_MainContent_txtForeignName', soup)
    previous_name = get_span('ctl00_MainContent_lblOldName', soup)
    if previous_name != "":
        previous_names_detail.append({
            "mame": previous_name
        })
    item['series'] = get_span('ctl00_MainContent_txtSeriesMessage', soup)
    item['delayed_effective_date'] = format_date(get_span('ctl00_MainContent_lblDelayedDate', soup))
    item['next_annual_report_due'] = get_span('ctl00_MainContent_lblARDueDate', soup)
    mailing_address = get_span('ctl00_MainContent_lblMailAddress', soup)
    if mailing_address != "":
        addresses_detail.append({
            'type': 'mailing_address',
            'address': mailing_address
        })
    item['managed_by'] = get_span('ctl00_MainContent_lblOptional1', soup)
    item['expiry_date'] = format_date(get_span('ctl00_MainContent_lblExpirationDate', soup))
    owner_name = get_sibling('Owner Name:', soup)
    if owner_name != "":
        people_detail.append({
            'designation': 'owner',
            'name': owner_name,
            'address': get_sibling('Physical Address:', soup),
            'postal_address': get_sibling('Mailing Address:', soup)
        }) 

    item['people_detail'] = people_detail
    item['addresses_detail'] = addresses_detail
    return item

try:
    url = "https://sosenterprise.sd.gov/BusinessServices/Business/FilingSearch.aspx"
    start_prefix = str(sys.argv[1]) if len(sys.argv) > 1 else "BK"
    start_number = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    prefixes = ["BK", "DL", "DB", "CH", "CI", "CO", "RG", "UB", "FB", "NS", "FL", "FK", "FT", "RN"]
    start_index = prefixes.index(start_prefix)
    for i in range(start_index, len(prefixes)):
        prefix = prefixes[i]
        for num in range(start_number, 1000000):
            num_str = str(num).zfill(6)
            print(f"Record No: {prefix}{num_str}")
            driver.get(url)
            search_box = driver.find_element(By.ID, 'ctl00_MainContent_txtFilingId')
            search_box.clear()
            search_box.send_keys(f"{prefix}{num_str}")
            submit_btn = driver.find_element(By.ID,'ctl00_MainContent_SearchButton')
            wait_for_captcha_to_be_solved(driver)
            submit_btn.click()
            main_page_soup = BeautifulSoup(driver.page_source, 'html.parser')
            business_element = driver.find_elements(By.CLASS_NAME, 'MenuNav')
            if len(business_element) == 0:
                continue
            business_element[0].click()
            detail_button = driver.find_elements(By.ID, 'ctl00_MainContent_btnViewDetail')
            if len(detail_button) > 0:
                wait_for_captcha_to_be_solved(driver)
                detail_button[0].click()
            soup = BeautifulSoup(driver.page_source, "html.parser")
            data = get_data(main_page_soup, soup)
            ENTITY_ID = south_dakota_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
            BIRTH_INCORPORATION_DATE = ''
            DATA = south_dakota_crawler.prepare_data_object(data)
            ROW = south_dakota_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
            south_dakota_crawler.insert_record(ROW)
            start_number = 0        

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    south_dakota_crawler.db_log(log_data)
    south_dakota_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    south_dakota_crawler.db_log(log_data)
display.stop()