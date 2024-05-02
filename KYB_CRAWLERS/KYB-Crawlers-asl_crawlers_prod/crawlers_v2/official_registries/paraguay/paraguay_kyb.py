"""Import required library"""
import time, sys
import ssl
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
# Give start and end range
first_range = int(arguments[1]) if len(arguments)>1 else 80000001
second_range = int(arguments[2]) if len(arguments)>1 else 80133321
meta_data = {
    'SOURCE' :'Registro Único del Contribuyente (RUC)',
    'COUNTRY' : 'Paraguay',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ruc.com.py/", 
                        "Source Description": "Registro Único del Contribuyente (Unique Taxpayer Registry) in Paraguay, It is a unique identification number assigned to individuals and businesses for tax purposes by the tax authority of Paraguay, known as the Subsecretaría de Estado de Tributación (SET)."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.ruc.com.py/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Paraguay Official Registry"
}

paraguay_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  paraguay_crawler.get_requests_helper()
selenium_helper = paraguay_crawler.get_selenium_helper()

start_number = first_range
end_number = second_range

try:
    for number in range(start_number , end_number):
        driver = selenium_helper.create_driver(headless=True,Nopecha=False)
        wait = WebDriverWait(driver, 10) 
        driver.get('https://www.ruc.com.py/')
        print("Searching for:",str(number))
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'txt_buscar')))
        search_field.clear()
        search_field.send_keys(str(number))
        time.sleep(2)
        search_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div/div[1]/button')
        search_button.click()
        time.sleep(5)
        try:
            login_model = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="login-modal"]//button[@id="btn-cerrar-modal-login"]')))
        except:
            pass
        login_model.click()
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        time.sleep(5)
        tr = tbody.find_element(By.TAG_NAME, 'tr')
        registration_number = tr.find_element(By.TAG_NAME, 'td').text
        NAME = tr.find_elements(By.TAG_NAME, 'td')[1].text
        OBJ={
            "name":NAME,
            "registration_number":registration_number
        }
        print(OBJ , 'OBJ')
        OBJ =  paraguay_crawler.prepare_data_object(OBJ)
        ENTITY_ID = paraguay_crawler.generate_entity_id(company_name= NAME ,  reg_number= registration_number)
        BIRTH_INCORPORATION_DATE =''
        ROW = paraguay_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        paraguay_crawler.insert_record(ROW)
        driver.quit()

    paraguay_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"  }
    paraguay_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    paraguay_crawler.db_log(log_data)           