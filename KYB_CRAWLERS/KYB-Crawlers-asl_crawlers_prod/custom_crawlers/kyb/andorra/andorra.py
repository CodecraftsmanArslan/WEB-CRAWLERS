"""Import required library"""
import sys, os, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
import math
from datetime import datetime
import pdfplumber
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv
WINDOW_SIZE = '1920,1080'
FILE_PATH = os.path.dirname(os.getcwd()) + "/andorra/pdf_file"

URL = "https://aplicacions.govern.ad/OMPA/RegistreResultats"

meta_data = {
    'SOURCE': 'OFFICE OF TRADEMARKS AND PATENTS OF THE PRINCIPALITY OF ANDORRA',
    'COUNTRY': 'Andorra',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://aplicacions.govern.ad/OMPA/RegistreResultats",
                      "Source Description": "Businesses seeking to register a trademark or a patent should contact the Andorran Trademarks Office and Patents Office."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://aplicacions.govern.ad/OMPA/RegistreResultats'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Andorra Official Registry"
}

andorra_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0, size=(800, 600))
display.start()

selenium_helper = andorra_crawler.get_selenium_helper()
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument("--dns-prefetch-disable")
options.add_argument("--dns-server=8.8.8.8")
options.add_argument(f'--window-size={WINDOW_SIZE}')
prefs = {"download.default_directory": FILE_PATH,
         "download.prompt_for_download": False,
         "plugins.always_open_pdf_externally": True}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout = 300

start_page = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 1

driver.get(url=URL)
WebDriverWait(driver, 120).until(EC.presence_of_element_located(
    (By.XPATH, '//h1[text()="RESULTATS DE LA CONSULTA"]')))
time.sleep(5)

# If the crawler is resumed, it will skip already crawled pages


def skip_pages():
    if start_page > 1:
        print(f"Skipping to page no: {start_page}")
        for i in range(start_page - 1):
            WebDriverWait(driver, 120).until(EC.presence_of_element_located(
                (By.XPATH, '//button[@aria-label="go to next page"]')))
            next_page_button = driver.find_element(
                By.XPATH, '//button[@aria-label="go to next page"]')
            next_page_button.click()
            print(f"Page Number: {i+1} skipped.")
        time.sleep(5)

# Once the data is scraped from the PDF it will delete it.


def delete_file(file_number):
    time.sleep(3)
    try:
        os.remove(f"{FILE_PATH}/Marca_{file_number}.pdf")
    except:
        os.remove(f"{FILE_PATH}/Marca_{file_number}(1).pdf")

# Opens, the website and download PDFs one by one


def crawl():
    no_of_results = int(driver.find_element(
        By.XPATH, '//span[contains(text(),"de")]/following-sibling::span').text)
    if no_of_results % 10 == 0:
        no_of_pages = int(no_of_results/10)
    else:
        no_of_pages = math.ceil(no_of_results/10)
    skip_pages()
    for page in range(start_page, no_of_pages+1):
        print(f"Scrapping page no: {page}")
        no_of_companies = len(driver.find_elements(
            By.XPATH, '//a[@title="Document de marca"]'))
        for i in range(no_of_companies):
            soup = BeautifulSoup(driver.page_source, "html.parser")
            data_table = soup.find("tbody")
            all_rows = data_table.find_all("tr")
            data_row = all_rows[i]
            all_data = data_row.find_all("td")
            registration_number = all_data[1].text.strip(
            ) if all_data[1] else ""
            registration_date = all_data[2].text.strip() if all_data[2] else ""
            classes_of_products_and_services = all_data[3].text.strip(
            ) if all_data[3] else ""
            name_ = all_data[4].text.strip() if all_data[4] else ""
            status_ = all_data[5].text.strip() if all_data[5] else ""
            expiry_date = all_data[6].text.strip() if all_data[6] else ""
            all_companies = driver.find_elements(
                By.XPATH, '//a[@title="Document de marca"]')
            the_company = all_companies[i]
            the_company.click()
            WebDriverWait(driver, 300).until(EC.presence_of_element_located(
                (By.XPATH, '//div[text()="Document descarregat."]')))
            print("File Downloaded!!")
            get_data(file_number=registration_number, registration_date=registration_date, registration_number=registration_number,
                     classess=classes_of_products_and_services, name=name_, status=status_, expiry=expiry_date)
        try:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@aria-label="go to next page"]')))
            next_page_button = driver.find_element(
                By.XPATH, '//button[@aria-label="go to next page"]')
            next_page_button.click()
            time.sleep(10)
        except Exception as e:
            tb = traceback.format_exc()
            print(e, tb)
            print("No more pages!!")
            break

