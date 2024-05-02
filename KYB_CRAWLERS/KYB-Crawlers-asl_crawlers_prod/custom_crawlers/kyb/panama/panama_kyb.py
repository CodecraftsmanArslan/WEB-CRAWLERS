"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from dateutil import parser
from pyvirtualdisplay import Display
from proxy import get_proxy_file

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def skip_pages(browser):
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if start_number != 0:
        for i in range(start_number):
            try:
                time.sleep(10)
                print("Skipping page number: ", i+1)
                next_button = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div/div/div/div[4]/div[1]/nav[1]/ul/li[4]/a')
                next_button.click()
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    return start_number

def get_data(browser, source_type, entity_type, country, category, url, name, description, search_term):
    wait = WebDriverWait(browser, 30)
    page_count = skip_pages(browser)
    while True:
        try:
            page_count += 1
            row_count = 0
            print('page : ', page_count, "search term ", search_term)
            tables = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            rows = tables[1].find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                DATA = []
                row_count += 1
                try:
                    print('row: ', row_count)
                    tds = row.find_elements(By.TAG_NAME, 'td')
                    btn_element = tds[4].find_element(By.TAG_NAME, 'button')
                    btn_element.click()
                    details = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'dl-horizontal')))
                    dt_elements = details[0].find_elements(By.TAG_NAME, 'dt')
                    dd_elements = details[0].find_elements(By.TAG_NAME, 'dd')
                    key_value_pairs = {}
                    for dt, dd in zip(dt_elements, dd_elements):
                        key = dt.text.strip().replace("'","''")
                        value = dd.text.strip().replace("'","''")
                        key_value_pairs[key] = value

                    procedures_and_services = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[1]').text.replace("'","''") if len(browser.find_elements(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[1]')) > 0 else ""
                    payment_documents_submitted = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[2]').text.replace("'","''") if len(browser.find_elements(By.XPATH, '/html/body/app/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/ul[2]')) > 0 else ""

                    # Find the <div> element with the class "btn-group"
                    btn_group = browser.find_element(By.CLASS_NAME, "btn-group")
                    # Find all the <button> elements within the <div> element
                    buttons = btn_group.find_elements(By.TAG_NAME, "button")

                    if len(buttons) > 1:

                        buttons[2].click()
                        try:
                            processing_history_table = []
                            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
                            rows = table.find_elements(By.XPATH, ".//tbody/tr")
                            for row in rows:
                                cells = row.find_elements(By.XPATH, ".//td")
                                if cells[0].text.strip().replace("'","''") != "" and cells[1].text.strip().replace("'","''") != "":
                                    row_data = {
                                        "action": cells[0].text.strip().replace("'","''"),
                                        "date_and_time": timestamp_to_str(cells[1].text.strip().replace("'","''"))
                                    }
                                    processing_history_table.append(row_data)
                        except:
                            pass

                        buttons[3].click()                        
                        try:
                            documents_table = []
                            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
                            rows = table.find_elements(By.XPATH, ".//tbody/tr")
                            for row in rows:
                                cells = row.find_elements(By.XPATH, ".//td")
                                href = ""
                                try:
                                    second_td = row.find_element(By.XPATH, "./td[2]")
                                    button = second_td.find_element(By.XPATH, ".//button[contains(@class, 'btn-link')]")
                                    button.click()
                                    time.sleep(3)
                                    # Find the anchor tag by its text using XPath
                                    anchor = browser.find_element(By.XPATH, "//a[contains(text(), 'Descargar Documento')]")
                                    # Retrieve the href attribute
                                    href = anchor.get_attribute("href")
                                    # Find the h3 tag with "Visor Documento" text
                                    h3_element = browser.find_element(By.XPATH, "//h3[contains(text(), 'Visor Documento')]")

                                    # Find the next sibling button
                                    button = h3_element.find_element(By.XPATH, "./following-sibling::button")

                                    # Click the button
                                    button.click()

                                except Exception as e:
                                    pass
                                if len(cells) > 0 and cells[0].text.strip().replace("'","''") != "":
                                    row_data = {
                                        "document": cells[0].text.strip().replace("'","''"),
                                        "file_url": href
                                    }
                                    documents_table.append(row_data)

                        except:
                            pass

                    browser.find_element(By.CLASS_NAME, 'blazored-modal-close').click()
                    time.sleep(3)

                    registration_number = key_value_pairs.get("NÚMERO DE ENTRADA:")
                    incorporation_date = key_value_pairs.get("FECHA INGRESO:")
                    agent = key_value_pairs.get("PRESENTANTE:")

                    notary = {}
                    if key_value_pairs.get("NOTARIO:") or key_value_pairs.get("NOTARÍA:"):
                        notary = {
                            "type": "notary",
                            "name": key_value_pairs.get("NOTARIO:"),
                            "office_name": key_value_pairs.get("NOTARÍA:")
                        }

                    documentation_date = key_value_pairs.get("FECHA DE ESCRITURA:")
                    deed_number = key_value_pairs.get("NÚMERO DE ESCRITURA:")
                    industries = key_value_pairs.get("DESTINO:")
                    current_status = key_value_pairs.get("SITUACIÓN ACTUAL:")
                    people_detail = key_value_pairs.get("SOCIEDAD/DUEÑO/TITULAR:")

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
                
                    create(DATA, source_type, entity_type, country, category, url, name, description)
                except Exception as e:
                    try: 
                        button = browser.find_element(By.CLASS_NAME, "blazored-modal-close") 
                        button.click()
                        print('model closed')
                    except: pass
                    print('Something went wrong in table row.')

            try:
                next_button = browser.find_element(By.XPATH, '/html/body/app/div[2]/div[2]/div/div/div/div[4]/div[1]/nav[1]/ul/li[4]/a')
                next_button.click()
                time.sleep(30)
            except:
                print('Next button not found.')
                break
                
        except:
            pass

