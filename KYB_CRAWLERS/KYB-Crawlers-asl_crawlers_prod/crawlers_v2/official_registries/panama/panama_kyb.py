"""Import required library"""
import time
import sys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from pyvirtualdisplay import Display
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import traceback
from helper.helper import skip_pages, timestamp_to_str
from load_env.load_env import ENV
from CustomCrawler import CustomCrawler



meta_data = {
    'SOURCE': 'Registro Público de Panamá',
    'COUNTRY': 'Panama',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.rp.gob.pa/",
                      "Source Description": "This is the website of the Public Registry of Panama (Registro Público de Panamá in Spanish). The public registry is a government institution that manages and regulates public records related to different legal matters in Panama, such as property ownership, mortgages, and business registration. The website provides various services, including access to public registers, information about procedures, forms, and regulations. It also offers online services for businesses, such as online registration and payment systems, as well as tools for searching and obtaining information from the public records."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.rp.gob.pa/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Panama Official Registry "
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

panama_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = panama_crawler.get_requests_helper()


display = Display(visible=0, size=(800, 600))
display.start()

selinum_helper = panama_crawler.get_selenium_helper()
driver = selinum_helper.create_driver(headless=False, Nopecha=True)
URL = 'https://www.rp.gob.pa/'
driver.get(URL)
time.sleep(10)
selinum_helper.wait_for_captcha_to_be_solved(driver)


def get_listed_object(record):
    '''
    Description: This method prepares the data object.
    It constructs a structured dictionary from the input data for insertion into the database.

    @param record: A list containing data for the record.
    @return: A dictionary representing the data object.
    '''

    meta_detail = {}
    if timestamp_to_str(record[4]) != "":
        meta_detail['deed_date'] = timestamp_to_str(record[4])
    if record[5] != "":
        meta_detail['deed_number'] = record[5]

    additional_detail = []
    people_detail = []

    if record[3] != {}:
        people_detail.append(record[3])

    if record[8] is not None and record[8].strip() != "":
        people_detail.append({
            "name": record[8],
            "designation": "company, owner, or titleholder"
        })

    if record[9] != "":
        additional_detail.append({
            "type": "procedures_and_services",
            "data": [{
                "name": record[9].replace("\n", "")
            }]
        })

    if record[10] != "":
        additional_detail.append({
            "type": "payment_documents_detail",
            "data": [{
                "name": record[10].replace("\n", "")
            }]
        })

    if len(record[11]) != 0:
        additional_detail.append({
            "type": "processing_history",
            "data": record[11]
        })

    if len(record[12]) != 0:
        additional_detail.append({
            "type": "documents",
            "data": record[12]
        })

    if record[2] is not None and record[2] != "":
        people_detail.append({
            "name": record[2].replace("'", "''"),
            "designation": "registered_agent"
        })

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": "",
        "registration_number": record[0],
        "registration_date": timestamp_to_str(record[1]),
        "people_detail": people_detail,
        "meta_detail": meta_detail,
        "status": record[7],
        "dissolution_date": "",
        "industries": record[6],
        "crawler_name": "custom_crawlers.kyb.panama.panama_kyb",
        "country_name": "Panama",
        "additional_detail": additional_detail
    }

    return data_obj


