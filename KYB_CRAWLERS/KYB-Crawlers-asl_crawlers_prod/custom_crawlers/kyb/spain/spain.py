"""Import required library"""
import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
import time
from CustomCrawler import CustomCrawler
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from dateutil import parser
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'Comisión Nacional del Mercado de Valores (CNMV) - Ministry of Economy and Finance',
    'COUNTRY': 'Spain',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://sede.registradores.org/site/invitado/mercantil/busqueda",
                      "Source Description": "The CNMV is the body responsible for the supervision and inspection of Spanish securities markets and the activity of all those involved in them. The aim of the CNMV is to ensure the transparency of Spanish securities markets and the correct formation of prices, as well as the protection of investors. The CNMV, in the exercise of its powers, receives a large volume of information from and on market participants, much of which appears in its Official Registers and is public."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://sede.registradores.org/site/invitado/mercantil/busqueda'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Spain Official Registry" 
}

spain_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

WAIT_TIMEOUT = 10
SEARCH_TIMEOUT = 3

selenium_helper = spain_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=True, timeout=300)
action = ActionChains(driver=driver)
url = "https://sede.registradores.org/site/home"

alphabets = ["A", "B", "G", "X", "OA", "N", "W", "J"]


start_alphabet = ARGUMENT[1][0].capitalize() if len(ARGUMENT) > 1 else alphabets[0]
start_number = int(''.join(filter(str.isdigit, ARGUMENT[1]))) if len(ARGUMENT) > 1 else 100
start_number = max(start_number, 100)  # Ensure the start number is at least 100
start_number = str(start_number).zfill(8)

end_number = 99999999

def identify_captcha(driver):
    try:
        captcha = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
        if captcha:
            print("Captcha Found. Trying to resolve...")
            captcha_not_solved = True
            while captcha_not_solved:
                iframe_element = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                driver.switch_to.frame(iframe_element)
                wait = WebDriverWait(driver, 30000)
                checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
                if checkbox:
                    driver.switch_to.default_content()
                    captcha_not_solved = False
            print("Captcha Solved!")
            time.sleep(2)
    except NoSuchElementException:
        print("Captcha not found.")

def open_search_page():
    driver.get(url=url)
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/site/mercantil"][@class="link "]'))).click()
    time.sleep(SEARCH_TIMEOUT)
    search_by_company_button = driver.find_element(By.XPATH, '//a[text()="Buscar por sociedad"]')
    search_by_company_button.click()
    identify_captcha(driver=driver)
    search_input_button = driver.find_element(By.XPATH, '//label/span[text()="NIF"]')
    search_input_button.click()
    crawl()

def crawl():
     for alphabet in alphabets:
        if len(ARGUMENT) > 1 and start_alphabet != alphabet:
            continue
        for i in range(int(start_number), end_number):
            search_query = alphabet+str(i).zfill(8)
            search_field = driver.find_element(By.XPATH, '//input[@type="text"]')
            search_field.clear()
            action.scroll_to_element(search_field).double_click(search_field).send_keys(Keys.DELETE).perform()
            time.sleep(1)
            search_field.send_keys(search_query)
            time.sleep(1)
            search_field.send_keys(Keys.RETURN)
            time.sleep(3)
            if "No se han encontrado resultados para los datos de búsqueda indicados." in driver.page_source:
                print(f"No record found for {search_query}")
                continue
            print(f"Scraping data for {search_query}")
            get_data()

def get_data():
    time.sleep(4)
    data_soup = BeautifulSoup(driver.page_source, "html.parser")
    data_table = data_soup.find("table")
    all_rows = data_table.find_all("tr")
    for row in all_rows[1:]:
        all_cells = row.find_all("td")
        name_ = all_cells[0].text.strip()
        registration_number =all_cells[1].text.strip()
        city = all_cells[2].text.strip()
        status_ = all_cells[3].text.strip()
        OBJ = {
            "name": name_,
            "registration_number": registration_number,
            "jurisdiction": city,
            "status": status_
        }
        OBJ = spain_crawler.prepare_data_object(OBJ)
        ENTITY_ID = spain_crawler.generate_entity_id(OBJ)
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ''
        ROW = spain_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
        spain_crawler.insert_record(ROW)
        time.sleep(1)

try:
    open_search_page()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    spain_crawler.db_log(log_data)
    spain_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    spain_crawler.db_log(log_data)
    display.stop()