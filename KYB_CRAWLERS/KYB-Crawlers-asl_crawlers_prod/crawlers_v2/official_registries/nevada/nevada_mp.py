"""Import required library"""
from pyvirtualdisplay import Display
import zipfile
import ssl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from datetime import datetime
import time
import os
import sys
from multiprocessing import Process, freeze_support
import traceback
import undetected_chromedriver as uc
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from load_env.load_env import ENV

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
FILE_PATH = os.path.dirname(os.getcwd()) + "/nevada"

nevada_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = nevada_crawler.get_selenium_helper()

display = Display(visible=0, size=(800, 600))
display.start()

starting_number = 1000000
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


def find_solve_captcha():
    if len(driver.find_elements(By.XPATH, '//iframe[@id="main-iframe"]')) > 0:
        iframe_element = driver.find_element(
            By.XPATH, '//iframe[@id="main-iframe"]')
        driver.switch_to.frame(iframe_element)
        time.sleep(1)
        second_iframe = driver.find_element(
            By.XPATH, '//iframe[@title="reCAPTCHA"]')
        driver.switch_to.frame(second_iframe)
        time.sleep(1)
        print("Captcha Found!")
        captcha_not_solved = True
        captcha_element_classes = driver.find_element(
            By.XPATH, '//span[@role="checkbox"]')
        captcha_element_classes = captcha_element_classes.get_attribute(
            "class")
        if "recaptcha-checkbox-checked" not in captcha_element_classes:
            print('trying to resolve captcha...')
            solve_tries = 0
            while captcha_not_solved and solve_tries < 6:
                if len(driver.find_elements(
                        By.XPATH, '//span[@role="checkbox"]')) > 0:
                    captcha_element_classes = driver.find_element(
                        By.XPATH, '//span[@role="checkbox"]').get_attribute("class")
                    if "recaptcha-checkbox-checked" not in captcha_element_classes:
                        print("Still Trying...")
                        time.sleep(10)
                        solve_tries += 1
                        continue
                    else:
                        captcha_not_solved = False
                else:
                    break
            print("Stuck at captcha, refreshing the page...")
            driver.get(
                "https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
        else:
            print("No Captcha Found")
            driver.switch_to.default_content()

        driver.switch_to.default_content()
        print("Captcha has been Solved!")
        time.sleep(2)
    else:
        print("Captcha not found.")

# opens the webpage, enter the search query, if there is any data it opens the data page.


def crawl(starting_year, ending_year):
    driver.get("https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
    time.sleep(2)
    for year in range(starting_year, ending_year):
        for number in range(starting_number, ending_number):
            ID_ = f"NV{year}{number}"
            with open(f"{FILE_PATH}/crawled_record.txt", "r") as crawled_records:
                file_contents = crawled_records.read()
                if ID_ in file_contents:
                    continue
            while True:
                try:
                    time.sleep(2)
                    find_solve_captcha()
                    search_field = driver.find_element(
                        By.ID, 'BusinessSearch_Index_txtNVBusinessID')
                    search_field.clear()
                    time.sleep(1)
                    search_field.send_keys(ID_)
                    time.sleep(1)
                    search_field.send_keys(Keys.RETURN)
                    time.sleep(5)
                    find_solve_captcha()
                    break
                except:
                    print("Search Field Not Found, Refreshing the page...")
                    driver.get(
                        "https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
                    time.sleep(5)
                    find_solve_captcha()
            try:
                company_link = driver.find_element(By.XPATH, '//tr/td/a')
                if company_link:
                    get_data(id=ID_, driver=driver)
                    with open(f"{FILE_PATH}/crawled_record.txt", "a") as crawled_records:
                        crawled_records.write(ID_ + "\n")

            except:
                print(f"No record found for: {ID_}")
                with open(f"{FILE_PATH}/crawled_record.txt", "a") as crawled_records:
                    crawled_records.write(ID_ + "\n")
                try:
                    alert = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@class = "ui-dialog-buttonset"]/button')))
                    alert.click()
                    continue
                except TimeoutException:
                    driver.get(
                        "https://esos.nv.gov/EntitySearch/OnlineEntitySearch")
                    time.sleep(5)
                    find_solve_captcha()
                    continue

# It scrapes all the data available for the company and store in database.


def get_data(id, driver):

    print(f"Scraping details for ID: {id}")

    officer_list = []
    share_data = []
    filing_details = []
    name_details = []
    merger_details = []

    company_link = driver.find_element(By.XPATH, '//tr/td/a')
    company_link.click()
    time.sleep(2)
    find_solve_captcha()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    entity_name = soup.find(
        'label', string="Entity Name:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Entity Name:") else ""
    entity_type = soup.find(
        'label', string="Entity Type:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Entity Type:") else ""
    formation_date = soup.find(
        'label', string="Formation Date:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Formation Date:") else ""
    try:
        termination_date = soup.find(
            'label', string="Termination Date:").parent.find_next_sibling().text.strip()
    except:
        termination_date = ""
    entity_number = soup.find(
        'label', string="Entity Number:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Entity Number:") else ""
    entity_status = soup.find(
        'label', string="Entity Status:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Entity Status:") else ""
    business_id = soup.find(
        'label', string="NV Business ID:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="NV Business ID:") else ""
    report_due_date = soup.find('label', string="Annual Report Due Date:").parent.find_next_sibling(
    ).text.strip().replace("/", "-") if soup.find('label', string="Annual Report Due Date:") else ""

    # Agent Details
    agent_name = soup.find(
        'label', string="Name of Individual or Legal Entity: ").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Name of Individual or Legal Entity: ") else ""
    agent_entity_type = soup.find(
        'label', string="CRA Agent Entity Type: ").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="CRA Agent Entity Type: ") else ""
    agent_id = soup.find(
        'label', string="NV Business ID: ").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="NV Business ID: ") else ""
    jurisdiction = soup.find(
        'label', string="Jurisdiction: ").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Jurisdiction: ") else ""
    street_address = soup.find(
        'label', string="Street Address:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Street Address:") else ""
    mailing_address = soup.find('label', string="Mailing Address:").parent.find_next_sibling().text.strip(
    ) if soup.find('label', string="Mailing Address:") else ""
    authority_individual = soup.find(
        'label', string="Individual with Authority to Act:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Individual with Authority to Act:") else ""
    website_domain = soup.find(
        'label', string="Fictitious Website or Domain Name:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Fictitious Website or Domain Name:") else ""
    agent_status = soup.find(
        'label', string="Status:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Status:") else ""
    agent_type = soup.find(
        'label', string="Registered Agent Type:").parent.find_next_sibling().text.strip() if soup.find(
        'label', string="Registered Agent Type:") else ""

    # Officers Detail
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
    if officer_table:
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
    if share_table:
        share_rows = share_table.find_all('tr')
        no_par_value = soup.find(
            "span", string="Number of No Par Value Shares:").parent.find_next_sibling().text.replace("\n", "")
        total_auth_capital = soup.find(
            "span", string="Total Authorized Capital:").parent.find_next_sibling().text.replace("\n", "")
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
    if len(driver.find_elements(
            By.XPATH, '//input[@value = "Filing History"]')) > 0:
        filing_history_button = driver.find_element(
            By.XPATH, '//input[@value = "Filing History"]')
        filing_history_button.click()
        time.sleep(2)
        find_solve_captcha()
        filing_soup = BeautifulSoup(driver.page_source, "html.parser")
        filling_table = filing_soup.find("table", id="xhtml_grid")
        if filling_table:
            filing_rows = filling_table.find_all("tr")
            for row in filing_rows[1:]:
                if row.find("td").text.strip() != "No records to view.":
                    filing_cell = row.find_all("td")
                    filing_date = filing_cell[0].text.replace("/", "-")
                    filing_effective_date = filing_cell[1].text.replace(
                        "/", "-")
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

        back_button = driver.find_element(By.ID, 'btnBack')
        back_button.click()
        time.sleep(2)
        find_solve_captcha()

    # Previous Name Details
    time.sleep(2)
    if len(driver.find_elements(
            By.XPATH, '//input[@value = "Name History"]')) > 0:
        name_history_button = driver.find_element(
            By.XPATH, '//input[@value = "Name History"]')
        name_history_button.click()
        time.sleep(2)
        find_solve_captcha()
        name_soup = BeautifulSoup(driver.page_source, "html.parser")
        name_table = name_soup.find("table", id="xhtml_grid")
        if name_table:
            name_rows = name_table.find_all("tr")
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
            find_solve_captcha()

    # Merger/Coverser Details
    time.sleep(2)
    if len(driver.find_elements(
            By.XPATH, '//input[@value = "Mergers/Conversions"]')) > 0:
        merger_button = driver.find_element(
            By.XPATH, '//input[@value = "Mergers/Conversions"]')
        merger_button.click()
        time.sleep(2)
        find_solve_captcha()
        merger_soup = BeautifulSoup(driver.page_source, "html.parser")
        merger_table = merger_soup.find("table", id="xhtml_grid")
        if merger_table:
            merger_rows = merger_table.find_all("tr")
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

        back_button = driver.find_element(By.ID, 'btnBack')
        back_button.click()
        time.sleep(2)
        find_solve_captcha()

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
    time.sleep(2)


try:

    processess = []
    if __name__ == '__main__':
        freeze_support()
        procs = []
        start_1 = 1980
        end_1 = 1991
        start_2 = 1991
        end_2 = 2001
        start_3 = 2001
        end_3 = 2011
        start_4 = 2011
        end_4 = 2023

        process_1 = Process(target=crawl, args=(start_1, end_1))
        processess.append(process_1)
        process_1.start()
        process_2 = Process(target=crawl, args=(start_2, end_2))
        processess.append(process_2)
        process_2.start()
        process_3 = Process(target=crawl, args=(start_3, end_3))
        processess.append(process_3)
        process_3.start()
        process_4 = Process(target=crawl, args=(start_4, end_4))
        processess.append(process_4)
        process_4.start()

        for proc in processess:
            proc.join()

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
