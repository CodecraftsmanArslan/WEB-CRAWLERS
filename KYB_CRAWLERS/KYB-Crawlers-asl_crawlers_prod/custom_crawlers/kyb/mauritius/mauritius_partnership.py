"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import ssl
from datetime import datetime
from random import randint
from dateutil import parser
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENTS = sys.argv
TIMEOUT = 5

meta_data = {
    'SOURCE': 'Corporate and Business Registration Department (CBRD)',
    'COUNTRY': 'Mauritius',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": " https://onlinesearch.mns.mu/",
                      "Source Description": "The Corporate and Business Registration Department (CBRD) of Mauritius is a government agency responsible for the registration and administration of businesses and corporate entities in Mauritius. It operates under the Ministry of Financial Services and Good Governance."},
    'SOURCE_TYPE': 'HTML',
    'URL': ' https://onlinesearch.mns.mu/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Mauritius Partnership Official Registry"
}

mauritius_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = mauritius_crawler.get_selenium_helper()
request_helper = mauritius_crawler.get_requests_helper()

start_number = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 16
end_number = 200

# format the date and replace "/" withn "-"


def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

# proxy_host = "185.48.55.61"
# proxy_port = "6537"

# It generates a random number for random time intervals


def random_number():
    r_numb = randint(1, 3)
    return r_numb

# Opens the webpage and search the company data.


def crawl(start_number):
    options = Options()
    options.add_argument("--headless")
    # options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
    driver = uc.Chrome(version_main=114, options=options)
    driver.get('https://onlinesearch.mns.mu/')
    time.sleep(5)
    for i in range(start_number, end_number):
        random_query = randint(start_number, end_number)
        with open("crawled_record_py.txt", "r") as crawled_records:
            file_contents = crawled_records.read()
            if str(random_query) in file_contents:
                continue
            else:
                with open("crawled_record_py.txt", "a") as crawled_records:
                    crawled_records.write(str(random_query) + "\n")
        search_query = "p" + str(random_query)
        search_field = driver.find_element(
            By.ID, 'company-partnership-text-field')
        search_field.send_keys(search_query)
        time.sleep(random_number())
        file_radio = driver.find_element(By.ID, 'fileNo')
        file_radio.click()
        time.sleep(random_number())
        search_button = driver.find_element(
            By.XPATH, '//button[text()=" Search "]')
        search_button.click()
        time.sleep(random_number())
        try:
            error_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="ERROR"]')))
            if error_box:
                print("Bot Detected!!!")
                driver.quit()
                time.sleep(random_number())
                crawl(start_number)
        except:
            try:
                try:
                    cookie_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()=" Accept "]')))
                except:
                    cookie_button = ""
                if cookie_button:
                    cookie_button = driver.find_element(
                        By.XPATH, '//button[text()=" Accept "]')
                    cookie_button.click()
                data_view_button = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//fa-icon[@title="View"]')))
                data_view_button.click()
                time.sleep(random_number())
                WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, 'cdk-accordion-child-1')))
                print(f"Scraping data for {search_query}...")
                time.sleep(random_number())
                get_data(driver=driver)
                time.sleep(random_number())
            except:
                print(f"No record found for {search_query}.")
                driver.refresh()
                time.sleep(5)
                continue

# If there is data, it scrapes data using beautifulsoup4 and store it in Database.