def get_data(browser, search_term):
    """
    Retrieve and process data from a web page.

    This function retrieves data from a web page using a Selenium WebDriver and processes it. It iterates through multiple pages,
    extracts information from tables, and handles various elements like buttons, tables, and modals.

    Args:
        browser (WebDriver): An instance of the Selenium WebDriver for interacting with the web page.
        search_term (str): The search term or query used to retrieve the data.

    Returns:
        None: The function does not return a value. The processed data is stored in a database.

    """
    wait = WebDriverWait(browser, 30)
    page_count = skip_pages(browser)
    while True:
        try:
            page_count += 1
            row_count = 0
            print('page : ', page_count, "search term ", search_term)
            tables = wait.until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            rows = tables[1].find_elements(By.TAG_NAME, 'tr')

            for row in rows:

                row_count += 1
                try:
                    print('row: ', row_count)
                    tds = row.find_elements(By.TAG_NAME, 'td')
                    btn_element = tds[4].find_element(By.TAG_NAME, 'button')
                    btn_element.click()
                    details = wait.until(EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, 'dl-horizontal')))
                    dt_elements = details[0].find_elements(By.TAG_NAME, 'dt')
                    dd_elements = details[0].find_elements(By.TAG_NAME, 'dd')
                    key_value_pairs = {}
                    for dt, dd in zip(dt_elements, dd_elements):
                        key = dt.text.strip().replace("'", "''")
                        value = dd.text.strip().replace("'", "''")
                        key_value_pairs[key] = value

                    procedures_and_services = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[1]').text.replace(
                        "'", "''") if len(browser.find_elements(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[1]')) > 0 else ""
                    payment_documents_submitted = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[2]').text.replace(
                        "'", "''") if len(browser.find_elements(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[2]')) > 0 else ""

                    # Find the <div> element with the class "btn-group"
                    btn_group = browser.find_element(
                        By.CLASS_NAME, "btn-group")
                    # Find all the <button> elements within the <div> element
                    buttons = btn_group.find_elements(By.TAG_NAME, "button")

                    if len(buttons) > 1:

                        buttons[2].click()
                        try:
                            processing_history_table = []
                            table = wait.until(EC.presence_of_element_located(
                                (By.CLASS_NAME, 'table')))
                            rows = table.find_elements(By.XPATH, ".//tbody/tr")
                            for row in rows:
                                cells = row.find_elements(By.XPATH, ".//td")
                                if cells[0].text.strip().replace("'", "''") != "" and cells[1].text.strip().replace("'", "''") != "":
                                    row_data = {
                                        "action": cells[0].text.strip().replace("'", "''"),
                                        "date_and_time": timestamp_to_str(cells[1].text.strip().replace("'", "''"))
                                    }
                                    processing_history_table.append(row_data)
                        except:
                            pass

                        buttons[3].click()
                        try:
                            documents_table = []
                            table = wait.until(EC.presence_of_element_located(
                                (By.CLASS_NAME, 'table')))
                            rows = table.find_elements(By.XPATH, ".//tbody/tr")
                            for row in rows:
                                cells = row.find_elements(By.XPATH, ".//td")
                                href = ""
                                try:
                                    second_td = row.find_element(
                                        By.XPATH, "./td[2]")
                                    button = second_td.find_element(
                                        By.XPATH, ".//button[contains(@class, 'btn-link')]")
                                    button.click()
                                    time.sleep(3)
                                    # Find the anchor tag by its text using XPath
                                    anchor = browser.find_element(
                                        By.XPATH, "//a[contains(text(), 'Descargar Documento')]")
                                    # Retrieve the href attribute
                                    href = anchor.get_attribute("href")
                                    # Find the h3 tag with "Visor Documento" text
                                    h3_element = browser.find_element(
                                        By.XPATH, "//h3[contains(text(), 'Visor Documento')]")

                                    # Find the next sibling button
                                    button = h3_element.find_element(
                                        By.XPATH, "./following-sibling::button")

                                    # Click the button
                                    button.click()

                                except Exception as e:
                                    pass
                                if len(cells) > 0 and cells[0].text.strip().replace("'", "''") != "":
                                    row_data = {
                                        "document": cells[0].text.strip().replace("'", "''"),
                                        "file_url": href
                                    }
                                    documents_table.append(row_data)

                        except:
                            pass

                    browser.find_element(
                        By.CLASS_NAME, 'blazored-modal-close').click()
                    time.sleep(3)

                    registration_number = key_value_pairs.get(
                        "NÚMERO DE ENTRADA:")
                    incorporation_date = key_value_pairs.get("FECHA INGRESO:")
                    agent = key_value_pairs.get("PRESENTANTE:")

                    notary = {}
                    if key_value_pairs.get("NOTARIO:") or key_value_pairs.get("NOTARÍA:"):
                        notary = {
                            "type": "notary",
                            "name": key_value_pairs.get("NOTARIO:"),
                            "office_name": key_value_pairs.get("NOTARÍA:")
                        }

                    documentation_date = key_value_pairs.get(
                        "FECHA DE ESCRITURA:")
                    deed_number = key_value_pairs.get("NÚMERO DE ESCRITURA:")
                    industries = key_value_pairs.get("DESTINO:")
                    current_status = key_value_pairs.get("SITUACIÓN ACTUAL:")
                    people_detail = key_value_pairs.get(
                        "SOCIEDAD/DUEÑO/TITULAR:")

                    DATA = [
                        registration_number,
                        incorporation_date,
                        agent,
                        notary,
                        documentation_date,
                        deed_number,
                        industries,
                        current_status,
                        people_detail,
                        procedures_and_services,
                        payment_documents_submitted,
                        processing_history_table,
                        documents_table
                    ]
                    OBJ = get_listed_object(DATA)
                    OBJ = panama_crawler.prepare_data_object(OBJ)
                    ENTITY_ID = panama_crawler.generate_entity_id(
                        OBJ['registration_number'], company_name=OBJ.get('name', ""))
                    NAME = OBJ['name']
                    BIRTH_INCORPORATION_DATE = ""
                    ROW = panama_crawler.prepare_row_for_db(
                        ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                    panama_crawler.insert_record(ROW)
                except Exception as e:
                    try:
                        button = browser.find_element(
                            By.CLASS_NAME, "blazored-modal-close")
                        button.click()
                        print('model closed')
                    except Exception as e:
                        tb = traceback.format_exc()
                        print(e, tb)
                        print('Something went wrong in table row.')

            try:
                next_button = browser.find_element(
                    By.XPATH, '/html/body/app/div[2]/div[2]/div/div/div/div[4]/div[1]/nav[1]/ul/li[4]/a')
                next_button.click()
                time.sleep(30)
            except:
                print('Next button not found.')
                break

            log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "", "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            panama_crawler.db_log(log_data)
            display.stop()
        except:
            # Handle exceptions
            tb = traceback.format_exc()
            print(e, tb)
            log_data = {"status": "fail",
                        "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"), "crawler": "HTML"}
            # Log error data
            panama_crawler.db_log(log_data)
            display.stop()


# Data used for user credentials
username = 'kifoya1508@soremap.com'
password = 'Test.user123'

driver.switch_to.default_content()
wait = WebDriverWait(driver, 20)
username_input = wait.until(
    EC.presence_of_element_located((By.ID, 'itNombreUsuario')))
password_input = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, 'body > app > div > div.content.px-4 > div > div:nth-child(2) > div.col-sm > form > div:nth-child(2) > div > div > input')))
username_input.send_keys(username)
password_input.send_keys(password)
time.sleep(2)

