"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc 
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'Conservador De Bienes Raíces De Santiago, Commercial Registry Index',
    'COUNTRY' : 'Santiago',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.conservador.cl/portal/indice_comercio", 
                        "Source Description": "In the commercial registry index, the transactions of commercial companies and their powers are registered for the efficacy of business procedures."},
    'URL' : 'https://www.conservador.cl/portal/indice_comercio',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Santiago'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://www.conservador.cl/portal/indice_comercio'

display = Display(visible=0,size=(800,600))
display.start()
santiago_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  santiago_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=True)

def wait_for_captcha_to_be_solved(browser):
        while True:
            try:
                iframe_element = browser.find_element(By.XPATH, '//*[@id="recaptchaTexto"]/div/div/iframe')
                browser.switch_to.frame(iframe_element)
                print('trying to resolve captcha')
                time.sleep(3)
                if len(browser.find_elements(By.CLASS_NAME,"recaptcha-checkbox-checked")) > 0:
                    browser.switch_to.default_content()
                    print("Captcha has been Solved")
                    return browser 
                browser.switch_to.default_content()
            except Exception as e:
                print('captcha solution timeout error, retrying...', e)


try:
    wait = WebDriverWait(driver, 30)
    driver.get(BASE_URL)
    text_btn = driver.find_element(By.XPATH, '//*[@id="myTab"]/li[2]/a')
    text_btn.click()
    input_box = driver.find_element(By.ID, 'razon')
    wait_for_captcha_to_be_solved(driver)
    time.sleep(5)
    input_box.send_keys('*')
    submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'buscar')))
    submit_btn.click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tabla-razon')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='tabla-razon')
    if table is not None:
        tbody = table.find('tbody')
        if tbody is not None:
            trs = tbody.find_all('tr')
            for tr in trs:
                item = {}
                additional_detail = []
                tds = tr.find_all('td')
                item['registration_number'] = tds[1].text
                item['formation_year'] = tds[2].text    
                item['registry_status'] = tr.find('p', class_='texto-index-tipo').text.strip() if tr.find('p', class_='texto-index-tipo') else ''
                NAME = tr.find('p', class_='texto-index-nombre').text.strip() if tr.find('p', class_='texto-index-nombre') else ''
                item['name'] = NAME
                entity_name = tr.find('p', class_='texto-index-personas').text.strip() if tr.find('p', class_='texto-index-personas') else ''
                item['additional_detail'] = [{
                    'type': 'related_entity',
                    'data': [{
                        'name': entity_name
                    }]
                }] if entity_name != '' else []
                ENTITY_ID = santiago_crawler.generate_entity_id(company_name=NAME, reg_number=item.get('registration_number'))
                BIRTH_INCORPORATION_DATE = ''
                DATA = santiago_crawler.prepare_data_object(item)
                ROW = santiago_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                santiago_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    santiago_crawler.db_log(log_data)
    santiago_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    santiago_crawler.db_log(log_data)
display.stop()
