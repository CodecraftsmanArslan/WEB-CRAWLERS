"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Utah.gov',
    'COUNTRY': 'Utah',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://secure.utah.gov/bes/index.html",
                      "Source Description": "The Utah.gov  serves as the official online portal for the state of Utah, USA. It provides a wide range of services, resources, and information related to government, business, education, healthcare, and more. The website offers a user-friendly interface that allows individuals, businesses, and organizations to access important services and conduct various transactions."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://secure.utah.gov/bes/index.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Utah Official Registry",
}

utah_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

selenium_helper = utah_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False,Nopecha=True, user_agent=False, proxy=True, timeout=500)

wait = WebDriverWait(driver, 10)

def get_data(driver, page_number):
    arr = []
    url = "https://secure.utah.gov/bes/details.html?id="
    for i in range(0, 50):
        driver.get(url + str(i))
        name = driver.find_element(
            By.XPATH, '//h2[@class = "entityDetail"]').text.replace("%", "%%").strip()
        print(f"Scraping data for {name} on page # {page_number + 1}")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        registration_number = soup.find("b", string="Entity Number:").nextSibling.text.strip(
        ) if soup.find("b", string="Entity Number:").nextSibling is not None else ""

        company_type = soup.find('b', string="Company Type:").nextSibling.text.strip(
        ) if soup.find('b', string="Company Type:").nextSibling is not None else ""

        try:
            address_detail = ((soup.find('b', string="Address:").nextSibling.text.strip(
            ).split("\n")[0].strip()) + ", " + (soup.find('b', string="Address:").nextSibling.text.strip(
            ).split("\n")[1].strip())) if soup.find('b', string="Address:").nextSibling is not None else ""
        except IndexError:
            address_detail = (soup.find('b', string="Address:").nextSibling.text.strip(
            ).split("\n")[0].strip())
        else:
            additional_detail = ""

        address_detail = address_detail.replace("%", "%%")

        jurisdiction = soup.find('b', string="State of Origin:").nextSibling.text.strip(
        ) if soup.find('b', string="State of Origin:").nextSibling is not None else ""

        agent_name = soup.find('b', string="Registered Agent:").nextSibling.nextSibling.text.replace("%", "%%").strip(
        ) if soup.find('b', string="Registered Agent:") is not None else ""

        try:
            agent_address = (soup.find('b', string="Registered Agent Address:").nextSibling.nextSibling.nextSibling.text.strip(
            ).split("\n")[0].strip()) + ", " + (soup.find('b', string="Registered Agent Address:").nextSibling.nextSibling.nextSibling.text.strip(
            ).split("\n")[1].strip()) if soup.find('b', string="Registered Agent Address:") is not None else ""
        except IndexError:
            agent_address = soup.find('b', string="Registered Agent Address:").nextSibling.nextSibling.nextSibling.text.strip(
            ) if soup.find('b', string="Registered Agent Address:") is not None else ""

        agent_address = agent_address.replace("%", "%%")

        status = soup.find('b', string="Status:").nextSibling.text.strip(
        ) if soup.find('b', string="Status:").nextSibling is not None else ""

        font_tags = soup.find_all('font', color='#333333')

        if len(font_tags) >= 2:
            naics_code = font_tags[0].next_sibling.strip(
            ) if font_tags[0].next_sibling is not None else ""
            naics_title = font_tags[1].next_sibling.strip(
            ) if font_tags[1].next_sibling is not None else ""
        else:
            naics_code = ""
            naics_title = ""

        registration_date = soup.find(
            'b', string="Registration Date:").nextSibling.text.strip(
        ).replace("/", "-") if soup.find('b', string="Registration Date:").nextSibling is not None else ""

        last_renewed = soup.find('b', string="Last Renewed:").nextSibling.text.strip().replace("/", "-") if soup.find(
            'b', string="Last Renewed:").nextSibling is not None else ""

        next_renewal = soup.find('b', string="Renew By:").nextSibling.text.strip(
        ).replace("/", "-") if soup.find('b', string="Renew By:") and soup.find('b', string="Renew By:").nextSibling is not None else ""

        aliases = soup.find('h4', string="Doing Business As").nextSibling.text.strip(
        ) if soup.find('h4', string="Doing Business As") is not None else ""

        h4_element = soup.find('h4', string='Former Business Names')
        if h4_element:
            p_element = h4_element.find_next('p')
            previous_business_name = p_element.get_text(strip=True)

        else:
            previous_business_name = ""

        filled_documents_page = driver.find_element(
            By.XPATH, '//form/a[contains(text(), "View Filed Documents")]')
        filled_documents_page.click()

        time.sleep(1)
        filing_detail = []
        try:
            detail_page = BeautifulSoup(driver.page_source, "html.parser")
            table_ = detail_page.find('table', {"id": "images"})
            if table_ is not None:
                table_rows = table_.find_all('tr')
                if table_rows is not None:
                    for row in table_rows[1:]:
                        tds = row.find_all('td')
                        item = {
                            "filing_code": tds[0].text,
                            "date": tds[1].text,
                            "filing_type": tds[2].text,
                        }
                        filing_detail.append(item)
        except:
            filing_detail = []

        additional_detail = []
        if naics_title and naics_code != "":
            code_dict = {
                "type": "naics_code",
                        "data": [
                            {
                                "code": naics_code,
                                "name": naics_title
                            }
                        ]
            }
            additional_detail.append(code_dict)

        OBJ = {
            "name": name.replace("\"", ""),
            "registration_number": registration_number,
            "type": company_type,
            "jurisdiction": jurisdiction,
            "status": status,
            "registration_date": registration_date,
            "last_renewed": last_renewed.replace("N-A", ""),
            "next_renewal": next_renewal.replace("N-A", ""),
            "aliases": aliases,
            "addresses_detail": [
                {
                    "type": "general_address",
                    "address": address_detail
                }
            ],
            "people_detail": [
                {
                    "name": agent_name,
                    "address": agent_address,
                    "designation": "registered_agent"
                }
            ],
            "additional_detail": additional_detail,
            "fillings_detail": filing_detail,

            "previous_names_detail": [
                {
                    "name": previous_business_name.replace("\"", "").replace("%", "%%")
                }
            ]
        }
        arr.append(OBJ)

    driver.back()

    all_searches = driver.find_element(
        By.XPATH, '//p/a[contains(text(),"<< Back to Search Results")]')
    all_searches.click()
    time.sleep(2)

    return arr

