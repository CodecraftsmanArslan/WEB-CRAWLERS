"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

meta_data = {
    'SOURCE' :'Ministry Of Commerce and Industry',
    'COUNTRY' : 'Somalia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ebusiness.gov.so/search/name-search?_token=uc7hBGT0Sj4uGPCn6EBtjXmHG1tkJbYHc7HEp8DB&q=__a", 
                        "Source Description": "Somali Company Registry by Ministry of Commerce and Industry, it allow users to reserve the name of company, register the company and also apply for license. It also provide service to verify the authenticity of Incorporation Certificates and Licenses."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://ebusiness.gov.so/search/name-search?_token=uc7hBGT0Sj4uGPCn6EBtjXmHG1tkJbYHc7HEp8DB&q=__a'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Somalia Official Registry"
}
    
somalia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  somalia_crawler.get_requests_helper()
selenium_helper = somalia_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=True,Nopecha=False)

alphabet_range = [f'__{i}' for i in range(10)] + [f'__{chr(ord("a") + i)}' for i in range(26)]
Alphabets = alphabet_range

arguments = sys.argv

if len(arguments) > 1 and arguments[1] in Alphabets:
    start_index = Alphabets.index(arguments[1])
else:
    start_index = 0
try:
    for i in range(start_index, len(Alphabets)):
        ALPHABET = Alphabets[i]
        print('ALPHABET', ALPHABET)
        url = f'https://ebusiness.gov.so/search/name-search?q={ALPHABET}'
        print(url)
        driver.get(url)
        time.sleep(10)
        DATA_SIZE = len(driver.page_source)
        dropdown_element = driver.find_element(By.CLASS_NAME, 'custom-select')
        select = Select(dropdown_element)
        select.select_by_value('100')
        while True:
            table = driver.find_element(By.XPATH,'/html/body/main/section/div/div/div/div/div/div/table')

            rows = table.find_elements(By.TAG_NAME,"tr")
            data = {}
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME,"td")
                Name = cells[0].text.strip()
                Registration_Number = cells[1].text.strip().replace("N/A","")
                type_ = cells[2].text.strip()
                Registration_Date = cells[3].text.strip().replace("N/A","").replace("/","-")
                Status = cells[4].text.strip()
                data['name'] = Name
                data['registration_number'] = Registration_Number
                data['type'] = type_
                data['registration_date'] = Registration_Date
                data['status'] = Status

                OBJ = {
                    "name":data["name"],
                    "registration_number":data["registration_number"],
                    "type":data["type"],
                    "registration_date":data["registration_date"],
                    "status":data["status"]
                }

                OBJ =  somalia_crawler.prepare_data_object(OBJ)
                ENTITY_ID = somalia_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
                NAME = OBJ['name']
                BIRTH_INCORPORATION_DATE = ""
                ROW = somalia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                somalia_crawler.insert_record(ROW)
            
            next_button = driver.find_element(By.CLASS_NAME,'next')
            next_btn_class = next_button.get_attribute('class')
            
            if next_btn_class.find('disabled') != -1:
                break
        
            try:
                next_button.click()
                time.sleep(2)
            except:
                next_button = driver.find_element(By.CLASS_NAME,'next')
                next_button.click()
                time.sleep(2)

    somalia_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    somalia_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    somalia_crawler.db_log(log_data)