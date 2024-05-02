"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import ssl
from dateutil import parser
from pyvirtualdisplay import Display

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'New Mexico Secretary of State Business Services Division',
    'COUNTRY': 'New Mexico',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch",
                      "Source Description": "Official online portal for the New Mexico Secretary of State Business Services Division that provides information related to entities registered in New Mexico."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "New Mexico PS Official Registry" 
}

new_mexico_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

selenium_helper = new_mexico_crawler.get_selenium_helper()
request_helper = new_mexico_crawler.get_requests_helper()

response = request_helper.make_request("https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/username/direct/-/")
data = response.text
lines = data.strip().split('\n')
proxy_list = [line.replace('\r', '') for line in lines]
start_page = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 1

for i in range(10, len(proxy_list)):
    try:
        URL = "https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch"
        driver = selenium_helper.create_driver(headless=False, Nopecha=True, timeout=300, proxy=True, proxy_server=proxy_list[i])
        action = ActionChains(driver=driver)
        driver.get(URL)
        time.sleep(5)
        search_field = driver.find_element(By.XPATH, '//input[@id = "txtBusinessName"]')
        print("Website Opened!")
        break
    except:
        pass

def crawl():
    driver.get(URL)
    time.sleep(5)
    print("Website Opened!")
    find_solve_captcha()
    search_field = driver.find_element(By.XPATH, '//input[@id = "txtBusinessName"]')
    search_field.send_keys("*")
    time.sleep(1)
    search_button = driver.find_element(By.XPATH, '//input[@value="Search"]')
    search_button.click()
    time.sleep(5)
    skip_pages()
    total_pages = int(driver.find_elements(By.XPATH, '//li[@class="pageinfo"]')[1].text.split(":")[-1].split("of")[-1].strip())
    for i in range(start_page, total_pages):
        print(f"Scraping page number: {i}")
        no_of_companies = len(driver.find_elements(By.XPATH, '//table[@id = "xhtml_grid_PartnershipBusinesses"]//tr/td/a'))
        for number in range(no_of_companies):
            all_companies = driver.find_elements(By.XPATH, '//table[@id = "xhtml_grid_PartnershipBusinesses"]//tr/td/a')
            if all_companies[number].text:
                action.scroll_to_element(all_companies[number]).move_to_element(all_companies[number]).click().perform()
                print(f"Scraping data for partnership number {number + 1}")
                get_partnership_data()
                back_button = driver.find_element(By.XPATH, '//input[@value="Back"]')
                action.scroll_to_element(back_button).move_to_element(back_button).click().perform()
                time.sleep(3)
        time.sleep(5)
        page_field_ = driver.find_elements(By.ID, 'txtCommonPageNo')[1]
        action.scroll_to_element(page_field_).perform()
        page_field_.send_keys(i+1)
        time.sleep(2)
        page_field_.send_keys(Keys.RETURN)
        time.sleep(10)


def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def find_solve_captcha():
    try:
        captcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
        if captcha_element:
            print("Captcha Found!")
            selenium_helper.wait_for_captcha_to_be_solved(driver)
        time.sleep(5)
    except:
        print("No captcha found!")

def skip_pages():
    if len(ARGUMENT) > 1:
        print(f"Skipping to page number: {ARGUMENT[1]}...")
        page_field = driver.find_elements(By.ID, 'txtCommonPageNo')[1]
        action.scroll_to_element(page_field).perform()
        page_field.send_keys(ARGUMENT[1])
        time.sleep(2)
        page_field.send_keys(Keys.RETURN)
        time.sleep(2)
        print(f"{int(ARGUMENT[1]) - 1} pages skipped!")
    time.sleep(3)