# Opens the PDF, extract the required data and store it in Database.


def get_data(file_number, registration_number, registration_date, classess, name, status, expiry):
    print(f"Scrapping data of Marca_{file_number}.pdf")
    time.sleep(5)
    path = f"{FILE_PATH}/Marca_{file_number}.pdf"
    search_keys = ["Denominació social", "MANDATARIO ACREDITADO", "Forma jurídica", "Data del registre", "Número del registre",
                   "País en què s'ha efectuat el registre", "and/or services for which priority right is claimed", "DIRECCIÓN DEL TITULAR"]
    data_dict = {}
    people_detail = []
    additional_detail = []
    filings_detail = []
    pdf_text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            pdf_text += page_text + "\n"
    lines = pdf_text.split('\n')
    for search_key in search_keys:
        for i in range(len(lines)):
            if search_key in lines[i]:
                if i + 1 < len(lines):
                    data_dict[search_key] = lines[i + 1]
                break

    number_16 = "INSCRIPCIONES EN EL REGISTRO DE MARCAS"
    for page in pdf.pages:
        for n in range(len(lines)):
            if number_16 in lines[n]:
                if n + 1 < len(lines):
                    data_dict[number_16] = lines[n+1:-1]
                break

    number_8 = "WHICH TRADEMARK REGISTRATION IS SOUGHT"
    for page in pdf.pages:
        for p in range(len(lines)):
            if number_8 in lines[p]:
                if p + 1 < len(lines):
                    data_dict[number_8] = lines[p+1:-1]
                    break

    people_dict = {
        "designation": "owner",
        "name": data_dict.get("Denominació social", ""),
        "address": data_dict.get("DIRECCIÓN DEL TITULAR", ""),
        "meta_detail": {
            "type": data_dict.get("Forma jurídica", "")
        }
    }
    if data_dict.get("Denominació social", "") or data_dict.get("DIRECCIÓN DEL TITULAR", "") or data_dict.get("Forma jurídica", ""):
        people_detail.append(people_dict)

    power_of_attor = data_dict.get("MANDATARIO ACREDITADO", "") if data_dict.get(
        "MANDATARIO ACREDITADO", "") else ""

    reg_data = []
    if number_8 in data_dict:
        all_reg_prod = data_dict[number_8]
        for prod in all_reg_prod[2:]:
            if str(prod).startswith("GEN"):
                nace_code = prod.split(" ")[0].strip()
                nace_detail = prod.replace(nace_code, "").strip()
                reg_pr_dict = {
                    "nace_code": nace_code,
                    "nace_detail": nace_detail
                }
                if nace_code or nace_detail:
                    reg_data.append(reg_pr_dict)

        reg_prod_dict = {
            "type": "nace_details",
            "data": reg_data
        }
        additional_detail.append(reg_prod_dict)

    property_right_dict = {
        "type": "property_right_claim_info",
        "data": [
            {
                "country_where_the_registration_was_made": data_dict.get("País en què s'ha efectuat el registre", ""),
                "date_of_registration": data_dict.get("Data del registre", ""),
                "registration_number": data_dict.get("Número del registre", ""),
                "products_services_for_which_priorty_is_claimed": data_dict.get("and/or services for which priority right is claimed", "")
            }
        ]
    }
    if data_dict.get("País en què s'ha efectuat el registre", "") or data_dict.get("Data del registre", "") or data_dict.get("Número del registre", "") or data_dict.get("and/or services for which priority right is claimed", ""):
        additional_detail.append(property_right_dict)

    if number_16 in data_dict:
        all_filings = data_dict[number_16]
        for filing in all_filings[:-1]:
            filing_dict = {
                "date": filing.split(":")[0].strip(),
                "title": filing.split(":")[-1].strip()
            }
            filings_detail.append(filing_dict)

    OBJ = {
        "registration_number": registration_number,
        "registration_date": registration_date,
        "classes_of_products_and_services": classess,
        "name": name,
        "status": status,
        "expiry_date": expiry,
        "people_detail": people_detail,
        "power_of_attorney_number": power_of_attor,
        "additional_detail": additional_detail,
        "fillings_detail": filings_detail
    }

    OBJ = andorra_crawler.prepare_data_object(OBJ)
    ENTITY_ID = andorra_crawler.generate_entity_id(
        OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%", "%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = andorra_crawler.prepare_row_for_db(
        ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    andorra_crawler.insert_record(ROW)

    delete_file(file_number=file_number)
    print("File Deleted!")
    print("Downloading Next File...")


try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    andorra_crawler.db_log(log_data)
    andorra_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    andorra_crawler.db_log(log_data)
    display.stop()
