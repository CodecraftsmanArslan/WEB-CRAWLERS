"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'Companies Office for the Province of Manitoba',
    'COUNTRY': 'Manitoba',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "http://companiesoffice.gov.mb.ca/listings.html",
                      "Source Description": "Official website of the Companies Office of Manitoba, which is a government agency responsible for maintaining records related to corporations and business names in Manitoba, Canada. The website provides a variety of resources and services for businesses operating in Manitoba, including information on how to incorporate a business, register a business name, and file various business documents."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'http://companiesoffice.gov.mb.ca/listings.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Manitoba Official Registry" 
}

manitoba_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = manitoba_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=1000)
URL = "https://web22.gov.mb.ca/Sso/Account/LogOn?lang=en-CA"

username = "AimenAbid"
password = "@User12345"

driver.get(URL)
time.sleep(5)
print("Website Opened")

def crawl():
    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys(username)
    time.sleep(1)
    print("Username Entered")
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(password)
    print("Password Enetered")
    time.sleep(1)
    submit_button = driver.find_element(By.TAG_NAME, "button")
    submit_button.click()
    print("Logging in...")
    time.sleep(3)
    access_button = driver.find_element(By.XPATH, '//a[text()="Companies Online"]')
    access_button.click()
    time.sleep(2)
    try:
        main_menu_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Main Menu"]')))
        main_menu_button.click()
        time.sleep(2)
    except NoSuchElementException:
        main_menu_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Main Menu"]')))
        main_menu_button.click()
        time.sleep(2)
    search_entity_button = driver.find_element(By.XPATH, '//span[text()="Search by Name/Number"]')
    search_entity_button.click()
    time.sleep(2)
    print("Opening Search Page...")
    search_field = driver.find_element(By.ID, 'txtRegNm')
    search_field.send_keys("1")
    search_button = driver.find_element(By.ID, 'cmdSearch')
    print("Loading results...")
    search_button.click()
    time.sleep(5)
    get_data()

def get_data():
    print("Scraping data...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all("table")[1]
    all_rows = table.find_all("tr")
    for row in all_rows[1:]:
        data = row.find_all("td")
        name = data[0].text
        registration_number = data[1].text
        status_ = data[2].text
        complience_status = data[3].text
        type_ = data[4].text
        jurisdiction = data[5].text
        current_name = data[6].text
        if current_name and current_name != name:
            previous_name = name
        else:
            previous_name = ""
        expiry_date = data[8].text.replace("/", "-") if data[8] else ""

        OBJ = {
            "name": name,
            "registration_number": registration_number,
            "status": status_,
            "compliance_status": complience_status,
            "type": type_,
            "jurisdiction": jurisdiction,
            "current_name": current_name,
            "expiry_date": expiry_date,
            "previous_names_detail": [
                {
                    "name": previous_name
                }
            ]
        }

        if previous_name == "":
            del OBJ["previous_names_detail"]

        OBJ = manitoba_crawler.prepare_data_object(OBJ)
        ENTITY_ID = manitoba_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
        ROW = manitoba_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
        manitoba_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    manitoba_crawler.db_log(log_data)
    manitoba_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    manitoba_crawler.db_log(log_data)