"""Import required library"""
import sys, traceback,time,os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'Ontario Business Information System (ONBIS) portal in Canada',
    'COUNTRY' : 'Ontario',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.appmybizaccount.gov.on.ca/onbis/companykey/?lang=en", 
                        "Source Description": "Online government services are critical, not only to individual citizens but also to businesses and not-for-profit corporations of all sizes. To serve Ontario better, the Ontario Business Registry offers simpler, faster, and more convenient access for organizations that are registered, incorporated, or licensed to carry on business in Ontario."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.appmybizaccount.gov.on.ca/onbis/companykey/?lang=en'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Ontario Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

ontario_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = ontario_crawler.get_requests_helper()
selenium_helper = ontario_crawler.get_selenium_helper()

display = Display(visible=0,size=(800,600))
display.start()
driver = selenium_helper.create_driver(headless=False,Nopecha=False)

arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0

def get_range():
    for i in range(start_num, 999999999):
        yield f"{i:06d}"

driver.get('https://www.appmybizaccount.gov.on.ca/onbis/companykey/?lang=en')
time.sleep(3)
try:
    # lst = [937163, 1127827]
    numbers = get_range()
    for number in numbers:
        print('\nSearch Number',number)
        searchText = driver.find_element(By.ID,'searchText')
        searchText.send_keys(number)
        time.sleep(2)

        search_button = driver.find_element(By.ID,'search-button')
        search_button.click()
        time.sleep(10)
        
        if 'No results found. Please change your search criteria and try again.' in driver.page_source:
            print('No results found.')
            continue
        
        all_data = {}
        try:
            previous_names = driver.find_element(By.XPATH, '//span[text()="Previously known as:"]/following-sibling::ul').text.strip() 
        except:
            previous_names = ""
        all_data['previous_names'] = previous_names
        wait = WebDriverWait(driver, 300)
        search_results = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'search-results__entity-info')))
        search_results.click()
        time.sleep(14)
        if 'A company key is not available for this registration type. The company key was issued to the registrant corporation or partnership to which this business name is registered.' in driver.page_source:
            print("A company key is not available for this registration type")
            reset_button = driver.find_element(By.ID,'reset-button')
            reset_button.click()
            time.sleep(5)
            continue
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for div in soup.find_all('div', class_='get-entity__entity-info'):
            key = div.find('div', class_='get-entity__entity-info__col1').text.strip()
            value = div.find('div', class_='get-entity__entity-info__col2').text.strip()
            all_data[key] = value
            
        # get additional_detail
        additional_detail = []
        if all_data.get('Primary activity code','') !='[Not provided]' and all_data.get('Primary activity code','') != "":
            additional_detail.append({
                "type":"primary_acitvity_info",
                "data":[
                        {
                            "code":all_data.get('Primary activity code',''),
                            "activity":all_data.get('Primary activity','')
                        }
                    ]
            })
        
        # get addresses_detail
        addresses_detail = []
        if all_data.get('Principal place of business','') !='':
            addresses_detail.append({
                "type":"general_address",
                "address":all_data.get('Principal place of business','')  
            })
        
        if all_data.get('Registered or head office address','') !='':
            addresses_detail.append({
                "type":"registered_address",
                "address":all_data.get('Registered or head office address','')  
            })
        try:
            registration_number = all_data['Business Identification Number (BIN)']
        except:
           registration_number = all_data.get('Ontario Corporation Number', '')
        try:
            NAME = all_data['Business name']
        except:
            NAME = all_data.get('Corporation name','')
        
        OBJ = {
                "name":NAME,
                "registration_number":registration_number,
                "registration_date":all_data.get('Registration Date',''),
                "type":all_data.get('Type',''),
                "status":all_data.get('Status',''),
                'incorporation_date':all_data.get('Incorporation date',''),
                'jurisdiction':all_data.get('Governing jurisdiction',''),
                "addresses_detail":addresses_detail,
                "additional_detail":additional_detail,
                'previous_names_detail':[
                    {
                        "name":all_data.get('previous_names','')
                    }
                ]
            }

        OBJ =  ontario_crawler.prepare_data_object(OBJ)
        ENTITY_ID = ontario_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
        ROW = ontario_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        ontario_crawler.insert_record(ROW)
        
        time.sleep(8)
        back_button = wait.until(EC.visibility_of_element_located((By.ID,'back-button')))
        back_button.click()
        time.sleep(5)
        reset_button = driver.find_element(By.ID,'reset-button')
        reset_button.click()
        time.sleep(5)
        driver.refresh()
        time.sleep(5)


    ontario_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    ontario_crawler.db_log(log_data)
    display.stop()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    ontario_crawler.db_log(log_data)
    display.stop()