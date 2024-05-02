"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE': 'Tennessee Secretary of State',
    'COUNTRY': 'Tennessee',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx",
                      "Source Description": "The Tennessee Secretary of State Business Services division provides a range of services and resources related to businesses in the state of Tennessee, USA. The division is responsible for overseeing business registrations, maintaining business records, and facilitating various business-related transactions."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Tennessee_kyb_crawler"
}

display = Display(visible=0, size=(800, 600))
display.start()

tennessee_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = tennessee_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=True)

API_URL = 'https://newregister.bcci.bg/edipub/CombinedReports/SrcCombined'

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments) > 1 else 5

# Help find and solve the captcha.


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

# It changes the format of date and replace "/" with "-"


def change_date_format(date_string):
    if date_string:
        try:
            date = datetime.strptime(date_string, "%m/%d/%Y")
            new_date_string = date.strftime("%m-%d-%Y")
            return new_date_string
        except:
            pass
    else:
        return date_string

# Opens the search page, enter the search number and scrape and store the data in database.


def crawl(record_number=None):
    try:
        ROWS = []
        i = record_number if record_number else PAGE
        while i <= 1398859:
            nine_number_format = "{:09d}".format(int(i))
            print("record_number :", nine_number_format)
            driver.get("https://tnbear.tn.gov/Ecommerce/FilingSearch.aspx")
            time.sleep(5)
            find_solve_captcha(browser=driver)

            input_element = driver.find_element(
                By.ID, "ctl00_MainContent_txtFilingId")
            input_element.send_keys(nine_number_format)
            search_btn = driver.find_element(
                By.ID, 'ctl00_MainContent_SearchButton')
            search_btn.click()
            time.sleep(3)

            table_div = driver.find_element(
                By.ID, "ctl00_MainContent_SearchResultList")
            table_element = table_div.find_element(By.XPATH, ".//table")
            rows = table_element.find_elements(By.XPATH, ".//tr")

            if len(rows) > 1:
                cells = rows[1].find_elements(By.XPATH, ".//td")
                anchor_tag = cells[0].find_element(By.XPATH, ".//a")
                anchor_tag.click()

                find_solve_captcha(browser=driver)

                optional_key = driver.find_element(By.ID, "ctl00_MainContent_lblOptional1").text.strip(
                ).replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_lblOptional1") else ''

                if optional_key == "Managed By:":
                    optional_key = "managed_by"
                elif optional_key == "Shares of Stock:":
                    optional_key = "stock_share"

                OBJ = {
                    "name": driver.find_element(By.ID, "ctl00_MainContent_txtName").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtName") else '',
                    "status": driver.find_element(By.ID, "ctl00_MainContent_txtStatus").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtStatus") else '',
                    "registration_number": nine_number_format,
                    "registration_date": change_date_format(driver.find_element(By.ID, "ctl00_MainContent_txtInitialDate").text.strip()) if driver.find_element(By.ID, "ctl00_MainContent_txtInitialDate") else '',
                    "formed_in": change_date_format(driver.find_element(By.ID, "ctl00_MainContent_txtInitialDate").text.strip()) if driver.find_element(By.ID, "ctl00_MainContent_txtInitialDate") else '',
                    "effective_date": change_date_format(driver.find_element(By.ID, "ctl00_MainContent_txtDelayedDate").text.strip()) if driver.find_element(By.ID, "ctl00_MainContent_txtDelayedDate") else '',
                    "fiscal_year": driver.find_element(By.ID, "ctl00_MainContent_txtFYC").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtFYC") else '',
                    "accounts_receivable_date": change_date_format(driver.find_element(By.ID, "ctl00_MainContent_txtARDueDate").text.strip()) if driver.find_element(By.ID, "ctl00_MainContent_txtARDueDate") else '',
                    "term_of_duration": driver.find_element(By.ID, "ctl00_MainContent_txtDuration").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtDuration") else '',
                    "inactive_date": change_date_format(driver.find_element(By.ID, "ctl00_MainContent_txtInactiveDate").text.strip()) if driver.find_element(By.ID, "ctl00_MainContent_txtInactiveDate") else '',
                    "accounts_receivable_exempt": driver.find_element(By.ID, "ctl00_MainContent_txtARExempt").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtARExempt") else '',
                    "obligated_member_entity": driver.find_element(By.ID, "ctl00_MainContent_txtOME").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtOME") else '',

                    optional_key: driver.find_element(By.ID, "ctl00_MainContent_txtOptional1").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtOptional1") else '',
                    "number_of_members": driver.find_element(By.ID, "ctl00_MainContent_txtOptional2").text.strip().replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtOptional2") else '',

                    "addresses_detail": [
                        {
                            "address": driver.find_element(By.ID, "ctl00_MainContent_txtOfficeAddresss").text.strip().replace("'", "''").replace('\n', ' ') if driver.find_element(By.ID, "ctl00_MainContent_txtOfficeAddresss") else '',
                            "type": "office_address"
                        } if driver.find_element(By.ID, "ctl00_MainContent_txtOfficeAddresss").text.strip().replace("'", "''") else None,
                        {
                            "type": "postal_address",
                            "address": driver.find_element(By.ID, "ctl00_MainContent_txtMailAddress").text.strip().replace("'", "''").replace("\n", " ") if driver.find_element(By.ID, "ctl00_MainContent_txtMailAddress") else ''
                        }
                    ],

                }

                addtional_detail = list()

                try:
                    name_div = driver.find_element(
                        By.ID, "ctl00_MainContent_divAssumedNames")
                    table_element = name_div.find_element(By.XPATH, ".//table")
                    rows = table_element.find_elements(By.XPATH, ".//tr")

                    if len(rows) > 1:
                        data_names = list()
                        for row in rows[1:]:
                            cells = row.find_elements(By.XPATH, ".//td")
                            if len(cells) > 1:
                                data_obj = dict()
                                data_obj['name'] = cells[0].text.strip()
                                data_obj['status'] = cells[1].text.strip()
                                data_obj['expiration_date'] = change_date_format(
                                    cells[2].text.strip()) if cells[2].text else ''
                                data_names.append(data_obj)

                        if len(data_names) > 0:
                            assumed_name_obj = dict()
                            assumed_name_obj['type'] = "assumed_name"
                            assumed_name_obj['data'] = data_names
                            addtional_detail.append(assumed_name_obj)

                except NoSuchElementException:
                    print("Element not found.")

                history_btn = driver.find_element(
                    By.XPATH, "//*[@id='ctl00_MainContent_menuTabsn1']/table/tbody/tr/td/a")
                history_btn.click()
                time.sleep(4)
                fillings_detail = list()
                try:
                    history_div = driver.find_element(
                        By.ID, "ctl00_MainContent_divHistorySummary")
                    table_element = history_div.find_element(
                        By.XPATH, ".//table")
                    table_bodies = table_element.find_elements(
                        By.XPATH, ".//tbody")

                    if len(table_bodies) > 0:
                        for table_body in table_bodies[1:]:
                            rows = table_body.find_elements(By.XPATH, ".//tr")

                            file_history = dict()
                            if len(rows) > 1:
                                cells = rows[0].find_elements(
                                    By.XPATH, ".//td")

                                file_history['filing_type'] = cells[0].text.strip()
                                file_history['date'] = change_date_format(
                                    cells[1].text.strip()) if cells[1].text else ''
                                file_history['meta_detail'] = {
                                    "image_number": cells[2].text.strip()
                                } if cells[2].text else {}
                                cells[3].find_element(
                                    By.XPATH, ".//a").click() if cells[3].text != " " else ''

                                cells_ = rows[1].find_elements(
                                    By.XPATH, ".//td")

                                description = ''
                                div_elements = cells_[0].find_elements(
                                    By.XPATH, '//div[b]')
                                for div in div_elements:
                                    text_with_b_tags = div.get_attribute(
                                        'innerHTML')
                                    description += text_with_b_tags.replace('<b>', '').replace(
                                        '</b>', '') + "," if text_with_b_tags else ''
                                file_history['description'] = description
                                fillings_detail.append(file_history)

                            else:
                                cells = rows[0].find_elements(
                                    By.XPATH, ".//td")
                                file_history['filing_type'] = cells[0].text.strip()
                                file_history['date'] = change_date_format(
                                    cells[1].text.strip()) if cells[1].text else ''
                                file_history['meta_detail'] = {
                                    "image_number": cells[2].text.strip()
                                } if cells[2].text else {}
                                file_history['description'] = ''
                                fillings_detail.append(file_history)
                except NoSuchElementException:
                    print("Element not found.")

                people_list = list()
                registered_agent_btn = driver.find_element(
                    By.XPATH, "//*[@id='ctl00_MainContent_menuTabsn2']/table/tbody/tr/td/a")
                registered_agent_btn.click()
                time.sleep(4)

                try:
                    people = dict()
                    people['designation'] = "registered_agent"

                    people['name'] = driver.find_element(By.ID, "ctl00_MainContent_txtAgentName").text.strip(
                    ).replace("'", "''") if driver.find_element(By.ID, "ctl00_MainContent_txtAgentName") else ''

                    people['address'] = driver.find_element(By.ID, "ctl00_MainContent_txtAgentAddress").text.strip().replace(
                        "'", "''").replace('\n', ' ') if driver.find_element(By.ID, "ctl00_MainContent_txtAgentAddress") else ''

                    people_list.append(people) if people['name'] else ''

                except NoSuchElementException:
                    print("Element not found.")

                OBJ['fillings_detail'] = fillings_detail
                OBJ['additional_detail'] = addtional_detail
                OBJ['people_detail'] = people_list

                OBJ = tennessee_crawler.prepare_data_object(OBJ)
                ENTITY_ID = tennessee_crawler.generate_entity_id(
                    OBJ.get('registration_number'), OBJ['name'])
                NAME = OBJ['name']
                BIRTH_INCORPORATION_DATE = ""
                ROW = tennessee_crawler.prepare_row_for_db(
                    ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                tennessee_crawler.insert_record(ROW)

            i += 1

        return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE
    except Exception as e:
        print(f"Error occured in record number:{i},", e)
        driver.refresh()
        crawl(i)


try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl(PAGE)
    tennessee_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    tennessee_crawler.db_log(log_data)
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    tennessee_crawler.db_log(log_data)
    display.stop()
