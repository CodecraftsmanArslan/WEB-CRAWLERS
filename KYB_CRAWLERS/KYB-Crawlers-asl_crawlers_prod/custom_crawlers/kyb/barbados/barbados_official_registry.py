"""Set System Path"""
import sys
from pathlib import Path
import traceback
from CustomCrawler import CustomCrawler
import json
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from bs4 import BeautifulSoup
import requests, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


ENV =  {
           'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')                 
        }

meta_data = {
    'SOURCE' :'Corporate Affairs and Intellectual Property Office (CAIPO)',
    'COUNTRY' : 'Barbados',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://caipo.gov.bb/search-our-database/", 
                        "Source Description": "The Corporate Affairs and Intellectual Property Office (CAIPO) in Barbados is a government agency responsible for the registration and regulation of corporate entities and intellectual property rights in the country."},
    'URL' : 'https://caipo.gov.bb/search-our-database/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Barbados Official Registry"
}

ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

barbados_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  barbados_crawler.get_requests_helper()

selenium_helper =  barbados_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)
# Check if a command-line argument is provided
arguments = sys.argv
page_number = int(arguments[1]) if len(arguments)>1 else 1
# Define the search range


flag = True
max_retries = 3
try:
    # Define the search range
    start_number = page_number
   
    end_number = 78113
    # Iterate over the search range
    number = start_number
    while number < end_number:
        try:
            driver.get('https://caipo.gov.bb/search-our-database/')
            time.sleep(2)
            wait = WebDriverWait(driver, 30)
            print(number)
            select_element = wait.until(
                EC.presence_of_element_located((By.ID, 'srchOpt_1_number'))
            )
            select = Select(select_element)
            select.select_by_index(1)

            search_field = wait.until(EC.presence_of_element_located((By.ID, 'value_number_1')))
            search_field.clear()
            search_field.send_keys(str(number))
            # Get the captcha element
            captcha_element = driver.find_element(By.XPATH, '//*[@id="form_grid_1"]/tbody/tr/td/div[2]/div[1]')
            # Extract the numbers from the captcha element
            captcha_text = captcha_element.text
            start_index = captcha_text.find("What is") + len("What is")
            end_index = captcha_text.find(":")
            numbers_string = captcha_text[start_index:end_index].strip()
            # Split the numbers string into individual numbers
            numbers = numbers_string.split("+")
            # Convert the numbers to integers
            numbers = [int(num.strip()) for num in numbers]
            # Calculate the sum of the numbers
            result = sum(numbers)
            # Enter the result into the captcha input field
            captcha_input = driver.find_element(By.XPATH, '//*[@id="form_grid_1"]/tbody/tr/td/div[2]/div[2]/input')
            captcha_input.clear()
            captcha_input.send_keys(str(result))
            time.sleep(2)
            # Click the search button
            search_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchButton1"]')))
            search_button.click()
            time.sleep(2)

            while True:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
                table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dataTables_scrollBody'))) 
                table_html = table.get_attribute('innerHTML')
                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(table_html, 'html.parser')

                # Find the table rows
                rows = soup.find_all('tr')

                for row in rows[1:]:
                    cells = row.find_all('td')
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    NAME = row_data[0].replace("%", "%%") if row_data[0] is not None else ""
                    registration_number = row_data[1] if row_data[1] else ""
                    categories = row_data[2] if row_data[2] else ""
                    date_ = row_data[3] if row_data[3] else ""
                    DATA = {
                        "name": NAME,
                        "registration_number":registration_number.replace("%","%%"),
                        "category": categories.replace("%","%%"),    
                    "category": categories.replace("%","%%"),    
                        "category": categories.replace("%","%%"),    
                    "category": categories.replace("%","%%"),    
                        "category": categories.replace("%","%%"),    
                        "registration_date": date_.replace("%","%%"),
                    }
                    ENTITY_ID = barbados_crawler.generate_entity_id(reg_number=NAME)
                    BIRTH_INCORPORATION_DATE = ''
                    DATA = barbados_crawler.prepare_data_object(DATA)
                    ROW = barbados_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                    barbados_crawler.insert_record(ROW)

                next_button = driver.find_element(By.XPATH, '//*[@id="table_id_next"]')
                if 'disabled' in next_button.get_attribute('class'):
                    break
                else:
                    # Scroll to the "Next" button before clicking
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
            number += 1
            print("Page_no:",number)
        except:
            if max_retries == 0:
                number += 1
                max_retries = 3
            else:
                max_retries -= 1
            print(f"Error occurred on page {number} - retrying {max_retries}")            
            
    driver.quit()
    log_data = {"status": 'success',
                     "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    barbados_crawler.db_log(log_data)
    barbados_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    barbados_crawler.db_log(log_data)
    barbados_crawler.end_crawler()
