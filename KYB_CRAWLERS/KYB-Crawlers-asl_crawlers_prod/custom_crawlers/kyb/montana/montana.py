"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import ssl
from dateutil import parser
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import undetected_chromedriver as uc
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

meta_data = {
    'SOURCE': 'Montana Secretary of State, Business Services Division',
    'COUNTRY': 'Montana',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://biz.sosmt.gov/search/business",
                      "Source Description": "The Division assists businesses with the filing of their registration, articles of organization, assumed business name, and trademarks. Additionally, the division is responsible for filing and maintaining records under the Uniformed Commercial Code (UCC)."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://biz.sosmt.gov/search/business'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Montana Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

ssl._create_default_https_context = ssl._create_unverified_context

all_alphabets = ["C", "A", "E", "D", "F", "R", "RN", "P"]

display = Display(visible=0,size=(800,600))
display.start()

start_alphabet = ARGUMENT[1].capitalize() if len(ARGUMENT) > 1 else all_alphabets[0]
start_number = int(ARGUMENT[2]) if len(ARGUMENT) > 2 else 1
proxy = ARGUMENT[3] if len(ARGUMENT) > 3 else "69.58.12.5:8010"
start_number = str(start_number).zfill(6)
end_number = 99999999

montana_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = montana_crawler.get_selenium_helper()
options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=http://{proxy}')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = uc.Chrome(version_main=114, options=options)
action = ActionChains(driver=driver)

driver.get("https://biz.sosmt.gov")
time.sleep(5)
search_button = driver.find_element(By.XPATH, '//span[text()="Search"]')
search_button.click()
time.sleep(5)

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def clear_search_field():
    search_field = driver.find_element(By.TAG_NAME, 'input')
    action.scroll_to_element(search_field).double_click(search_field).perform()
    search_field.send_keys(Keys.DELETE)
    
def crawl():
    for alphabet in all_alphabets:
        if alphabet != start_alphabet:
            continue
        for number in range(int(start_number), end_number):
            search_number = alphabet+str(number).zfill(6)
            search_field = driver.find_element(By.TAG_NAME, 'input')
            search_field.send_keys(search_number)
            search_field.send_keys(Keys.RETURN)
            time.sleep(5)
            if len(driver.find_elements(By.XPATH, '//div[@role="button"]')):
                print(f"Scraping data for: {search_number}...")
                company = driver.find_element(By.XPATH, '//div[@role="button"]')
                company.click()
                time.sleep(5)
                get_data(reg_no= search_number)
                clear_search_field()
            elif "An error" in driver.page_source:
                print("Too many requests Error.")
                driver.quit()
            else:
                print(f"No data for: {search_number}.")
                clear_search_field()

def get_data(reg_no):
    time.sleep(5)
    filing_details = []
    abns_data = []
    people_detail = []
    registration_number = reg_no
    soup = BeautifulSoup(driver.page_source, "html.parser")

    company_name = soup.find("div", class_="title-box").text.split(f"({reg_no})")[0].strip()
    company_type = soup.find("td", string="Entity Type") 
    company_type = company_type.find_next_sibling().text.strip() if company_type else ""
    company_sub_type = soup.find("td", string="Entity SubType")
    company_sub_type = company_sub_type.find_next_sibling().text.strip() if company_sub_type else ""
    company_status = soup.find("td", string="Status")
    company_status = company_status.find_next_sibling().text.strip() if company_status else ""
    jurisdiction = soup.find("td", string="Formed In")
    jurisdiction = jurisdiction.find_next_sibling().text.strip() if jurisdiction else ""
    previous_name = soup.find("td", string="Previous Entity Names")
    previous_name = previous_name.find_next_sibling().text.strip() if previous_name else ""
    description = soup.find("td", string="Reinstatement")
    description = description.find_next_sibling().text.strip() if description else ""
    managed_by = soup.find("td", string="Managed By")
    managed_by = managed_by.find_next_sibling().text.strip() if managed_by else ""

    qualification_date = soup.find("td", string="Qualification Date")
    if qualification_date:
        qualification_date = qualification_date.find_next_sibling().text.strip()
        qualification_date = format_date(qualification_date)
    else:
        qualification_date = ""
    expiration_date = soup.find("td", string="Expiration Date")
    if expiration_date:
        expiration_date = expiration_date.find_next_sibling().text.strip()
        expiration_date = format_date(expiration_date)
    else:
        expiration_date = ""
    jur_reg_date = soup.find("td", string="Date Registered In State/Country of Jurisdiction")
    if jur_reg_date:
        jur_reg_date = jur_reg_date.find_next_sibling().text.strip()
        jur_reg_date = format_date(jur_reg_date)
    else:
        jur_reg_date = ""
    principal_address = soup.find("td", string="Principal Address")
    principal_address = principal_address.find_next_sibling().text.strip().replace("N/A", "") if principal_address else ""
    mailing_address = soup.find("td", string="Mailing Address")
    mailing_address = mailing_address.find_next_sibling().text.strip().replace("N/A", "") if mailing_address else ""
    physical_jur_address = soup.find("td", string="Business Physical Address of Office Required to be Maintained in State of Formation")
    physical_jur_address = physical_jur_address.find_next_sibling().text.strip().replace("N/A", "") if physical_jur_address else ""
    mailing_jur_address = soup.find("td", string="Business Mailing Address of Office Required to be Maintained in State of Formation")
    mailing_jur_address = mailing_jur_address.find_next_sibling().text.strip().replace("N/A", "") if mailing_jur_address else ""
    registration_date = soup.find("td", string="Registration Date")
    if registration_date:
        registration_date = registration_date.find_next_sibling().text.strip().replace("N/A", "")
        registration_date = format_date(registration_date)
    else:
        registration_date = ""
    inactive_date = soup.find("td", string="Inactive Date")
    if inactive_date:
        inactive_date = inactive_date.find_next_sibling().text.strip().replace("N/A", "")
        inactive_date = format_date(inactive_date)
    else:
        inactive_date = ""
    ar_due_date = soup.find("td", string="AR Due Date")
    if ar_due_date:
        ar_due_date = ar_due_date.find_next_sibling().text.strip().replace("N/A", "")
        ar_due_date = format_date(ar_due_date)
    else:
        ar_due_date = ""
    
    agent_detail = soup.find("td", string="Registered Agent")
    if agent_detail == None:
        agent_detail = soup.find("td", string="Commercial Registered Agent")
        
    agent_detail = agent_detail.find_next_sibling().text.strip().replace("N/A", "").split("\n") if agent_detail else ""
    agent_type = agent_detail[0] if agent_detail else ""
    agent_code = agent_detail[1] if agent_detail else ""
    agent_name = agent_detail[2]if agent_detail else ""
    agent_address = (agent_detail[3] + ", " + agent_detail[4]) if agent_detail else ""
    agent_dict = {
                "designation": "registered_agent",
                "meta_detail": {
                    "type_of_agent": agent_type,
                    "agent_code": agent_code,
                },
                "name": agent_name,
                "address": agent_address
            }
    if agent_detail:
        people_detail.append(agent_dict)

    if len(driver.find_elements(By.XPATH, '//td[text()="Active ABNs & TMs"]/parent::tr/following-sibling::tr/td//li')) > 0:
        active_abns_data = driver.find_elements(By.XPATH, '//td[text()="Active ABNs & TMs"]/parent::tr/following-sibling::tr/td//li')
        for active_item in active_abns_data:
            active_url = active_item.find_element(By.TAG_NAME, "a").get_attribute("href")
            active_title = active_item.find_element(By.TAG_NAME, "a").text.strip()
            abn_dict = {
                "title": active_title,
                "url": active_url
            }
            abns_data.append(abn_dict)
    
    if len(driver.find_elements(By.XPATH, '//td[text()="Inactive ABNs & TMs"]/parent::tr/following-sibling::tr/td//li')) > 0:
        inactive_abns_data = driver.find_elements(By.XPATH, '//td[text()="Inactive ABNs & TMs"]/parent::tr/following-sibling::tr/td//li')
        for inactive_item in inactive_abns_data:
            inactive_url = inactive_item.find_element(By.TAG_NAME, "a").get_attribute("href")
            inactive_title = inactive_item.find_element(By.TAG_NAME, "a").text.strip()
            tm_dict = {
                "title": inactive_title,
                "url": inactive_url
            }
            abns_data.append(abn_dict)

    if len(driver.find_elements(By.XPATH, '//button[@aria-label="View History"]')) > 0:
        history_button = driver.find_element(By.XPATH, '//button[@aria-label="View History"]')
        action.scroll_to_element(history_button).move_to_element(history_button).click().perform()
        time.sleep(5)
        all_filings = driver.find_elements(By.XPATH, '//button[@class="title collapsed"]')
        if len(driver.find_elements(By.XPATH, '//button[@class="title collapsed"]')) > 0:
            expand_all_button = driver.find_element(By.XPATH, '//button[text()="Expand All"]')
            expand_all_button.click()
        time.sleep(5)
        filing_soup = BeautifulSoup(driver.page_source, "html.parser")
        if len(all_filings) > 0:
            for i in range(len(all_filings)):
                filing_title = filing_soup.find_all("label", string="Amendment Type")[i]
                filing_title = filing_title.find_next_sibling().text.strip().replace("- ", "") if filing_title else ""
                filing_number = filing_soup.find_all("label", string="Document Number")[i]
                filing_number = filing_number.find_next_sibling().text.strip() if filing_number else ""
                filing_date = filing_soup.find_all("label", string="Date")[i]
                if filing_date:
                    filing_date = filing_date.find_next_sibling().text.strip().replace("N/A", "")
                    filing_date = format_date(filing_date)
                else:
                    filing_date = ""
                delayed_effective_date = filing_soup.find_all("label", string="Delayed Effective Date")[i]
                if delayed_effective_date:
                    delayed_effective_date = delayed_effective_date.find_next_sibling().text.strip().replace("N/A", "")
                    delayed_effective_date = format_date(delayed_effective_date)
                else:
                    delayed_effective_date = ""
                filing_main_div = filing_soup.find("div", class_="amendment-drawer")
                filing_table = filing_main_div.find("div", class_="table-wrapper").find("table") if filing_main_div.find("div", class_="table-wrapper") else ""
                if filing_table:
                    filing_rows = filing_table.find_all("tr")
                    for filing_row in filing_rows[1:]:
                        filing_data = filing_row.find_all("td")
                        field_name = filing_data[0].text.strip()
                        changed_from = format_date(filing_data[1].text.split(" ")[0].strip())
                        changed_to = format_date(filing_data[2].text.split(" ")[0].strip())
                        filing_dict = {
                            "title": filing_title,
                            "date": filing_date,
                            "filing_type": filing_title,
                            "filing_code": filing_number,
                            "meta_detail": {
                                "delayed_effective_date": delayed_effective_date,
                                "field": field_name,
                                "changed_from": changed_from,
                                "changed_to": changed_to
                            }
                        }
                        filing_details.append(filing_dict)
                else:
                    filing_dict = {
                        "title": filing_title,
                        "date": filing_date,
                        "filing_type": filing_title,
                        "filing_code": filing_number,
                        "meta_detail": {
                            "delayed_effective_date": delayed_effective_date
                        }
                    }
                    filing_details.append(filing_dict)
                
        close_button = driver.find_elements(By.XPATH, '//button[@aria-label="Close"]')[1]
        close_button.click()
        time.sleep(3)

    OBJ = {
        "name": company_name,
        "registration_number": registration_number,
        "subtype": company_sub_type,
        "status": company_status,
        "jurisdiction": jurisdiction,
        "addresses_detail": [
            {
                "type": "general_address",
                "address": principal_address.replace("\n", ", ")
            },
            {
                "type": "mailing_address",
                "address": mailing_address.replace("\n", ", ")
            },
            {
                "type": "physical_jurisdiction_address",
                "address": physical_jur_address.replace("\n", ", ")
            },
            {
                "type": "mailing_jurisdiction_address",
                "address": mailing_jur_address.replace("\n", ", ")
            }
        ],
        "registration_date": registration_date,
        "registered_in_jurisdiction_date": jur_reg_date,
        "fillings_detail": filing_details,
        "inactive_date": inactive_date,
        "annual_return_due_date": ar_due_date,
        "description": description,
        "previous_name_detail": [
            {
                "name": previous_name
            }
        ],
        "expiry_date": expiration_date,
        "people_detail": people_detail,
        "qualified_date": qualification_date,
        "managed_by": managed_by,
        "additional_detail": [
            {
                "type": "active/inactive_abn_and_tm",
                "data": abns_data
            }
        ]
    }

    if previous_name == "":
        del OBJ["previous_name_detail"]

    OBJ = montana_crawler.prepare_data_object(OBJ)
    ENTITY_ID = montana_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = montana_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    montana_crawler.insert_record(ROW)   


try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    montana_crawler.db_log(log_data)
    montana_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    montana_crawler.db_log(log_data)
    display.stop()
