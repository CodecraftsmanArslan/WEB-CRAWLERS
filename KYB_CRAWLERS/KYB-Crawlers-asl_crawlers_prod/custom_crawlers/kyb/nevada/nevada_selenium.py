"""Import required library"""
import sys, traceback,time,os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import undetected_chromedriver as uc
from datetime import datetime
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl
import zipfile
from pyvirtualdisplay import Display

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
arguments = sys.argv

meta_data = {
    'SOURCE': 'SilverFlume- Nevada Secretary of State, Commercial Recordings Division',
    'COUNTRY': 'Nevada',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://esos.nv.gov/EntitySearch/OnlineEntitySearch",
                      "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://esos.nv.gov/EntitySearch/OnlineEntitySearch'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Nevada"
}

NOPECHA_KEY = 'sub_1NdSf9CRwBwvt6ptQYIIto4Z'

nevada_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = nevada_crawler.get_selenium_helper()

display = Display(visible=0,size=(800,600))
display.start()

starting_number = int(arguments[2]) if len(arguments) > 2 else 1000010
starting_year = int(arguments[1]) if len(arguments) > 1 else 1980
ending_year = 2023
ending_number = 1999999
timeout = 60

options = uc.ChromeOptions()
with zipfile.ZipFile('chrome.zip', 'r') as f:
    f.extractall('nopecha')
options.add_argument(f"--load-extension={os.getcwd()}/nopecha")
print("Downloading NopeCHA crx extension file.")
print('Open webdriver')
driver = uc.Chrome(version_main=114, options=options)
driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY}")
action = ActionChains(driver=driver)

# It will identify if there is any captcha on website and solves it.


def find_solve_captcha(browser):
    try:
        iframe_element = browser.find_element(
            By.XPATH, '//iframe[@title="reCAPTCHA"]')
        browser.switch_to.frame(iframe_element)
        time.sleep(1)
        captcha_not_solved = True
        captcha_element_classes = driver.find_element(
            By.XPATH, '//span[@role="checkbox"]')
        captcha_element_classes = captcha_element_classes.get_attribute(
            "class")
        if "recaptcha-checkbox-checked" not in captcha_element_classes:
            print("Captcha Found!")
            print('trying to resolve captcha...')
            while captcha_not_solved:
                captcha_element_classes = driver.find_element(
                    By.XPATH, '//span[@role="checkbox"]').get_attribute("class")
                if "recaptcha-checkbox-checked" not in captcha_element_classes:
                    print("Still Trying...")
                    time.sleep(3)
                    continue
                else:
                    captcha_not_solved = False
        else:
            print("No Captcha Found")
            browser.switch_to.default_content()

        browser.switch_to.default_content()
        print("Captcha has been Solved!")
        time.sleep(2)
    except Exception as e:
        browser.switch_to.default_content()
        print("Captcha not found.")

# opens the webpage, enter the search query, if there is any data it opens the data page.


