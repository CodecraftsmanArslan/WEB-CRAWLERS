"""Import required library"""
import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from CustomCrawler import CustomCrawler
from helpers.load_env import ENV
from datetime import datetime


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Bermuda Registrar of Companies',
    'COUNTRY': 'Bermuda',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.registrarofcompanies.gov.bm/",
                      "Source Description": "The Bermuda Registrar of Companies Online Register is available to registered users to register and maintain entities and perform searches of the public registry. "},
    'SOURCE_TYPE': 'HTML',
    'URL': ' https://www.registrarofcompanies.gov.bm/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bermuda Official Registry",
}

Bermuda_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = Bermuda_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
driver.get("https://www.registrarofcompanies.gov.bm")
time.sleep(5)

def skip_pages():
    """
    Skips a specified number of pages in a web application.

    This function takes the starting page number as a command-line argument (if provided)
    and skips the specified number of pages by clicking on the "Next" button in the application.
    It uses the Selenium WebDriver to interact with the web pages and handles WebDriverExceptions
    that may occur during the process.

    Parameters:
    - None

    Returns:
    - int: The page count after skipping the specified number of pages.
    """
    start_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    if start_number != 1:
        for i in range(start_number-1):
            try:
                time.sleep(5)
                print("Skipping page number: ", i+1)
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="appNext pagination-item"]')))
                next_button.click()
            except:
                print("WebDriverException occurred while skipping page")
    page_count = start_number
    time.sleep(5)
    return page_count

alphabets_digits = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0','1','2','3','4','5','6','7','8','9']

arguments = sys.argv
start_alphabet= arguments[1] if len(arguments)>1 else alphabets_digits[0]
try:
    wait = WebDriverWait(driver, 10)
    search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[role="button"]')))
    search.click()
    time .sleep(5)
    button=wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[class="guest-primary-row1-menu1 appMenu appMenuItem appMenuDepth0 appButtonPrimary appButton noUrlStackPush appNotReadOnly appIndex2"]')))
    button.click()
    time.sleep(5)
    select_element=wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="appGroupSelector appRestricted appRestrictedSelect"]')))
    select_element.click()
    dropdown = wait.until(EC.visibility_of_element_located((By.XPATH, '//option[@value="Contains"]')))
    dropdown.click()
    time.sleep(10)
    
    for letter in alphabets_digits[alphabets_digits.index(start_alphabet):]:
        id_search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
        id_search.send_keys(letter)  
        print('Current alphabets_digit',letter)  
     
        id_button=wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[class="appButton searchEntities-tabs-criteriaAndButtons-buttonPad-search appButtonPrimary appSearchButton appSubmitButton appPrimaryButton appNotReadOnly appIndex2"]')))
        id_button.click()
        time.sleep(3)
        
        page= skip_pages()

        while True:  
            links = len(driver.find_elements(By.XPATH, '//div[@class="appMinimalMenu viewMenu noSave viewInstanceUpdateStackPush"]'))  
            for page_number in range(links):
                time.sleep(5)
                elements = driver.find_elements(By.XPATH, '//div[@class="appMinimalMenu viewMenu noSave viewInstanceUpdateStackPush"]')
                names = elements[page_number].find_element(By.XPATH, './/a[@class="searchEntities-results-page-searchRow-resultLeft-viewMenu appMenu appMenuItem appMenuDepth0 noSave viewInstanceUpdateStackPush appReadOnly appIndex0"]')
                names.click()

                reg_num = driver.find_element(By.XPATH, '//span[@class="appPageTitleText"]').text
                number = re.sub(r'[^0-9]', '', reg_num)
                try:
                    entity = driver.find_element(By.XPATH, '//span[text()="Type of entity"]/parent::span/parent::div/following-sibling::div').text
                except:
                    entity = driver.find_element(By.XPATH, '//span[text()="Entity type"]/parent::span/parent::div/following-sibling::div').text  
                name = driver.find_element(By.XPATH, '//span[text()="Entity name"]/parent::span/parent::div/following-sibling::div').text.replace("%","%%")
                reg_date = driver.find_element(By.XPATH, '//span[text()="Registration date in Bermuda"]/parent::span/parent::div/following-sibling::div')
                reg_date_str = reg_date.text.replace('\n', ' ').strip()            
                date_components = reg_date_str.split()
                reg_date = date_components[0]
                
                OBJ = {
                    "registration_number": number,
                    "name": name,
                    "type": entity,
                    "registration_date": reg_date
                }
                OBJ =  Bermuda_crawler.prepare_data_object(OBJ)
                ENTITY_ID = Bermuda_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = ""
                ROW = Bermuda_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                Bermuda_crawler.insert_record(ROW)   
                print('Current alphabets_digit',letter)     
                driver.back()

            try:
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="appNext pagination-item"]')))
                next_button.click()
                page+= 1
                print(f"Clicking Page {page}")
            except:
                break

        Bermuda_crawler.end_crawler()
        log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML","ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        Bermuda_crawler.db_log(log_data)


except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Bermuda_crawler.db_log(log_data)
  

  


















