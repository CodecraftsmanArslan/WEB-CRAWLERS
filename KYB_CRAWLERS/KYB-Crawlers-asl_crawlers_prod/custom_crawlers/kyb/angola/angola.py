"""Import required library"""
import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from datetime import datetime
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


meta_data = {
    'SOURCE': 'GUICHÉ ÚNICO DA EMPRESA',
    'COUNTRY': 'Angola',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://gue.gov.ao/portal/publicacao?empresa=____",
                      "Source Description": "The Company's Single Guiché is a public, special and inter-organic service, endowed with legal personality, with administrative, financial and patrimonial autonomy, supervised by the Ministry of Justice and Human Rights, whose purpose is to speed up the incorporation processes, alteration, extinction and similar acts, of commercial companies, sole traders and cooperatives."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://gue.gov.ao/portal/publicacao?empresa=____'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Angola Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

angola_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = angola_crawler.get_requests_helper()
selenium_helper = angola_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)

start_page = int(sys.argv[1]) if len(sys.argv) > 1 else 1
end_page = int(sys.argv[2]) if len(sys.argv) > 2 else 12687

def crawl():
    for i in range(start_page, end_page):
        while True:
            URL = f"https://gue.gov.ao/portal/publicacao?empresa=____&page={i}"
            company_links_response = request_helper.make_request(url=URL, method="GET")
            STATUS_CODE = company_links_response.status_code
            DATA_SIZE = len(company_links_response.content)
            if not company_links_response:
                print("No Initial Response", company_links_response)
                time.sleep(10)
                continue
            if company_links_response.status_code == 200:
                data = company_links_response.text
                break
            else:
                print(f"Initial Error Code: {company_links_response.status_code}")
                time.sleep(10)
        
        links_soup = BeautifulSoup(data, "lxml")
        links_table = links_soup.find("table")
        links_table_rows = links_table.find_all("tr")
        for links_table_row in links_table_rows:
            company_link = links_table_row.find("a").get("href")
            nif_number= links_table_row.find_all("td")[2].text.strip()
            driver.get(company_link)
            time.sleep(8)
            if "Error" in driver.page_source:
                print(f"No record found for: {nif_number}")
                continue
            if len(driver.find_elements(By.ID, ':1.container')) > 0:
                translation_iframe = driver.find_element(By.ID, ':1.container')
                if translation_iframe:
                    driver.switch_to.frame(translation_iframe)
                    time.sleep(2)
                    if len(driver.find_elements(By.XPATH, '//a[@title="Close"]')) == 0:
                        continue
                    close_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[@title="Close"]')))
                    close_button.click()
                    driver.switch_to.default_content()
                    time.sleep(2)
            iframe_element = driver.find_element(By.ID, "myPDF_ifr")
            if iframe_element:
                driver.switch_to.frame(iframe_element)
                time.sleep(3)
                get_data(nif_num=nif_number, page_num=i)       

    return STATUS_CODE, DATA_SIZE

