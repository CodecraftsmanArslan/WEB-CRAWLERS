"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc 
from pyvirtualdisplay import Display

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Illinois Secretary of State',
    'COUNTRY' : 'Illinois',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://apps.ilsos.gov/businessentitysearch/", 
                        "Source Description": "The Department of Business Services Database includes information regarding corporations, not-for-profit corporations, limited partnerships, limited liability companies and limited liability partnerships, as well as, other business-related information."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://apps.ilsos.gov/businessentitysearch/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Illinois",
}

display = Display(visible=0,size=(800,600))
display.start()
illinois_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  illinois_crawler.get_selenium_helper()

# options = uc.ChromeOptions()
# options.add_argument('--proxy-server=http://93.120.32.49:9233')
driver = uc.Chrome(version_main = 114) 

def identify_recaptcha(driver):
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    if len(iframes) > 0:
        time.sleep(50)

def identify_recaptcha(driver):
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    if len(iframes) > 0:
        selenium_helper.wait_for_captcha_to_be_solved(driver)


def set_ranges(prefix, start):
    prefixes = ['S']

    if prefix == 1:
        zeros_to_ = range(start, 1000000)
        numbers = range(1, 99999999)
    else:
        zeros_to_ = range(1000000, 1000000)
        numbers = range(start, 99999999)
    
    for number in zeros_to_:
        yield f"{prefixes[0]}{number:06d}"
    
    for number in numbers:
        yield str(number).zfill(6)


def extract_info(soup, label):
    element = soup.find('b', string=label)
    if element:
        next_div = element.find_next('div')
        if next_div and next_div is not None:
            return next_div.text.strip().replace("  ", "").replace("\r\n", "").replace("\t", "")
    return ""


def get_record_data(driver):
    result = {}
    people_detail = []
    previous_names_detail = []
    fillings_detail = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    result["name"] = extract_info(soup, "Entity Name")
    result["registration_number"] = extract_info(soup, "File Number")
    result["status"] = extract_info(soup, "Status")
    result["type"] = extract_info(soup, "Entity Type")
    result["corporation_type"] = extract_info(soup, "Type of Corp")
    result["incorporation_date"] = extract_info(soup, "Org. Date/Admission Date")
    if result["incorporation_date"] == "":
        result["incorporation_date"] = extract_info(soup, "Incorporation Date")
    result["jurisdiction"] = extract_info(soup, "State")
    if result["jurisdiction"] == "":
        result["jurisdiction"] = extract_info(soup, "Jurisdiction")
    result["duration_date"] = extract_info(soup, "Duration Date")
    result["duration"] = extract_info(soup, "Duration")
    agent_information = soup.find('b', string="Agent Information")
    if agent_information is not None:
        agent_information = agent_information.find_next('div')
        agent_change_date = extract_info(soup, "Agent Change Date")
        address_parts = [str(item) for item in agent_information.contents[1:]]
        people_detail.append({
            "designation": "registered_agent",
            "name": agent_information.contents[0].strip(),
            "address": ' '.join(address_parts).strip().replace("<br/>", "").replace("  ",""),
            "appointment_date": agent_change_date
        })
    filing_date = extract_info(soup, "Filing Date")
    for_year = extract_info(soup, "For Year")

    if filing_date != "" or for_year != "":
        fillings_detail.append({
            "title": "annual_report",
            "date": filing_date,
            "year": for_year
        })

    officers_div = soup.find("div", {"id": "officers"})
    if officers_div is not None:
        officers_table = officers_div.find('table')
        if officers_table is not None:
            officers_tbody = officers_table.find('tbody')
            rows = officers_tbody.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if ',' in tds[1].text:
                    name, address = tds[1].text.split(',', 1)
                else:
                    name = tds[1].text
                    address = ''
                previous_names_detail.append({
                    "designation": tds[0].text.strip(),
                    "name": name.strip(),
                    "address": address.strip()
                })

    manager_table = soup.find("table", {"id": "sortManagers"})
    if manager_table is not None:
        tbody = manager_table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            people_detail.append({
                "designation": "manager",
                "name": tds[0].text.strip(),
                "address": tds[1].text.strip()
            })

    file_history_table = soup.find("table", {"id": "fileHistory"})
    if file_history_table is not None:
        tbody = file_history_table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            people_detail.append({
                "filing_type": tds[0].text.strip(),
                "date": tds[1].text.strip,
                "file_url": ""
            })

    assumed_names_table = soup.find("table", {"id": "sortAssumed"})
    if assumed_names_table is not None:
        tbody = assumed_names_table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) > 1:
                previous_names_detail.append({
                    "name": tds[1].text.strip(),
                    "meta_detail": {
                        "status": tds[0].text.strip(),
                    }
                })

    old_llc_name_table = soup.find("table", {"id": "sortOldLlcNames"})
    if old_llc_name_table is not None:
        tbody = old_llc_name_table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            previous_names_detail.append({
                "update_date": tds[0].text.strip(),
                "name": tds[1].text.strip(),
            })

    old_corp_name_div = soup.find("div", {"id": "oldCorpName"})
    if old_corp_name_div is not None:
        old_corp_name_table = old_corp_name_div.find('table')
        if old_corp_name_table is not None:
            old_corp_name_tbody = old_corp_name_table.find('tbody')
            rows = old_corp_name_tbody.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                previous_names_detail.append({
                    "name": tds[1].text.strip(),
                    "meta_detail": {
                        "date": tds[0].text.strip(),
                    }
                })
    
    result["people_detail"] = people_detail
    result["previous_names_detail"] = previous_names_detail
    result["fillings_detail"] = fillings_detail

    return result

def search_records(search_value, driver):
    radio_buttons = driver.find_elements(By.CLASS_NAME, "radio-inline")
    if len(radio_buttons) > 3:
        time.sleep(1)
        radio_buttons[3].click()
        search_box = driver.find_element(By.ID, "searchValue")
        search_box.clear()
        search_box.send_keys(search_value)
        time.sleep(2)
        search_box.submit()
        identify_recaptcha(driver)
        return True
    else:
        return False

try:   
    url = "https://apps.ilsos.gov/businessentitysearch/"
    start_value = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    prefix = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    for search_value in set_ranges(prefix, start_value):
        driver.get(url)
        search_method = "f"
        print("Note: for re-run crawler please pass first argument is <Record No> and second argument is prefix(0,1)")
        print(f"Record No: {search_value}")
        res = search_records(search_value, driver)
        if res:
            href_elements = driver.find_elements(By.CSS_SELECTOR, "td a")
            for i in range(len(href_elements)):
                href_elements = driver.find_elements(By.CSS_SELECTOR, "td a")
                href_elements[i].click()
                time.sleep(2)
                data = get_record_data(driver)
                if data.get("registration_number") == "" and data.get("name") == "":
                    time.sleep(60)
                    continue
                ENTITY_ID = illinois_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
                BIRTH_INCORPORATION_DATE = ''
                DATA = illinois_crawler.prepare_data_object(data)
                ROW = illinois_crawler.prepare_row_for_db(ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
                illinois_crawler.insert_record(ROW)
                driver.back()
        time.sleep(10)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    illinois_crawler.db_log(log_data)
    illinois_crawler.end_crawler()
    display.stop()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    illinois_crawler.db_log(log_data)
    display.stop()