# Click the login button
login_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//button[@class="btn btn-primary btn-block"]')))
login_button.click()
print("Successfully logged in!")
time.sleep(10)
search_text = sys.argv[2] if len(sys.argv) > 2 else 0
if search_text == "_":
    input_box = driver.find_element(By.ID, "reservaNombreSociedad")
    input_box.send_keys("_")
    submit_button = driver.find_element(
        By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
    submit_button.click()
    get_data(driver,  "_")
elif search_text == "__":
    input_box = driver.find_element(By.ID, "reservaNombrePH")
    input_box.send_keys("_")
    submit_button = driver.find_element(
        By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
    submit_button.click()
    get_data(driver, "__")

for year_index in range(int(search_text), 2024):
    if 0 <= year_index <= 299 or 1990 <= year_index <= 2023:
        for document_number in range(0, 10):
            if len(driver.find_elements(By.ID, "anio")) == 0:
                search_filter = driver.find_element(By.TAG_NAME, 'h5')
                search_filter.click()
                time.sleep(3)
            anio_field = driver.find_element(By.ID, "anio")
            anio_field.clear()
            anio_field.send_keys(year_index)
            numero_field = driver.find_element(By.ID, "numeroDocumentoREDI")
            numero_field.clear()
            numero_field.send_keys(document_number)
            submit_button = driver.find_element(
                By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
            submit_button.click()
            time.sleep(5)
            if len(driver.find_elements(By.CLASS_NAME, "dxbs-gridview")) > 0:
                get_data(
                    driver, f"year_index:{year_index}, document_number: {document_number}")