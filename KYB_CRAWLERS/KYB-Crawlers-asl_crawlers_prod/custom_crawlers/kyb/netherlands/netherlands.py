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

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'Kamer van Koophandel (Chamber of Commerce)',
    'COUNTRY': 'Netherlands',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.kvk.nl/zoeken/handelsregister/",
                      "Source Description": "The Kamer van Koophandel is the Chamber of Commerce in the Netherlands. The KVK's main statutory tasks are to operate the official national Business Register and provide businesses with information and advice."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.kvk.nl/zoeken/handelsregister/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Netherlands Official Registry" 
}

netherlands_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = netherlands_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)
url = "https://www.kvk.nl/zoeken/handelsregister/"

start_number = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 0
end_number = 99999999

def crawl():
    driver.get(url=url)
    time.sleep(2)
    if len(driver.find_elements(By.ID, 'cookie-consent')) > 0:
        continue_button = driver.find_element(By.XPATH, '//button[text()="Keuze opslaan"]')
        continue_button.click()
    for i in range(start_number, end_number):
        search_query = str(i).zfill(8)
        search_field = driver.find_element(By.ID, 'kvknummer')
        action.scroll_to_element(search_field).move_to_element(search_field).double_click().double_click().perform()
        search_field.send_keys(Keys.DELETE)
        time.sleep(1)
        search_field.send_keys(search_query)
        time.sleep(1)
        check_expired_trade = driver.find_element(By.XPATH, '//input[@name="zoekvervallen"]').get_attribute("id").split("-")[-1]
        if check_expired_trade == "0":
            expired_name_box = driver.find_element(By.XPATH, '//span[text()="Vervallen handelsnamen"]')
            expired_name_box.click()
            time.sleep(1)
        search_button = driver.find_element(By.ID, 'zoeken-button')
        action.scroll_to_element(search_button).perform()
        time.sleep(1)
        search_button.click()
        time.sleep(5)
        result_text = driver.find_element(By.XPATH, '//div[@class="feedback"]').text.strip()
        if result_text == "0 resultaten met filter Handelsregister":
            print(f"No record found for: {search_query}")
            continue
        else:
            get_data(registration_num = search_query)
            driver.back()
            time.sleep(2)

def get_data(registration_num):
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    name_ = soup.find("h3", class_="handelsnaamHeader").text.strip()
    details_url = "https://www.kvk.nl" + soup.find("a", string=name_).get("href")

    all_existing_trade_names  = []
    if len(soup.find_all("h5", string="Bestaande handelsnamen")) > 0:
        existing_trade_names = [name.strip() for name in soup.find("h5", string="Bestaande handelsnamen").find_next_sibling().text.split("|")]
        for existing_name in existing_trade_names:
            existing_dict = {
                "name": existing_name
            }
            all_existing_trade_names.append(existing_dict)

    all_expired_trade_names = []
    if len(soup.find_all("h5", string="Vervallen handelsnamen")) > 0:
        expired_trade_names = [name.strip() for name in soup.find("h5", string="Vervallen handelsnamen").find_next_sibling().text.split("|")]
        for expired_name in expired_trade_names:
            expired_dict = {
                "name": expired_name
            }
            all_expired_trade_names.append(expired_dict)

    if len(soup.find_all("h5", string="Statutaire naam")) > 0:
        statutory_name = soup.find("h5", string="Statutaire naam").find_next_sibling().text.strip()
    else:
        statutory_name = ""

    if len(soup.find_all("h5", string="Naam samenwerkingsverband")) > 0:
        partnership_name = soup.find("h5", string="Naam samenwerkingsverband").find_next_sibling().text.strip()
    else:
        partnership_name = ""

    location_number = soup.find("ul", class_="kvk-meta").text.split("Vestigingsnr.")[-1].split(" ")[1].strip()
    address = soup.find("ul", class_="kvk-meta").text.split(location_number)[1].strip()
    description = soup.find(class_="snippet-result").text.strip()

    driver.get(details_url)
    time.sleep(5)
    if len(driver.find_elements(By.XPATH, '//div[@class="info show"]')) > 0:
        show_details = driver.find_element(By.XPATH, '//div[@class="info show"]')
        if len(show_details.find_elements(By.TAG_NAME, "a")) > 0:
            company_url = show_details.find_element(By.TAG_NAME, "a").get_attribute("href")
        else:
            company_url = ""
    else:
        company_url = ""

    if company_url == driver.current_url + "#":
        company_url = ""
    
    if len(driver.find_elements(By.XPATH, '//p[text()="Status:"]')) > 0:
        status_ = driver.find_element(By.XPATH, '//p[text()="Status:"]/following-sibling::p').text
    else:
        status_ = ""

    OBJ = {
        "name": name_,
        "registration_number": registration_num,
        "location_number": location_number,
        "addresses_detail": [
            {
                "type": "general_address",
                "address": address
            }
        ],
        "website_url": company_url,
        "description": description,
        "previous_names_detail": all_expired_trade_names,
        "status": status_,
        "aliases": statutory_name,
        "additional_detail": [
            {
                "type": "existing_names",
                "data": all_existing_trade_names
            },
            {
                "type": "partnership_name",
                "data": [
                    {
                        "name": partnership_name
                    }
                ]
            }
        ]
    }

    if OBJ["additional_detail"][1]["data"][0]["name"] == "":
        del OBJ["additional_detail"][1]

    OBJ = netherlands_crawler.prepare_data_object(OBJ)
    ENTITY_ID = netherlands_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = netherlands_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    netherlands_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    netherlands_crawler.db_log(log_data)
    netherlands_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    netherlands_crawler.db_log(log_data)
