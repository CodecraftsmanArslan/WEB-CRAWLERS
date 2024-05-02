import sys, os, traceback, time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import traceback
from datetime import datetime
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing
from load_env.load_env import ENV


# Define constants
MAX_RETRIES = 3
SEARCH_LIST = ['r','0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# ALPHABETS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'] 

SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = "N/A"

# Define meta data and crawler configuration
meta_data = {
    "SOURCE_TYPE":"HTML",
    'SOURCE' :'Ministry of Communications',
    'COUNTRY' : 'Fiji Islands',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://roc.digital.gov.fj/BuyInformation/Search", 
                        "Source Description": "The Digital Transformation Programme is an initiative undertaken by the Fiji Government to modernize and enhance digital services across various sectors and government agencies in Fiji"},
    'URL' : 'https://roc.digital.gov.fj/BuyInformation/Search',
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Fiji Island Official Registry"
}
fiji_island_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
# Initialize the Chrome web driver
selenium_helper =  fiji_island_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False, proxy=True)

def load_processed_entity_numbers():
    """
    Description: Load processed entity numbers from a file named 'crawler_numbers.txt'.
    Attempts to read the file and return a set containing the processed entity numbers.
    If the file is not found, an empty set is returned.
    @return:
    - set: A set containing processed entity numbers read from the file, or an empty set if the file is not found.
    """
    try:
        with open('crawler_numbers.txt', 'r') as file:
            processed_numbers = file.read().splitlines()
        return set(processed_numbers)
    except FileNotFoundError:
        return set()

processed_entity_numbers = load_processed_entity_numbers()

# Function to process a single entity number
def process_entity(entity_number):
    """
    Description: Process the provided entity number on a specific web page.
    @param:
    - entity_number (str): The entity number to be processed.
    @return:
    - None
    """
    if entity_number in processed_entity_numbers:
        print(f"Entity number {entity_number} already processed. Skipping...")
        return
    
    entity_number_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID,'SearchNumber')))

    entity_number_input.clear()
    entity_number_input.send_keys(entity_number)

    # Click the search button
    search_button = driver.find_element(By.XPATH, '//*[@id="btn-search-submit"]')
    search_button.click()
    # Wait for the "loader2" element to disappear
    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.ID, 'loader2')))
    while True:
        # Wait for the table to load
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            time.sleep(3)  # Allow some time for the table to fully load

            DATA_SIZE = len(driver.page_source)
            
            table = driver.find_element(By.TAG_NAME, 'table')
            # Find the table rows
            rows = table.find_elements(By.TAG_NAME,'tr')
            if len(rows) == 1:
                # Only header row is present, indicating no data available
                print("No data available for entity number:", entity_number)
                driver.refresh()
                time.sleep(10)
                break
            
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME,'td')
                row_data = [cell.text.strip() for cell in cells]

                NAME = row_data[2]
                registration_number = row_data[3]
                type = row_data[4]
                status = row_data[5]

                DATA = {
                    "name": NAME,
                    "registration_number": registration_number,
                    "type": type,
                    "status": status,
                }
                print(DATA)

                ENTITY_ID = fiji_island_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
                BIRTH_INCORPORATION_DATE = ''
                DATA = fiji_island_crawler.prepare_data_object(DATA)
                ROW = fiji_island_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                fiji_island_crawler.insert_many_records([ROW])
                print("Entity Number", entity_number)
                
            try:
                next_button = driver.find_elements(By.CLASS_NAME, "k-pager-nav")[-2] 
                next_btn_classes = next_button.get_attribute('class')
                if 'k-link k-pager-nav k-state-disabled' in next_btn_classes: 
                    break
                next_button.click()
            except:
                print("issue on next button")
                pass
            
            processed_entity_numbers.add(entity_number)
            # Save the processed entity numbers to the file
            with open('crawler_numbers.txt', 'a') as file:
                file.write(f"{entity_number}\n")
        
        except:
            print("Table rows not found")
            pass
            
try:
    processes = []
    driver.get('https://roc.digital.gov.fj/BuyInformation/Search')
    time.sleep(10)
    with multiprocessing.Pool(processes=4) as pool:
        pool.map(process_entity, SEARCH_LIST)
        
    log_data = {"status": 'success',
        "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":"",  "crawler":"HTML", "ebds_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    fiji_island_crawler.db_log(log_data)
    fiji_island_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": 'fail',
                "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    fiji_island_crawler.db_log(log_data)