def get_data(driver):

    soup = BeautifulSoup(driver.page_source, "html.parser")

    people_details = []
    company_detail_table = soup.find(id="cdk-accordion-child-1")
    file_no = company_detail_table.find("label", string="File No.:")
    file_no = file_no.find_next_sibling().text.strip() if file_no is not None else ""
    name = company_detail_table.find("label", string="Name:")
    name = name.find_next_sibling().text.strip().replace(
        "\n", " ").replace("  ", "") if name is not None else ""
    category = company_detail_table.find("label", string="Category:")
    category = category.find_next_sibling().text.strip() if category is not None else ""
    type_ = company_detail_table.find("label", string="Type:")
    type_ = type_.find_next_sibling().text.strip() if type_ is not None else ""
    office_address = company_detail_table.find(
        "label", string="Siege Social Address:")
    office_address = office_address.find_next_sibling().text.replace(
        "\n", " ").replace("  ", "").strip() if office_address is not None else ""
    registration_date = company_detail_table.find(
        "label", string="Date Incorporated/Registered:")
    if registration_date:
        registration_date = registration_date.find_next_sibling().text.strip()
        registration_date = format_date(registration_date)
    else:
        registration_date = ""
    nature = company_detail_table.find("label", string="Nature:")
    nature = nature.find_next_sibling().text.strip() if nature is not None else ""
    sub_category = company_detail_table.find("label", string="Sub-category:")
    sub_category = sub_category.find_next_sibling(
    ).text.strip() if sub_category is not None else ""
    status = company_detail_table.find("label", string="Status:")
    status = status.find_next_sibling().text.strip() if status is not None else ""
    inactive_date = company_detail_table.find("label", string="Defunct Date:")
    if inactive_date:
        inactive_date = inactive_date.find_next_sibling(
        ).text.strip() if inactive_date is not None else ""
        inactive_date = format_date(inactive_date)
    else:
        inactive_date = ""

    business_detail_table = soup.find(id="cdk-accordion-child-2")
    bdt_body = business_detail_table.find("tbody")
    bdt_rows = bdt_body.find_all("tr")
    bdt_check = bdt_body.find("tr").find("h4").text.strip(
    ) if bdt_body.find("tr").find("h4") is not None else ""
    all_business_data = []
    if len(bdt_rows) > 0 and "No result to display" not in bdt_check:
        for bdt_row in bdt_rows:
            business_registration_number = bdt_row.find(
                "td", {"data-column": "Business Registration No."})
            business_registration_number = business_registration_number.text.strip(
            ) if business_registration_number is not None else ""
            business_name = bdt_row.find(
                "td", {"data-column": "Business Name"})
            business_name = business_name.text.strip().replace(
                ".", "") if business_name is not None else ""
            nature_of_business = bdt_row.find(
                "td", {"data-column": "Nature of Business"})
            nature_of_business = nature_of_business.text.strip().replace(
                "\n", " ").replace("  ", "").strip() if nature_of_business is not None else ""
            business_address = bdt_row.find(
                "td", {"data-column": "Business Address"})
            business_address = business_address.text.strip().replace(
                "\n", " ").replace("  ", "") if business_address is not None else ""
            bdt_dict = {
                "registration_number": business_registration_number,
                "name": business_name,
                "nature_of_business": nature_of_business,
                "business_address": business_address
            }
            all_business_data.append(bdt_dict)

    share_detail_table = soup.find(id="cdk-accordion-child-3")
    sdt_body = share_detail_table.find("tbody")
    sdt_rows = sdt_body.find_all("tr")
    sdt_check = sdt_body.find("tr").find("h4").text.strip(
    ) if sdt_body.find("tr").find("h4") is not None else ""
    all_share_data = []
    if len(sdt_rows) > 0 and "No result to display" not in sdt_check:
        for sdt_row in sdt_rows:
            type_of_shares = sdt_row.find(
                "td", {"data-column": "Type Of Shares"}).text.strip().replace("\n", "").replace("  ", "")
            no_of_shares = sdt_row.find(
                "td", {"data-column": "No. Parts of Social"}).text.strip()
            share_currency = sdt_row.find(
                "td", {"data-column": "Currency"}).text.strip()
            share_capital = sdt_row.find(
                "td", {"data-column": "Stated Capital"}).text.strip()
            amount_unpaid = sdt_row.find(
                "td", {"data-column": "Amount Unpaid"}).text.strip()
            par_value = sdt_row.find(
                "td", {"data-column": "Valeur Nominale"}).text.strip()
            sdt_dict = {
                "share_type": type_of_shares,
                "number_of_shares": no_of_shares,
                "currency": share_currency,
                "capital": share_capital,
                "amount_unpaid": amount_unpaid,
                "par_value": par_value
            }
            all_share_data.append(sdt_dict)

    office_bearer_table = soup.find(id="cdk-accordion-child-4")
    obt_body = office_bearer_table.find("tbody")
    obt_rows = obt_body.find_all("tr")
    obt_check = obt_body.find("tr").find("h4").text.strip(
    ) if obt_body.find("tr").find("h4") is not None else ""
    if len(obt_rows) > 0 and "No result to display" not in obt_check:
        for obt_row in obt_rows:
            bearer_position = obt_row.find(
                "td", {"data-column": "Position"}).text.strip()
            bearer_name = obt_row.find(
                "td", {"data-column": "Name"}).text.replace("\n", " ").replace("  ", "").strip()
            bearer_address = obt_row.find(
                "td", {"data-column": "Address"}).text.strip().replace("\n", " ").replace("  ", "")
            bearer_appointed_date = obt_row.find(
                "td", {"data-column": "Appointed Date"}).text.strip()

            obt_dict = {
                "designation": bearer_position,
                "name": bearer_name,
                "address": bearer_address,
                "appointment_date": format_date(bearer_appointed_date)
            }
            people_details.append(obt_dict)

    associes_table = soup.find(id="cdk-accordion-child-5")
    associes_body = associes_table.find("tbody")
    associes_rows = associes_body.find_all("tr")
    associes_check = associes_body.find("tr").find("h4").text.strip(
    ) if associes_body.find("tr").find("h4") is not None else ""
    all_associes_data = []
    if len(associes_rows) > 0 and "No result to display" not in associes_check:
        for associes_row in associes_rows:
            shareholder_name = associes_row.find(
                "td", {"data-column": "Name"}).text.strip().replace("\n", " ").replace("  ", "")
            sh_number_of_shares = associes_row.find(
                "td", {"data-column": "No. of Parts Social"}).text.strip()
            sh_type_of_shares = associes_row.find(
                "td", {"data-column": "Type of Parts Social"}).text.strip().replace("\n", "").replace("  ", "")
            sh_currency = associes_row.find(
                "td", {"data-column": "Currency"}).text.strip()
            associes_dict = {
                "name": shareholder_name,
                "number_of_shares": sh_number_of_shares,
                "type_of_shares": sh_type_of_shares,
                "currency": sh_currency
            }
            all_associes_data.append(associes_dict)

    winding_up_table = soup.find(id="cdk-accordion-child-7")
    wut_body = winding_up_table.find("tbody")
    wut_rows = wut_body.find_all("tr")
    wut_check = wut_body.find("tr").find("h4").text.strip(
    ) if wut_body.find("tr").find("h4") is not None else ""
    winding_up_details = []
    if len(wut_rows) > 0 and "No result to display" not in wut_check:
        for wut_row in wut_rows:
            winding_type = wut_row.find(
                "td", {"data-column": "Type"}).text.strip().replace("\n", " ").replace("  ", "")
            wut_start_date = wut_row.find(
                "td", {"data-column": "Start Date"}).text.strip()
            wut_end_date = wut_row.find(
                "td", {"data-column": "End Date"}).text.strip()
            wut_winding_status = wut_row.find(
                "td", {"data-column": "Status"}).text.strip()
            wut_dict = {
                "winding_type": winding_type,
                "start_date": format_date(wut_start_date),
                "end_date": format_date(wut_end_date),
                "winding_status": wut_winding_status
            }
            winding_up_details.append(wut_dict)

    liquidators_table = soup.find(id="cdk-accordion-child-6")
    liq_name = liquidators_table.find("label", string="Name:")
    liq_name = liq_name.find_next_sibling().text.strip() if liq_name is not None else ""
    liq_address = liquidators_table.find("label", string="Address:")
    liq_address = liq_address.find_next_sibling(
    ).text.strip() if liq_address is not None else ""
    liq_appointed_date = liquidators_table.find(
        "label", string="Appointed Date:")
    liq_appointed_date = liq_appointed_date.find_next_sibling(
    ).text.strip() if liq_appointed_date is not None else ""
    liq_dict = {
        "designation": "liquidator",
        "name": liq_name,
        "address": liq_address,
        "appointment_date": format_date(liq_appointed_date)
    }
    if liq_name:
        people_details.append(liq_dict)

    objections_table = soup.find(id="cdk-accordion-child-8")
    objections_body = objections_table.find("tbody")
    objections_rows = objections_body.find_all("tr")
    objections_check = objections_body.find("tr").find("h4").text.strip(
    ) if objections_body.find("tr").find("h4") is not None else ""
    objection_details = []
    if len(objections_rows) > 0 and "No result to display" not in objections_check:
        for objections_row in objections_rows:
            objection_date = objections_row.find(
                "td", {"data-column": "Objection Date"}).text.strip()
            objector = objections_row.find(
                "td", {"data-column": "Objector"}).text.strip()
            objections_dict = {
                "date": objection_date,
                "objector": objector
            }
            objection_details.append(objections_dict)

    OBJ = {
        "registration_number": file_no,
        "name": name,
        "category": category,
        "type": type_,
        "registration_date": registration_date,
        "nature": nature,
        "sub_category": sub_category,
        "status": status,
        "inactive_date": inactive_date,
        "addresses_detail": [
            {
                "type": "registered_address",
                "address": office_address
            }
        ],
        "additional_detail": [
            {
                "type": "shares_information",
                "data": all_share_data
            },
            {
                "type": "associes_information",
                "data": all_associes_data
            },
            {
                "type": "winding_up_information",
                "data": winding_up_details
            },
            {
                "type": "branches_and_other_offices",
                "data": all_business_data
            },
            {
                "type": "objections_information",
                "data": objection_details
            }
        ],
        "people_detail": people_details,
    }

    OBJ = mauritius_crawler.prepare_data_object(OBJ)
    ENTITY_ID = mauritius_crawler.generate_entity_id(
        OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = mauritius_crawler.prepare_row_for_db(
        ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    mauritius_crawler.insert_record(ROW)

    time.sleep(3)
    popup_close_button = driver.find_element(
        By.CLASS_NAME, 'dialog-close-button')
    popup_close_button.click()
    time.sleep(3)
    driver.refresh()
    time.sleep(5)


try:
    crawl(start_number)
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    mauritius_crawler.db_log(log_data)
    mauritius_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    mauritius_crawler.db_log(log_data)
