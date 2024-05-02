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
from selenium.webdriver.support.ui import WebDriverWait
import ssl
from dateutil import parser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'International Registries, Inc',
    'COUNTRY': 'Marshall Islands',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://resources.register-iri.com/CorpEntity/Corporate/Search",
                      "Source Description": "International Registries, Inc. and its affiliates (IRI) provide administrative and technical support to the Republic of the Marshall Islands (RMI) Maritime and Corporate Registries. IRI has been administering maritime and corporate programs and involved in flag State administration since 1948."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://resources.register-iri.com/CorpEntity/Corporate/Search'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Marshall Islands Official Registry" 
}

marshal_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = marshal_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)
URL = "https://resources.register-iri.com/CorpEntity/Corporate/Search"

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def crawl():
    driver.get(URL)
    time.sleep(5)
    entity_name = driver.find_element(
        By.XPATH, '//td/input[@name="pt1:r1:0:it6"]')
    entity_name.send_keys("____")
    entity_type = driver.find_element(By.XPATH, '//td/select[@class="x2h"]')
    entity_type.click()
    time.sleep(3)
    all_types = [type.text.strip() for type in driver.find_elements(By.XPATH, '//td/select[@title="Choose"]/option')]
    for type in all_types[1:]:
        if len(ARGUMENT) > 2:
            type = all_types[int(ARGUMENT[2])]
        corporation = driver.find_element(
            By.XPATH, f'//td/select/option[@title="{type}"]')
        corporation.click()
        time.sleep(3)
        search_button = driver.find_element(By.XPATH, '//a/span[text()="Search"]')
        search_button.click()
        time.sleep(20)
        get_data(c_type=type)

def get_data(c_type):
    total_pages = driver.find_element(By.XPATH, '//tr/td[@class="x13f"]').text
    total_page_numbers = int(total_pages.split(" ")[-1])
    all_companies = int(len(driver.find_elements(By.XPATH, '//td/span/a')))

    if len(ARGUMENT) > 1:
        start_page_number = int(ARGUMENT[1])
    else:
        start_page_number = 1

    while start_page_number <= total_page_numbers:
        for i in range(all_companies):
            timeout = 60
            page_numb_box = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//td/input')))
            action.move_to_element(page_numb_box).double_click().send_keys(start_page_number).send_keys(Keys.RETURN).perform()
            time.sleep(3)
            company = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, '//td/span/a')))
            company[i].click()
            print(
                f'Scraping data of company ID: {company[i].text} on page number {start_page_number} of {c_type}')
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            registration_number = soup.find("label", string="Entity Number").parent.find_next_sibling().text.strip() if soup.find("label", string="Entity Number") is not None else ""
            entity_name = soup.find("label", string="Entity Name").parent.find_next_sibling().text.strip().replace("  ", "").replace("\n", " ") if soup.find("label", string="Entity Name") is not None else ""
            entity_type = soup.find("label", string="Entity Type").parent.find_next_sibling().text.strip() if soup.find("label", string="Entity Type") is not None else ""
            status_ = soup.find("label", string="Status").parent.find_next_sibling().text.strip() if soup.find("label", string="Status") is not None else ""
            incorporation_date = soup.find("label", string="Existence Date").parent.find_next_sibling().text.strip() if soup.find("label", string="Existence Date") is not None else ""
            incorporation_date = format_date(incorporation_date) if incorporation_date != "" else ""
            annulment_date = soup.find("label", string="Annulment Date").parent.find_next_sibling().text.strip() if soup.find("label", string="Annulment Date") is not None else ""
            annulment_date = format_date(annulment_date) if annulment_date != "" else ""
            dissolution_date = soup.find("label", string="Dissolved Date").parent.find_next_sibling().text.strip() if soup.find("label", string="Dissolved Date") is not None else ""
            dissolution_date = format_date(dissolution_date) if dissolution_date != "" else ""
            people_detail = []
            try:
                xdn = soup.find_all('div', class_="xdn")[1].get('style')
            except IndexError:
                xdn = ""
            if xdn == "display:none" or "display: none":
                pass
            else: 
                agent_name = soup.find("label", string="Name").parent.find_next_sibling().text.strip().replace("\n", " ").replace("  ", "") if soup.find("label", string="Name") is not None else ""
                agent_address = soup.find("label", string="Address").parent.find_next_sibling().text.strip().replace("\n", " ").replace("  ", "") if soup.find("label", string="Address") is not None else ""
                if agent_name != "":
                    dict = {
                            "designation": "registered_agent",
                            "name": agent_name.replace("%", "%%"),
                            "address": agent_address.replace("%", "%%")
                            }
                    people_detail.append(dict)

            OBJ = {
                    "registration_number": registration_number,
                    "name": entity_name.replace("%", "%%"),
                    "type": entity_type,
                    "status": status_,
                    "incorporation_date": incorporation_date,
                    "annulment_date": annulment_date,
                    "dissolution_date": dissolution_date,
                    "people_detail": people_detail
                }
            
            OBJ = marshal_crawler.prepare_data_object(OBJ)
            ENTITY_ID = marshal_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
            BIRTH_INCORPORATION_DATE = ''
            ROW = marshal_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
            marshal_crawler.insert_record(ROW)

            search_results = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//a/span[@class='x16z'][contains(text(), 'Search Results')]")))
            search_results.click()
            time.sleep(5)

        next_page = driver.find_element(By.XPATH, '//td/a[@title="Next Page"]').click()
        time.sleep(5)
        start_page_number += 1

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    marshal_crawler.db_log(log_data)
    marshal_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    marshal_crawler.db_log(log_data)