def crawl():
    driver.get("https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
    time.sleep(2)
    for year in range(starting_year, ending_year):
        for number in range(starting_number, ending_number):
            ID_ = f"NV{year}{number}"
            while True:
                try:
                    time.sleep(2)
                    find_solve_captcha(browser=driver)
                    search_field = driver.find_element(
                        By.ID, 'BusinessSearch_Index_txtNVBusinessID')
                    search_field.clear()
                    time.sleep(1)
                    search_field.send_keys(ID_)
                    time.sleep(1)
                    search_field.send_keys(Keys.RETURN)
                    time.sleep(5)
                    find_solve_captcha(browser=driver)
                    break
                except:
                    print("Search Field Not Found, Refreshing the page...")
                    driver.get(
                        "https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
                    time.sleep(5)
                    find_solve_captcha(browser=driver)
            try:
                company_link = driver.find_element(By.XPATH, '//tr/td/a')
                if company_link:
                    get_data(id=ID_, driver=driver)
            except:
                print(f"No record found for: {ID_}")
                try:
                    alert = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@class = "ui-dialog-buttonset"]/button')))
                    alert.click()
                    continue
                except TimeoutException:
                    driver.get(
                        "https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
                    time.sleep(5)
                    find_solve_captcha(browser=driver)
                    continue

# It scrapes all the data available for the company and store in database.


def get_data(id, driver):
    print(f"Scraping details for ID: {id}")
    company_link = driver.find_element(By.XPATH, '//tr/td/a')
    company_link.click()
    time.sleep(5)
    find_solve_captcha(browser=driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    entity_name = soup.find(
        'label', string="Entity Name:").parent.find_next_sibling().text.strip()
    entity_type = soup.find(
        'label', string="Entity Type:").parent.find_next_sibling().text.strip()
    formation_date = soup.find(
        'label', string="Formation Date:").parent.find_next_sibling().text.strip()
    try:
        termination_date = soup.find(
            'label', string="Termination Date:").parent.find_next_sibling().text.strip()
    except:
        termination_date = ""
    entity_number = soup.find(
        'label', string="Entity Number:").parent.find_next_sibling().text.strip()
    entity_status = soup.find(
        'label', string="Entity Status:").parent.find_next_sibling().text.strip()
    business_id = soup.find(
        'label', string="NV Business ID:").parent.find_next_sibling().text.strip()
    report_due_date = soup.find('label', string="Annual Report Due Date:").parent.find_next_sibling(
    ).text.strip().replace("/", "-")

    # Agent Details
    agent_name = soup.find(
        'label', string="Name of Individual or Legal Entity: ").parent.find_next_sibling().text.strip()
    agent_entity_type = soup.find(
        'label', string="CRA Agent Entity Type: ").parent.find_next_sibling().text.strip()
    agent_id = soup.find(
        'label', string="NV Business ID: ").parent.find_next_sibling().text.strip()
    jurisdiction = soup.find(
        'label', string="Jurisdiction: ").parent.find_next_sibling().text.strip()
    street_address = soup.find(
        'label', string="Street Address:").parent.find_next_sibling().text.strip()
    mailing_address = soup.find('label', string="Mailing Address:").parent.find_next_sibling().text.strip(
    ) if soup.find('label', string="Mailing Address:").parent.find_next_sibling().text.strip() is not None else ""
    authority_individual = soup.find(
        'label', string="Individual with Authority to Act:").parent.find_next_sibling().text.strip()
    website_domain = soup.find(
        'label', string="Fictitious Website or Domain Name:").parent.find_next_sibling().text.strip()
    agent_status = soup.find(
        'label', string="Status:").parent.find_next_sibling().text.strip()
    agent_type = soup.find(
        'label', string="Registered Agent Type:").parent.find_next_sibling().text.strip()

    # Officers Detail
    officer_list = []
    agent_dict = {
        "name": agent_name,
        "designation": agent_type,
        "address": street_address,
        "postal_address": mailing_address,
        "social_link": website_domain,
        "meta_detail": {
            "status": agent_status,
            "agent_type": agent_entity_type,
            "agent_id": agent_id,
            "jurisdiction": jurisdiction,
            "trusted_person": authority_individual,
        }
    }

    if agent_dict["meta_detail"]["status"] == "":
        del agent_dict["meta_detail"]["status"]
    if agent_dict["meta_detail"]["agent_type"] == "":
        del agent_dict["meta_detail"]["agent_type"]
    if agent_dict["meta_detail"]["agent_id"] == "":
        del agent_dict["meta_detail"]["agent_id"]
    if agent_dict["meta_detail"]["jurisdiction"] == "":
        del agent_dict["meta_detail"]["jurisdiction"]
    if agent_dict["meta_detail"]["trusted_person"] == "":
        del agent_dict["meta_detail"]["trusted_person"]

    officer_list.append(agent_dict)

    officer_table = soup.find('table', id='grid_principalList')
    officer_rows = officer_table.find_all('tr')
    for row in officer_rows[1:]:
        if row.find("td").text.strip() != "No records to view.":
            officer_cells = row.find_all('td')
            officer_designation = officer_cells[0].text.strip()
            officer_name = officer_cells[1].text.strip()
            officer_address = officer_cells[2].text.strip()
            officer_last_updated = officer_cells[3].text.strip()
            officer_status = officer_cells[4].text.strip()
            officer_dict = {
                "designation": officer_designation,
                "name": officer_name,
                "address": officer_address,
                "meta_detail": {
                    "last_updated": officer_last_updated.replace("/", "-"),
                    "status": officer_status
                }
            }
            officer_list.append(officer_dict)

    # Share Details
    share_table = soup.find('table', id='grid_sharesList')
    share_rows = share_table.find_all('tr')
    no_par_value = soup.find(
        "span", string="Number of No Par Value Shares:").parent.find_next_sibling().text.replace("\n", "")
    total_auth_capital = soup.find(
        "span", string="Total Authorized Capital:").parent.find_next_sibling().text.replace("\n", "")
    share_data = []
    for row in share_rows[1:]:
        if row.find("td").text.strip() != "No records to view.":
            share_cells = row.find_all("td")
            share_class_ = share_cells[0].text.strip()
            share_type_ = share_cells[1].text.strip()
            share_number = share_cells[2].text.strip()
            share_value = share_cells[3].text.strip()
            share_dict = {
                "class": share_class_,
                "type": share_type_,
                "share_number": share_number,
                "value": share_value,
                "no_par_value": no_par_value,
                "total_authorized_capital": total_auth_capital
            }
            share_data.append(share_dict)
        else:
            share_dict = {
                "no_par_value": no_par_value,
                "total_authorized_capital": total_auth_capital
            }
            share_data.append(share_dict)

    # Filing Details
    time.sleep(2)
    filing_history_button = driver.find_element(
        By.XPATH, '//input[@value = "Filing History"]')
    filing_history_button.click()
    time.sleep(2)
    find_solve_captcha(browser=driver)
    filing_soup = BeautifulSoup(driver.page_source, "html.parser")
    filling_table = filing_soup.find("table", id="xhtml_grid")
    if filling_table is not None:
        filing_rows = filling_table.find_all("tr")
        filing_details = []
        for row in filing_rows[1:]:
            if row.find("td").text.strip() != "No records to view.":
                filing_cell = row.find_all("td")
                filing_date = filing_cell[0].text.replace("/", "-")
                filing_effective_date = filing_cell[1].text.replace("/", "-")
                filing_code = filing_cell[2].text
                filing_title = filing_cell[3].text
                filing_type = filing_cell[4].text
                filing_source = filing_cell[5].text

                filing_dict = {
                    "date": filing_date,
                    "filing_code": filing_code,
                    "title": filing_title,
                    "filing_type": filing_type,
                    "meta_detail": {
                        "source": filing_source,
                        "effective_date": filing_effective_date,
                    }
                }

                filing_details.append(filing_dict)
    else:
        filing_details = []

    back_button = driver.find_element(By.ID, 'btnBack')
    back_button.click()
    time.sleep(2)
    find_solve_captcha(browser=driver)

    # Previous Name Details
    time.sleep(2)
    name_history_button = driver.find_element(
        By.XPATH, '//input[@value = "Name History"]')
    name_history_button.click()
    time.sleep(2)
    find_solve_captcha(browser=driver)
    name_soup = BeautifulSoup(driver.page_source, "html.parser")
    name_table = name_soup.find("table", id="xhtml_grid")
    if name_table:
        name_rows = name_table.find_all("tr")
        name_details = []
        for row in name_rows[1:]:
            if row.find("td").text.strip() != "No records to view.":
                name_cell = row.find_all("td")
                name_date = name_cell[0].text.replace("/", "-")
                name_update_date = name_cell[1].text.replace("/", "-")
                name_filing_code = name_cell[2].text
                name_name = name_cell[4].text

                name_dict = {
                    "update_date": name_update_date,
                    "name": name_name,
                    "meta_detail": {
                        "filing_date": name_date,
                        "filing_code": name_filing_code,
                    }
                }
                name_details.append(name_dict)

        back_button = driver.find_element(By.ID, 'btnBack')
        back_button.click()
        time.sleep(2)
        find_solve_captcha(browser=driver)
    else:
        name_details = []

    # Merger/Coverser Details
    time.sleep(2)
    merger_button = driver.find_element(
        By.XPATH, '//input[@value = "Mergers/Conversions"]')
    merger_button.click()
    time.sleep(2)
    find_solve_captcha(browser=driver)
    merger_soup = BeautifulSoup(driver.page_source, "html.parser")
    merger_table = merger_soup.find("table", id="xhtml_grid")
    if merger_table:
        merger_rows = merger_table.find_all("tr")
        merger_details = []
        for row in merger_rows[1:]:
            if row.find("td").text.strip() != "No records to view.":
                merger_cell = row.find_all("td")
                merger_name = merger_cell[0].text.replace("/", "-")
                merger_entity_id = merger_cell[1].text.replace("/", "-")
                merger_status = merger_cell[2].text
                merger_type = merger_cell[3].text
                merger_added_date = merger_cell[4].text

                name_dict = {
                    "name": merger_name,
                    "entity_id": merger_entity_id,
                    "status": merger_status,
                    "type": merger_type,
                    "added_date": merger_added_date
                }

                merger_details.append(name_dict)
                back_button = driver.find_element(By.ID, 'btnBack')
                time.sleep(2)
            else:
                continue
    else:
        merger_details = []

    back_button = driver.find_element(By.ID, 'btnBack')
    back_button.click()
    time.sleep(2)
    find_solve_captcha(browser=driver)

    OBJ = {
        "name": entity_name,
        "entity_number": entity_number,
        "type": entity_type,
        "status": entity_status,
        "registration_date": formation_date.replace("/", "-"),
        "registration_number": business_id,
        "inactive_date": termination_date,
        "annual_due_date": report_due_date,
        "charitable_contribution": "",
        "people_detail": officer_list,
        "additional_detail": [
            {
                "type": "shares_information",
                "data": share_data
            },
            {
                "type": "merging_information",
                "data": merger_details
            }
        ],
        "fillings_detail": filing_details,
        "previous_name_detail": name_details,
    }

    OBJ = nevada_crawler.prepare_data_object(OBJ)
    ENTITY_ID = nevada_crawler.generate_entity_id(
        OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = nevada_crawler.prepare_row_for_db(
        ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    nevada_crawler.insert_record(ROW)

    driver.get("https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
    time.sleep(5)


try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    nevada_crawler.db_log(log_data)
    nevada_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    nevada_crawler.db_log(log_data)
    display.stop()