def timestamp_to_str(timestamp):
    try:
        datetime_obj = parser.parse(timestamp)
        return datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        return ""

def create(record_, source_type, entity_type, country, category, url, name, description):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
        print("Stored record\n")
        crawlers_functions.db_connection(query)
    else:
        print("Something went wrong")


def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''

    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f"{record[0]}{url_}-panama_kyb")) # entity_id
    data_for_db.append('') #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')
    return data_for_db

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @param countries
    @param category_
    @param entity_type
    @return dict
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
            "data":[{
                "name": record[9].replace("\n", "")
            }]
        })

    if record[10] != "":
        additional_detail.append({
            "type": "payment_documents_detail",
            "data":[{
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

def wait_for_captcha_to_be_solved(browser):
        while True:
            try:
                iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                print(iframe_element)
                browser.switch_to.frame(iframe_element)
                wait = WebDriverWait(browser, 10000)
                print('trying to resolve captcha')
                checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
                print("Captcha has been Solved")
                break
            except:
                print('captcha solution timeout error, retrying...')

def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        NOPECHA_KEY = 'sub_1NDMQECRwBwvt6pthcY5VBHp'

        # Set up the Selenium WebDriver (assuming you have the appropriate driver executable in your system PATH)
        options = Options()
        



        # chrome_options = webdriver.ChromeOptions()
        # PROXY = "tkhxadjd:j2v7232i1iyg@2.56.119.93:5074"
        # options.add_argument('--proxy-server=' + PROXY)

        options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # options.add_extension(get_proxy_file())
        # options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--no-sandbox')
        options.add_argument('--no-zygote')
        options.add_argument('--log-level=3')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-breakpad')
        
        desired_capabilities = options.to_capabilities()
        desired_capabilities['acceptInsecureCerts'] = True

        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        username = 'kifoya1508@soremap.com'
        password = 'Test.user123'


        print("Downloading NopeCHA crx extension file.")
        # Download the latest NopeCHA crx extension file.
        # You can also supply a path to a directory with unpacked extension files.
        with open('ext.crx', 'wb') as f:
            f.write(requests.get('https://nopecha.com/f/ext.crx').content)
        options.add_extension('ext.crx')
        print('Open webdriver')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=desired_capabilities)
        # Start the driver.
        time.sleep(10)
        # Set the subscription key for the extension by visiting this URL.
        # You can programmatically import all extension settings using this method.
        # To learn more, go to "Export Settings" in the extension popup.
        print("Setting subscription key")
        driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY}")
        # Go to any page with a CAPTCHA and the extension will automatically solve it.
        driver.get(url)
        time.sleep(10)
        print("Wait for the CAPTCHA")
        driver.save_screenshot('screenshot.png')
        wait_for_captcha_to_be_solved(driver)


        # Switch back to the default content
        driver.switch_to.default_content()
        wait = WebDriverWait(driver, 20)
        username_input = wait.until(EC.presence_of_element_located((By.ID, 'itNombreUsuario')))
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > app > div > div.content.px-4 > div > div:nth-child(2) > div.col-sm > form > div:nth-child(2) > div > div > input')))
        username_input.send_keys(username)
        password_input.send_keys(password)
        time.sleep(2)

        # Click the login button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-primary btn-block"]')))
        login_button.click()
        print("Successfully logged in!")
        time.sleep(10)
        search_text = sys.argv[2] if len(sys.argv) > 2 else 0
        if search_text == "_":
            input_box = driver.find_element(By.ID, "reservaNombreSociedad")
            input_box.send_keys("_")
            submit_button = driver.find_element(By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
            submit_button.click()
            get_data(driver, source_type, entity_type, country, category, url, name, description, "_")
        elif search_text == "__":
            input_box = driver.find_element(By.ID, "reservaNombrePH")
            input_box.send_keys("_")
            submit_button = driver.find_element(By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
            submit_button.click()
            get_data(driver, source_type, entity_type, country, category, url, name, description, "__")

        for year_index in range(int(search_text), 2024):
            if 0 <= year_index <= 299 or 1990 <= year_index <= 2023:
                for document_number in range(0,10):
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
                    submit_button = driver.find_element(By.XPATH, "/html/body/app/div[2]/div[2]/form/div[2]/button")
                    submit_button.click()
                    time.sleep(5)
                    if len(driver.find_elements(By.CLASS_NAME, "dxbs-gridview")) > 0:
                        get_data(driver, source_type, entity_type, country, category, url, name, description, f"year_index:{year_index}, document_number: {document_number}")

        driver.quit()

        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")
    

if __name__ == '__main__':
    '''
    Description: Crawler Registro Público de Panamá
    '''
    name = "Registro Público de Panamá"
    description = "This is the website of the Public Registry of Panama (Registro Público de Panamá in Spanish). The public registry is a government institution that manages and regulates public records related to different legal matters in Panama, such as property ownership, mortgages, and business registration. The website provides various services, including access to public registers, information about procedures, forms, and regulations. It also offers online services for businesses, such as online registration and payment systems, as well as tools for searching and obtaining information from the public records."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Panama'
    category = 'Official Registry'
    url = "https://www.rp.gob.pa/"
    display = Display(visible=0,size=(800,600))
    display.start()
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
    display.stop()