def get_partnership_data():
    time.sleep(2)
    try:
        expand_all = driver.find_elements(By.XPATH, '//div[@style="float: right;"]')
        for item in expand_all:
            action.scroll_to_element(item).move_to_element(item).click().perform()
            time.sleep(0.2)
        time.sleep(2)
    except:
        print("Nothing to expand")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    people_detail = []
    additional_detail = []
    fillings_detail = []
    previous_names_detail = []

    # Entity Details
    registration_number = soup.find("td", string="Registration #:")
    registration_number = registration_number.find_next_sibling().text.strip() if registration_number else ""
    status_ = soup.find("td", string="Status:")
    status_ = status_.find_next_sibling().text.strip() if status_ else ""
    entity_name = soup.find("td", string=re.compile("Entity  Name:"))
    entity_name = entity_name.find_next_sibling().text.strip().replace("\"", "") if entity_name else ""
    period_of_duration = soup.find("td", string=re.compile("Period of Duration:"))
    period_of_duration = period_of_duration.find_next_sibling().text.strip() if period_of_duration else ""
    reg_date_nm = soup.find("td", string=re.compile("Registration  Date in NM:"))
    if reg_date_nm:
        reg_date_nm = reg_date_nm.find_next_sibling().text.strip()
        reg_date_nm = format_date(reg_date_nm)
    else:
        reg_date_nm = ""
    entity_type = soup.find("td", string=re.compile("Entity Type:"))
    entity_type = entity_type.find_next_sibling().text.strip() if entity_type else ""

    #Contact Information
    designated_office_address = soup.find("td", string=re.compile("Designated Office Address:"))
    designated_office_address = designated_office_address.find_next_sibling().text.strip().replace("NONE", "") if designated_office_address else ""
    mailing_address = soup.find("td", string=re.compile("Mailing Address:"))
    mailing_address = mailing_address.find_next_sibling().text.strip().replace("NONE", "") if mailing_address else ""
    email_address = soup.find("td", string=re.compile("Email Address:"))
    email_address = email_address.find_next_sibling().text.strip().replace("NONE", "") if email_address else ""
    phone_number = soup.find("td", string=re.compile("Phone:"))
    phone_number = phone_number.find_next_sibling().text.strip().replace("NONE", "") if phone_number else ""

    # Chief Executive Office Information
    ceo_physical_address = soup.find("td", string=re.compile("Physical Address:"))
    ceo_physical_address = ceo_physical_address.find_next_sibling().text.strip().replace("NONE", "") if ceo_physical_address else ""
    ceo_mailing_address = soup.find_all("td", string=re.compile("Mailing Address:"))[1]
    ceo_mailing_address = ceo_mailing_address.find_next_sibling().text.strip().replace("NONE", "") if ceo_mailing_address else ""
    ceo_dict = {
        "designation": "ceo",
        "address": ceo_physical_address,
        "postal_address": ceo_mailing_address
    }
    if ceo_physical_address or ceo_mailing_address:
        people_detail.append(ceo_dict)

    # Registered Agent Information
    agent_name = soup.find("td", string="Name:")
    agent_name = agent_name.find_next_sibling().text.strip().replace("NONE", "") if agent_name else ""
    agent_physical_address = soup.find_all("td", string="Physical Address:")[1]
    agent_physical_address = agent_physical_address.find_next_sibling().text.strip().replace("NONE", "") if agent_physical_address else ""
    agent_mailing_address = soup.find_all("td", string="Mailing Address:")[2]
    agent_mailing_address = agent_mailing_address.find_next_sibling().text.strip().replace("NONE", "") if agent_mailing_address else ""
    agent_dict = {
        "designation": "registered_agent",
        "name": agent_name,
        "address": agent_physical_address,
        "postal_address": agent_mailing_address
    }
    if agent_name or agent_physical_address or agent_mailing_address:
        people_detail.append(agent_dict)

    # General Partner Information
    gp_table = soup.find_all("table", id="xhtml_grid_genpartnerlist")[0]
    if gp_table:
        all_gp_rows = gp_table.find_all("tr")
        for gp_row in all_gp_rows[1:]:
            all_gp_data = gp_row.find_all("td")
            gp_name = all_gp_data[0].text
            if gp_name == "No records to view.":
                continue
            gp_physical_address = all_gp_data[1].text
            gp_mailing_address = all_gp_data[2].text
            gp_dict = {
                "designation": "partner",
                "name": gp_name,
                "address": gp_physical_address,
                "postal_address": gp_mailing_address.replace("NONE", "")
            }
            people_detail.append(gp_dict)

    # Memo
    memo_table = soup.find_all("table", id="xhtml_grid_genpartnerlist")[1]
    if memo_table:
        all_memo_rows = memo_table.find_all("tr")
        for memo_row in all_memo_rows[1:]:
            all_memo_data = memo_row.find_all("td")
            memo_name = all_memo_data[0].text
            if memo_name == "No records to view.":
                continue
            memo_physical_address = all_memo_data[1].text
            memo_mailing_address = all_memo_data[2].text
            memo_dict = {
                "type": "memo_information",
                "data":[
                    {
                    "name": memo_name,
                    "address": memo_physical_address,
                    "postal_address": memo_mailing_address.replace("NONE", "")
                    }
                ]
            }
            additional_detail.append(memo_dict)

    # Filing History
    filing_table = soup.find("table", id="PartnershipFilingHistory")
    if filing_table:
        all_filing_rows = filing_table.find_all("tr")
        for filing_row in all_filing_rows[1:]:
            all_filing_data = filing_row.find_all("td")
            filing_code = all_filing_data[0].text
            if filing_code == "No records to view.":
                continue
            filing_type = all_filing_data[1].text
            filing_date = all_filing_data[2].text
            filing_view_filing = all_filing_data[3].text.replace("\xa0\xa0\xa0\xa0\xa0N/A", "").replace("N/A", "")
            filing_last_reporting_year = all_filing_data[4].text
            filing_dict = {
                "filing_code": filing_code,
                "filing_type": filing_type,
                "date": format_date(filing_date),
                "meta_detail": {
                    "view_filing": filing_view_filing,
                    "last_reporting_year": filing_last_reporting_year.replace("0", "")
                }
            }
            fillings_detail.append(filing_dict)

    # Name History
    name_table = soup.find("table", id="tablegrid")
    if name_table:
        all_name_rows = name_table.find_all("tr")
        for name_row in all_name_rows[1:]:
            all_name_data = name_row.find_all("td")
            name_filing_code = all_name_data[0].text
            if name_filing_code == "No records to view.":
                continue
            name_filing_date = all_name_data[1].text
            name_name_changed = all_name_data[2].text
            name_dict = {
                "filing_code": name_filing_code,
                "name": name_name_changed,
                "meta_detail": {
                    "filing_date": format_date(name_filing_date)
                }
            }
            previous_names_detail.append(name_dict)

    OBJ = {
        "registration_number": registration_number,
        "status": status_,
        "name": entity_name,
        "duration": period_of_duration,
        "registration_date": reg_date_nm,
        "type": entity_type,
        "addresses_detail": [
            {
                "type": "office_address",
                "address": designated_office_address
            },
            {
                "type": "mailing_address",
                "address": mailing_address
            }
        ],
        "contacts_detail": [
            {
                "type": "email",
                "value": email_address
            },
            {
                "type": "phone_number",
                "value": phone_number
            }
        ],
        "people_detail": people_detail,
        "additional_detail": additional_detail,
        "fillings_detail": fillings_detail,
        "previous_names_detail": previous_names_detail
    }

    OBJ = new_mexico_crawler.prepare_data_object(OBJ)
    ENTITY_ID = new_mexico_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = new_mexico_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    new_mexico_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    new_mexico_crawler.db_log(log_data)
    new_mexico_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    new_mexico_crawler.db_log(log_data)
    display.stop()