try:
    arguments = sys.argv
    DUMMY_COR = int(arguments[1]) if len(arguments)>1 else 1
    driver.get("https://secure.utah.gov/bes/index.html")
    time.sleep(5)
    search_box = driver.find_element(
        By.XPATH, '//input[@name = "businessName"]')
    search_box.send_keys("_")
    time.sleep(2)
    search_button = driver.find_element(By.ID, 'searchByNameButton')
    search_button.click()
    time.sleep(2)
    
    captcha_solved = True

    while captcha_solved:
        time.sleep(10)
        try:
            time.sleep(10)
            captcha_elements = driver.find_elements(By.CLASS_NAME, "g-recaptcha")
            for captcha in captcha_elements:
                if captcha:
                    selenium_helper.wait_for_captcha_to_be_solved(driver)
                    submit_btn = driver.find_element(By.ID, "ctl00_MainContent_Button1")
                    submit_btn.click()
                time.sleep(5)
            search_button = driver.find_element(By.ID, 'searchByNameButton')
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(10)
            pagination = driver.find_element(By.ID, 'pagination') if driver.find_element(By.ID, 'pagination') is not None else ""
            if pagination != "":
                captcha_solved = False
                break
        except NoSuchElementException:
            print("Captcha Element not found.")
            time.sleep(5)
            search_button = driver.find_element(By.ID, 'searchByNameButton')
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(10)
            try:
                pagination = driver.find_element(By.ID, 'pagination')
                if pagination:
                    captcha_solved = False
                    break
            except NoSuchElementException:
                captcha_solved = True

    time.sleep(5)

    for i in range(DUMMY_COR, 36818):
        print(f"page no {i+1} opening...")
        pagination = driver.find_element(By.ID, 'pagination')
        pages = pagination.find_elements(By.TAG_NAME, 'a')
        driver.execute_script("arguments[0].click();", pages[i])
        print(f"page no {i+1} opened.")
        result = get_data(driver, page_number=i)
        for data in result:
            ENTITY_ID = utah_crawler.generate_entity_id(company_name=data.get(
                "name"), reg_number=data.get("registration_number"))
            BIRTH_INCORPORATION_DATE = ''
            DATA = utah_crawler.prepare_data_object(data)
            ROW = utah_crawler.prepare_row_for_db(
                ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
            utah_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}

    utah_crawler.db_log(log_data)
    utah_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": 'fail',
                "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    utah_crawler.db_log(log_data)
    display.stop()