def get_data(nif_num, page_num):
    data_soup = BeautifulSoup(driver.page_source, "html.parser")

    print(f"Scraping data for: {nif_num} on page: {page_num}")
    all_additional_data = []
    all_people_data = []

    all_tables = data_soup.find_all("table")
    for table in all_tables:
        check = table.find("tr").find("td").text
        if "MATRÍCULA" in check:
            matricula_data_ = table.find_all("tr")[1].find("td").text.strip()
            keywords_1 = ["Matrícula:", "Firma:", "NIF:", "Company:","Registration:"]
            matricula_result = {}
            for keyword in keywords_1:
                if keyword in matricula_data_:
                    start = matricula_data_.index(keyword) + len(keyword)
                    end = matricula_data_.find(keywords_1[keywords_1.index(keyword) + 1]) if keywords_1.index(keyword) + 1 < len(keywords_1) else None
                    value = matricula_data_[start:end].strip()
                    matricula_result[keyword] = value
            registration_number = matricula_result.get("Matrícula:", "").replace("=", "").replace("\"", "")
            company_name = matricula_result["Firma:"].replace("=", "").replace("\"", "") if 'Firma:' not in matricula_result else matricula_result.get('Company:','').replace("=", "").replace("\"", "")
            registration_detail = matricula_result.get("NIF:", "").replace(nif_num, "").replace("=", "").replace("\"", "").strip()
            company_tax_number = matricula_result.get("NIF:", "").replace(registration_detail, "").replace("=", "").replace("\"", "")

    for table2 in all_tables:
        check2 = table2.find("tr").find("td").text
        if "INSCRIÇÃO" in check2:
            try:
                inscricao_data = table2.find_all("tr")[1].find("td").text.strip()
            except:
                inscricao_data = ""
            initial_pattern = r'Insc\.1.*?FORMA DE OBRIGAR:[^.]*'
            initial_match = re.search(initial_pattern, inscricao_data, re.DOTALL)
            if initial_match:
                initial_data = initial_match.group(0)
            else:
                initial_data = ""

            if initial_data:
                initial_data_dict = {}
                initial_keys = {
                    "SEDE": r"SEDE:(.*?)OBJECTO:",
                    "OBJECTO": r"OBJECTO:(.*?)CAPITAL:",
                    "CAPITAL": r"CAPITAL:(.*?)SÓCIOS E QUOTAS:",
                    "SÓCIOS E QUOTAS": r"SÓCIOS E QUOTAS:(.*?)GERÊNCIA:",
                    "GERÊNCIA": r"GERÊNCIA:(.*?)FORMA DE OBRIGAR:",
                    "FORMA DE OBRIGAR": r"FORMA DE OBRIGAR:(.*?)(?=\n|$)",
                    "ADMINISTRAÇÃO": r"ADMINISTRAÇÃO:(.*?)FORMA DE OBRIGAR:"
                }
                for key, key_pattern in initial_keys.items():
                    data_match = re.search(key_pattern, initial_data, re.DOTALL | re.MULTILINE)
                    if data_match:
                        value = data_match.group(1).strip().replace("FIM DA EXTRACTAÇÃO.", "")
                        initial_data_dict[key] = value
                headquarters = initial_data_dict.get("SEDE", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "")
                service = initial_data_dict.get("OBJECTO", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "")
                forma_obrigar = initial_data_dict.get("FORMA DE OBRIGAR", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "") if initial_data_dict.get("FORMA DE OBRIGAR", "") else ""
                administration_value = initial_data_dict.get("ADMINISTRAÇÃO", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "") if initial_data_dict.get("ADMINISTRAÇÃO", "") else ""
                shareholder_dict = {
                    "type": "UBOs_info",
                    "data": [
                        {
                            "description": initial_data_dict.get("SÓCIOS E QUOTAS", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "")
                        }
                    ]
                }
                if initial_data_dict.get("SÓCIOS E QUOTAS", ""):
                    all_additional_data.append(shareholder_dict)

                capital_dict = {
                    "type": "capital_info",
                    "data": [
                        {
                            "capital": initial_data_dict.get("CAPITAL", "").replace("\n", "").replace("  ", "").replace("=", "").replace("\"", "")
                        }
                    ]
                }
                if initial_data_dict.get("CAPITAL", ""):
                    all_additional_data.append(capital_dict)

                other_pattern = r'(Insc\.\d+ \w+\/\d+|Ap\.\d+ \/ \d+)'
                paragraphs = re.split(other_pattern, inscricao_data)
                all_texts = []
                paragraphs = [paragraph.replace(initial_data, "").replace("\n", "").replace("  ", "").strip() for paragraph in paragraphs if paragraph.strip()]
                for paragraph in paragraphs:
                    split_texts = paragraph.replace('Ap.', "\nAp.").replace("Insc.", "\nInsc.").split("\n")
                    for split_text in split_texts[1:]:
                        if len(split_text) > 15:
                            split_text = split_text.replace("=", "").replace("\"", "")
                            all_text_dict = {
                                "description": split_text
                            }
                            if split_text:
                                all_texts.append(all_text_dict)

                split_dict = {
                    "type": "relative_details",
                    "data": all_texts
                }
                if len(all_texts) > 0:
                    all_additional_data.append(split_dict)
    try:
        headquarters = headquarters
        registration_number = registration_number
        company_name = company_name
    except:
        headquarters, service,forma_obrigar,  administration_value, registration_number, company_name, company_tax_number, registration_detail="","","","","","", "",[]
    OBJ = {
        "registration_number": registration_number,
        "name": company_name,
        "tax_number": company_tax_number,
        "reg_details": registration_detail,
        "addresses_detail": [
            {
                "type": "headquarters_address",
                "address": headquarters
            }
        ],
        "services": service,
        "additional_detail": all_additional_data,
        "obligtion_criteria": forma_obrigar,
        "people_detail": all_people_data,
        "administration": administration_value
    }

    OBJ = angola_crawler.prepare_data_object(OBJ)
    ENTITY_ID = angola_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = angola_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    angola_crawler.insert_record(ROW) 


try:
    STATUS_CODE, DATA_SIZE =  crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    angola_crawler.db_log(log_data)
    angola_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    angola_crawler.db_log(log_data)
