"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
arguments = sys.argv


meta_data = {
    'SOURCE': 'Chamber of Commerce Cayman Islands',
    'COUNTRY': 'Cayman Island',
    'CATEGORY': 'Official Chamber',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://web.caymanchamber.ky/allcategories",
                      "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://web.caymanchamber.ky/allcategories'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Cayman Island Official Chamber",
}

cayman_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = cayman_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, timeout=300)
start_category = int(sys.argv[1]) if len(sys.argv) > 1 else 25

def get_data(category):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    name = soup.find("span", {"itemprop": "name"}).text
    print(f"Scrapping company name: {name}")
    registration_number = soup.find("span", {"itemprop": "street-address"}).next_sibling.next_sibling.text.split("  ")[-1].strip()
    territory = soup.find("span", {"itemprop": "street-address"}).next_sibling.next_sibling.text.replace(registration_number, "").strip()
    jurisdiction = soup.find("span", {"itemprop": "locality"}).text
    description = driver.find_element(By.ID, 'ListingDetails_Level_DESCRIPTION').text.replace("\n", ", ").strip().replace("%", "%%")

    try:
        starting_year = driver.find_element(By.XPATH, '//div[@class = "ListingDetails_Level2_MEMBERSINCE"]').text.split(":")[-1].strip()
    except NoSuchElementException:
        starting_year = driver.find_element(By.XPATH, '//div[@class = "ListingDetails_Level1_MEMBERSINCE"]').text.split(":")[-1].strip()

    try:
        phone_number = driver.find_element(By.XPATH, '//span[@class = "ListingDetails_Level2_MAINCONTACT"]').text.strip().split("|")[0]
    except NoSuchElementException:
        phone_number = driver.find_element(By.XPATH, '//span[@class = "ListingDetails_Level1_MAINCONTACT"]').text.strip().split("|")[0]

    if len(driver.find_elements(By.XPATH, '//span[@class = "ListingDetails_Level2_MAINCONTACT"]')) > 0:
        fax_number = driver.find_element(By.XPATH, '//span[@class = "ListingDetails_Level2_MAINCONTACT"]').text
        fax_number = fax_number.strip().split("|")[1].replace("fax:", "").strip() if '|' in fax_number else ""
    elif len(driver.find_elements(By.XPATH, '//span[@class = "ListingDetails_Level1_MAINCONTACT"]')) > 0:
        fax_number = driver.find_element(By.XPATH, '//span[@class = "ListingDetails_Level1_MAINCONTACT"]').text
        fax_number = fax_number.strip().split("|")[1].replace("fax:", "").strip() if '|' in fax_number else ""
    else:
        fax_number = ""

    try:
        direction_button = driver.find_element(By.XPATH, '//span/a[contains(text(), "directions")]')
        direction_button.click()
        time.sleep(2)
        address = driver.find_element(By.XPATH, '//div[@class = "directionsContainer"]/strong').text.strip()
        map_url = driver.find_element(By.XPATH, '//span/a[contains(text(), "map")]').get_attribute("href")
    except NoSuchElementException:
        address, map_url = "", ""

    try:
        site_url = driver.find_element(By.XPATH, '//span[@class="ListingDetails_Level2_VISITSITE"]//a').get_attribute("href")
    except NoSuchElementException:
        try:
            site_url = driver.find_element(By.XPATH, '//span[@class="ListingDetails_Level1_VISITSITE"]//a').get_attribute("href")
        except:
          site_url = ""
    
    OBJ = {
        "name": name,
        "territory": territory,
        "registration_number": registration_number,
        "jurisdiction": jurisdiction,
        "map_url": map_url,
        "category": category,
        "contacts_detail": [
            {
                "type": "phone_number",
                "value": phone_number
            },
            {
                "type:": "fax_number",
                "value": fax_number
            },
            {
                "type": "website",
                "value": site_url.replace("%", "%%")
            }
        ],
        "industries": description,
        "starting_year": starting_year,
        "addresses_detail": [
            {
                "type": "general_address",
                "address": address
            }
        ]
    }

    #Few records have same name and registration number but different type and data.
    #For the reason above, we are generating the entity ID based on: Name + Reg No. + Category

    UUID_ = OBJ["registration_number"]+ OBJ["name"]

    OBJ = cayman_crawler.prepare_data_object(OBJ)
    ENTITY_ID = cayman_crawler.generate_entity_id(OBJ["meta_detail"]["category"], UUID_)
    BIRTH_INCORPORATION_DATE = ''
    ROW = cayman_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    cayman_crawler.insert_record(ROW)

def crawl():
    all_categories = driver.find_elements(By.XPATH, '//ul/li[@class = "ListingCategories_AllCategories_CATEGORY"]/a')
    category_names = [name.text for name in all_categories]
    all_categories_url = [category.get_attribute("href") for category in all_categories]
    for index, category in enumerate(all_categories_url[start_category-1:]):
        driver.get(category)
        category_name = category_names[start_category+index-1] if len(sys.argv) > 1 else category_names[index]
        print(f"Scraping Category Number: {index+start_category+1}") if start_category == 0 else print(f"Scraping Category Number: {index+start_category}")
        time.sleep(2)
        all_companies = driver.find_elements(By.XPATH, '//span[@itemprop = "name"]/a')
        if len(all_companies) >= 2:
            all_companies_url = [company.get_attribute("href") for company in all_companies]
            for company_url in all_companies_url:
                driver.get(company_url)
                time.sleep(2)
                get_data(category= category_name)
        else:
            try:
                get_data(category= category_name)
            except:
                print("No records for this category")

try:
    driver.get("https://web.caymanchamber.ky/allcategories")
    time.sleep(2)
    print("Website Opened")
    crawl()
    log_data = {"status": 'success',
                "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}

    cayman_crawler.db_log(log_data)
    cayman_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": 'fail',
                "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    cayman_crawler.db_log(log_data)