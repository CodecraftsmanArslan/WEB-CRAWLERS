"""Import required library"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from multiprocessing import Process, freeze_support
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from dateutil import parser
import sys
from datetime import datetime
import traceback
import time
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from load_env.load_env import ENV

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv
FILE_PATH = os.path.dirname(os.getcwd()) + "/kentucky"

# if ENV["ENVIRONMENT"] == "LOCAL":
#     FILE_PATH = os.path.dirname(os.getcwd()) + "/kentucky"
# else:
#     FILE_PATH = os.path.dirname(
#         os.getcwd()) + "/KYB-Crawlers/crawlers_v2/official_registries/kentucky"

URL = "https://web.sos.ky.gov/bussearchnprofile/Profile/?ctr="

meta_data = {
    'SOURCE': 'Kentucky Secretary of State',
    'COUNTRY': 'Kentucky',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://web.sos.ky.gov/bussearchnprofile/search",
                      "Source Description": "The Kentucky Secretary of State website serves as the official online platform for the Office of the Secretary of State in the state of Kentucky, USA. It provides a wide range of services, resources, and information related to business filings, elections, and government matters. The website offers various tools and features to assist individuals, businesses, and organizations in accessing important information and conducting official transactions."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://web.sos.ky.gov/bussearchnprofile/search'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Kentucky Official Registry"
}

kentucky_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = kentucky_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)

# Removes the alert sent by website.


def remove_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()

        print(f"Alert: {alert_text} - Removed")
    except NoAlertPresentException:
        pass

# This function takes a 'timestamp' as input, which is a string representing a date and time.


def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

# This function takes two inputs: a 'table' object (typically representing an HTML table) and a 'string' to search for in the table.


def format_data(table, string):
    element = table.find("td", string=string)
    if element:
        element = element.find_next_sibling().text.strip()
        return element
    else:
        return ""


def crawl(start_number, end_number):
    """
    This function 'crawl' is responsible for web scraping a range of records within a specified range defined by 'start_number' and 'end_number'.
    @param: 
    - start_number: (int)
    - end_number: (int)
    """
    for i in range(start_number, end_number):
        query = str(i).zfill(7)
        company_link = URL + query
        with open(f"{FILE_PATH}/crawled_record.txt", "r") as crawled_records:
            file_contents = crawled_records.read()
            if query in file_contents:
                continue
        driver.get(company_link)
        time.sleep(1)
        print("Record Opened!")
        remove_alert(driver=driver)
        if len(driver.find_elements(By.XPATH, '//input[@value="Show Current Officers"]')) > 0:
            current_officer_btn = driver.find_element(
                By.XPATH, '//input[@value="Show Current Officers"]')
            current_officer_btn.click()
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//h4[text()="Current Officers"]')))
            except:
                remove_alert(driver=driver)
        if len(driver.find_elements(By.XPATH, '//input[@value="Show Initial Officers"]')) > 0:
            initial_officer_btn = driver.find_element(
                By.XPATH, '//input[@value="Show Initial Officers"]')
            initial_officer_btn.click()
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//h4[text()="Individuals / Entities listed at time of formation"]')))
            except:
                remove_alert(driver=driver)
        if len(driver.find_elements(By.XPATH, '//input[@value="Show Images"]')) > 0:
            images_btn = driver.find_element(
                By.XPATH, '//input[@value="Show Images"]')
            images_btn.click()
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//h4[text()="Images available online"]')))
            except:
                remove_alert(driver=driver)

        if len(driver.find_elements(By.XPATH, '//input[@value="Show Activities"]')) > 0:
            activities_btn = driver.find_element(
                By.XPATH, '//input[@value="Show Activities"]')
            activities_btn.click()
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//h4[text()="Activity History"]')))
            except:
                remove_alert(driver=driver)
        get_data(record_number=query)
        with open(f"{FILE_PATH}/crawled_record.txt", "a") as crawled_records:
            crawled_records.write(query + "\n")

# This function 'get_data' is responsible for scraping and processing data from a webpage using BeautifulSoup.


def get_data(record_number):
    print(f"Scraping data of: {record_number}...")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    people_detail = []
    filings_detail = []
    addresses_detail = []

    main_table = soup.find("div", id="MainContent_pInfo")
    if main_table:
        main_table = main_table.find("table")
    else:
        return
    organization_number = format_data(main_table, "Organization Number")
    company_name = format_data(main_table, "Name")
    profit_nonprofit = format_data(main_table, "Profit or Non-Profit")
    company_type = format_data(main_table, "Company Type")
    status = format_data(main_table, "Status")
    standing = format_data(main_table, "Standing")
    state = format_data(main_table, "State")
    file_date = format_date(format_data(main_table, "File Date"))
    org_date = format_date(format_data(main_table, "Organization Date"))
    last_annual_report = format_date(
        format_data(main_table, "Last Annual Report"))
    expiration_date = format_date(format_data(main_table, "Expiration Date"))
    principal_office = format_data(main_table, "Principal Office")
    authority_date = format_date(format_data(main_table, "Authority Date"))
    authorized_shares = format_data(main_table, "Authorized Shares")
    office_address_dict = {
        "type": "office_address",
        "address": principal_office
    }
    if principal_office:
        addresses_detail.append(office_address_dict)
    managed_by = format_data(main_table, "Managed By")

    reg_agent = str(main_table.find("td", string="Registered Agent").find_next_sibling(
    )) if main_table.find("td", string="Registered Agent") else ""
    if reg_agent:
        reg_name = reg_agent.split("<br/>")[0].split(">")[-1]
        reg_address = main_table.find(
            "td", string="Registered Agent").find_next_sibling().text.replace(reg_name, "")
        agent_dict = {
            "designation": "registered_agent",
            "name": reg_name,
            "address": reg_address
        }
        people_detail.append(agent_dict)

    officer_table = soup.find("div", id="MainContent_PnlOfficers").find(
        "table") if soup.find("div", id="MainContent_PnlOfficers") else ""
    if officer_table:
        all_officer_rows = officer_table.find_all("tr")
        if len(all_officer_rows) > 1:
            for officer_row in all_officer_rows[1:]:
                officer_data = officer_row.find_all("td")
                officer_title = officer_data[4].text.replace("\n", "")
                officer_name = officer_data[5].text.replace("\n", "")
                officer_dict = {
                    "designation": officer_title,
                    "name": officer_name
                }
                if officer_title or officer_name:
                    people_detail.append(officer_dict)

    officer_2_table = soup.find("div", id="MainContent_PnlIOff").find(
        "table") if soup.find("div", id="MainContent_PnlIOff") else ""
    if officer_2_table:
        all_officer_2_rows = officer_2_table.find_all("tr")
        if len(all_officer_2_rows) > 1:
            for officer_2_row in all_officer_2_rows[1:]:
                officer_2_data = officer_2_row.find_all("td")
                officer_2_title = officer_2_data[5].text.replace("\n", "")
                officer_2_name = officer_2_data[6].text.replace("\n", "")
                officer_2_dict = {
                    "designation": officer_2_title,
                    "name": officer_2_name
                }
                if officer_2_title or officer_2_name:
                    people_detail.append(officer_2_dict)

    activity_table = soup.find("div", id="MainContent_PnlAct").find(
        "table") if soup.find("div", id="MainContent_PnlAct") else ""
    if activity_table:
        all_activity_rows = activity_table.find_all("tr")
        if len(all_activity_rows) > 1:
            for activity_row in all_activity_rows[1:]:
                activity_data = activity_row.find_all("td")
                activity_title = activity_data[6].text.replace("\n", "")
                activity_date = format_date(
                    activity_data[7].text.replace("\n", ""))
                activity_effective_date = format_date(
                    activity_data[8].text.replace("\n", ""))
                activity_org_ref = activity_data[9].text.replace("\n", "")
                activity_dict = {
                    "title": activity_title,
                    "date": activity_date,
                    "effective_date": activity_effective_date,
                    "reference": activity_org_ref
                }
                if activity_title or activity_date or activity_effective_date:
                    filings_detail.append(activity_dict)

    images_table = soup.find("div", id="MainContent_pnlImages").find(
        "table") if soup.find("div", id="MainContent_pnlImages") else ""
    if images_table:
        all_images_rows = images_table.find_all("tr")
        if len(all_images_rows) > 1:
            for images_row in all_images_rows[1:]:
                images_data = images_row.find_all("td")
                images_title = images_data[6].text.replace("\n", "")
                images_url = images_data[6].find("a").get("href").replace(
                    "../", "https://web.sos.ky.gov/bussearchnprofile/") if images_data[6].find("a").get("href") else ""
                images_date = format_date(
                    images_data[7].text.replace("\n", ""))
                images_dict = {
                    "title": images_title,
                    "file_url": images_url,
                    "date": images_date
                }
                if images_title or images_date or images_url:
                    filings_detail.append(images_dict)

    OBJ = {
        "registration_number": organization_number,
        "name": company_name,
        "profit_non_profit": profit_nonprofit,
        "type": company_type,
        "status": status,
        "standing": standing,
        "authorized_shares": authorized_shares,
        "authority_date": authority_date,
        "dissolution_date": expiration_date,
        "managed_by": managed_by,
        "jurisdiction_code": state,
        "registration_date": file_date,
        "organization_date": org_date,
        "last_anual_report": last_annual_report,
        "addresses_detail": addresses_detail,
        "people_detail": people_detail,
        "fillings_detail": filings_detail
    }

    OBJ = kentucky_crawler.prepare_data_object(OBJ)
    ENTITY_ID = kentucky_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ.get('name', "").replace("%", "%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = kentucky_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    kentucky_crawler.insert_record(ROW)


try:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 1300656
    crawl(start, end)
    log_data = {"status": "success", "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"],
                "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",
                "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    kentucky_crawler.db_log(log_data)
    kentucky_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail", "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"],
                "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE,
                "trace_back": tb.replace("'", "''"), "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    kentucky_crawler.db_log(log_data)
