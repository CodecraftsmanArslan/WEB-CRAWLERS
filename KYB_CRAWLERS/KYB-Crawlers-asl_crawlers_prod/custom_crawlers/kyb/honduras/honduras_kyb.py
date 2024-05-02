"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil import parser
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import urllib.parse
import base64

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Chamber of Commerce, Industry, and Tourism (CCIT)',
    'COUNTRY' : 'Honduras',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://rmprd.registrosccit.hn/scripts/consultaPublica.php", 
                        "Source Description": "The CCIT facilitates the registration process for new businesses, including companies, partnerships, and sole proprietorships. This involves collecting and processing relevant information, issuing registration numbers or certificates, and maintaining an official record of registered businesses."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://rmprd.registrosccit.hn/scripts/consultaPublica.php'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Honduras",
}

honduras_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = honduras_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)
def get_link(href_value):
    # Extract the parameters from the JavaScript function call
    parameters = href_value.split("('", 1)[1].rsplit("')", 1)[0]

    # Decode the base64-encoded data
    decoded_parameters = base64.b64decode(parameters).decode('utf-8')

    # Parse the decoded parameters to get the actual link
    parsed_parameters = urllib.parse.parse_qs(decoded_parameters)
    link = parsed_parameters.get('src', [''])[0]
    return link
def get_page_data(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'table-condensed'})
    if soup.find('tbody') is None:
        return None
    rows = table.select('tbody tr')
    respose = {}
    for row in rows:
        columns = row.select('td')
        key = columns[0].text.strip()
        value = columns[1].text.strip()
        respose[key] = value
    fillings_detail = []
    card_elements = soup.select(".card.bg-light")
    for card_element in card_elements:
        fields = card_element.select('div.card-header strong')
        values = card_element.select_one('div.card-header').text.split('***')

        data = {}
        for field, value in zip(fields, values):
            key = field.text.strip().rstrip(':')
            data[key] = value.strip().split(": ")
            data[key] = data[key][1].replace("/", "-").strip().replace("%", "%%") if len(data[key]) > 1 else value
        
            data['description'] = card_element.select_one('div.card-body p small').text.strip().replace('Noticia: ', '').replace("%", "%%").split('***')[0].strip()
            data['filling_person'] = card_element.select_one('div.card-body p small').text.strip().replace('Noticia: ', '').replace("%", "%%").split('Exequatur:')[-1].strip()
            data['file_url'] = get_link(card_element.select_one(".card-body a")['href']) if card_element.select_one(".card-body a") is not None else ""
        # Key mapping
        key_mapping = {
            'Libro-tomo-registro': 'book_number',
            'Fecha registro': 'date',
            'Nro. Documento': 'filing_code',
            'Tipo documento': 'filing_type',
            'Acto': 'title',
            'description': 'description',
            'filling_person': 'filling_person',
            'file_url': 'file_url'
        }

        mapped_data = {key_mapping[key]: value for key, value in data.items()}
        if 'book_number' in mapped_data and mapped_data['book_number'] is not None and mapped_data['book_number'] != "":
            mapped_data['meta_detail'] = {'book_number': mapped_data['book_number'], "filling_person":mapped_data['filling_person']}
            print(mapped_data)
            del mapped_data['book_number'], mapped_data['filling_person']

        fillings_detail.append(mapped_data)
    respose['fillings_detail'] = fillings_detail
    return respose
try:
    url = "https://rmprd.registrosccit.hn/scripts/consultaPublica.php"
    driver.get(url)
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for i in range(start_number, 85759):
        print("Record No:", i)
        wait = WebDriverWait(driver, 10)
        input_box = wait.until(EC.presence_of_element_located((By.ID, "_matricula")))
        input_box.clear()
        input_box.send_keys(i)
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-secondary")))
        search_button.click()
        data = get_page_data(driver) 
        if data is None:
            driver.back()
            continue
        DATA = {
            "registration_number": data.get("Matrícula"),
            "name": data.get("Razón social / Denominación Social / Nombre").replace("%", "%%") if data.get("Razón social / Denominación Social / Nombre") is not None else "",
            "type": data.get("Persona jurídica").replace("%", "%%") if data.get("Persona jurídica") is not None else "",
            "incorporation_date": data.get("Fecha constitución").replace("/", "-") if data.get("Fecha constitución") is not None else "",
            "fillings_detail": data.get("fillings_detail")
        }

        ENTITY_ID = honduras_crawler.generate_entity_id(company_name=data.get("Razón social / Denominación Social / Nombre"), reg_number=data.get("Matrícula"))
        BIRTH_INCORPORATION_DATE = ''
        DATA = honduras_crawler.prepare_data_object(DATA)
        ROW = honduras_crawler.prepare_row_for_db(ENTITY_ID, data.get("Razón social / Denominación Social / Nombre"), BIRTH_INCORPORATION_DATE, DATA)
        honduras_crawler.insert_record(ROW)
        time.sleep(2)
        driver.back()


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    honduras_crawler.db_log(log_data)
    honduras_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    honduras_crawler.db_log(log_data)
