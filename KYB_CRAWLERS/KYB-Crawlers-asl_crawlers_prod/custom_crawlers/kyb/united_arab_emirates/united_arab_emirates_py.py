"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import base64, os
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import nopecha as nopecha
from pyvirtualdisplay import Display
from selenium.common.exceptions import NoSuchElementException
from deep_translator import GoogleTranslator
nopecha.api_key = os.getenv('NOPECHA_API_KEY2')

meta_data = {
    'SOURCE' :'Ministry of Economy - National Economic Register',
    'COUNTRY' : 'United Arab Emirates',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ner.economy.ae/Search_By_BN.aspx", 
                        "Source Description": 'The "National Economic Register" is a federal electronic form developed as part of the government initiatives and is supervised by the Ministry of Economy. The platform aims to adopt the tools of knowledge-based economy by providing accurate, comprehensive, and instant data on the existing economic licenses in the United Arab Emirates. Additionally, the Register serves many groups of stakeholders from various categories such as government entities, businessmen, investors and consumers inside and outside the country.'},
    'URL' : 'https://ner.economy.ae/Search_By_BN.aspx',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'United Arab Emirates'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://ner.economy.ae/Search_By_BN.aspx'

display = Display(visible=0,size=(800,600))
display.start()
uae_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  uae_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=False)
driver.set_page_load_timeout(120)

def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'", "''").replace('"', '')
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        return translated_record

def get_key_value_pair(soup):
    label_elements = soup.find_all('td', class_='tbllabel')
    key_value_pairs = {}
    for label_element in label_elements:
        key = label_element.text.strip()
        next_td = label_element.find_next('td')
        input_element = next_td.find('input')
        if input_element is None:
            textarea_element = next_td.find('textarea')
            if textarea_element:
                value = textarea_element.text.strip()
                key_value_pairs[key] = value
        else:
            value = input_element.get('value')
            key_value_pairs[key] = value
    return key_value_pairs

def get_data(browser):
    record = []
    try:
        wait = WebDriverWait(browser, 60)
        table = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[2]/table/tbody/tr/td/table[1]')))
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        trs = tbody.find_elements(By.TAG_NAME, 'tr')
        for i in range(len(trs)):
            item = {}
            contacts_detail = []
            addresses_detail = []
            table = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[2]/table/tbody/tr/td/table[1]')))
            if len(table.find_elements(By.TAG_NAME, 'tbody')) == 0:
                continue

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    tbody = table.find_element(By.TAG_NAME, 'tbody')
                    trs = tbody.find_elements(By.TAG_NAME, 'tr')
                    detail_btn = trs[i].find_elements(By.TAG_NAME, 'a')
                    break
                except NoSuchElementException as e:
                    print(f"Attempt {attempt + 1}/{max_retries}: Element not found. Retrying...")                    
                    time.sleep(2)

            if len(detail_btn) > 0:
                time.sleep(5)
                try:
                    browser.execute_script("arguments[0].click();", detail_btn[0])
                except:
                    continue
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'DetailsDiv')))
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                detail_page = soup.find('div', class_='DetailsDiv')
                data = get_key_value_pair(detail_page)
                item['registration_number'] = data.get('CBLS No')
                item['license_number'] = data.get('BL Local No')
                item['name'] = data.get('Business Name English')
                item['alias'] = data.get('Business Name Arabic')
                item['type'] = data.get('Legal Type')
                item['is_branch'] = data.get('Is Branch')
                item['parent_establishment_number'] = data.get('Parent BL No')
                item['registration_date'] = data.get('Est. Date').replace('/', '-') if data.get('Est. Date') is not None else ""
                item['expiry_date'] = data.get('Expiry Date').replace('/', '-') if data.get('Expiry Date') is not None else ""
                item['industries_in_arabic'] = data.get('BA Desc. Arabic')
                item['industries'] = data.get('BA Desc. English')
                item['emirate_of_registration'] = data.get('Economic Department')
                item['registration_branch'] = data.get('Registration ED Branch')
                contacts_detail.append({
                    'type': 'mobile_number',
                    'value': data.get('Mobile No')
                })
                contacts_detail.append({
                    'type': 'phone_number',
                    'value': data.get('Phone No')
                })
                item['status'] = data.get('Status')
                type = 'mailing_address' if data.get('PO. Box') is not None and data.get('PO. Box').strip() != '' else 'general_address'
                address = f"{data.get('Full Address')}{data.get('PO. Box')}"
                if address is not None and address.replace('None', '').strip() != "":
                    addresses_detail.append({
                        'type': type,
                        'address': googleTranslator(address.strip().replace('None', '').replace(', ,', ''))
                    })
                contacts_detail.append({
                    'type': 'email',
                    'value': data.get('eMail')
                })
                contacts_detail.append({
                    'type': 'website',
                    'value': data.get('Web Site URL')
                })
                item['contacts_detail'] = contacts_detail
                item['addresses_detail'] = addresses_detail
                record.append(item)
                close_btn = browser.find_elements(By.CLASS_NAME, 'dxWeb_pcCloseButton')
                if len(close_btn) > 0:
                    browser.execute_script("arguments[0].click();", close_btn[0])
    except Exception as e:
        print("Something went wrong")

    return record

try:
    wait = WebDriverWait(driver, 60)
    flag = True
    start_char = sys.argv[1] if len(sys.argv) > 2 else "a"
    characters = list(range(ord('a'), ord('z') + 1)) + list(range(ord('0'), ord('9') + 1))
    for char in characters:
        if chr(char) != start_char and flag:
            continue
        else:
            flag = False
        while True:
            driver.get(BASE_URL)
            language_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@id='ctl00_SwitchLanguageButton' and text()='English']")))
            language_btn.click()
            time.sleep(2)
            if len(driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[1]/div/table/tbody/tr[2]/td[2]/input')) == 0:
                continue
            search_box = driver.find_element(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[1]/div/table/tbody/tr[2]/td[2]/input')
            search_box.clear()
            search_box.send_keys(chr(char))
            captcha_div = driver.find_element(By.CLASS_NAME, 'dxcaControl')
            image_element = captcha_div.find_element(By.TAG_NAME, 'img')
            image_element.screenshot('captcha/captcha.png')
            with open('captcha/captcha.png', 'rb') as image_file:
                image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')
            captcha_text = nopecha.Recognition.solve(
                type='textcaptcha',
                image_urls=[image_64_encode],
            )
            captcha_text_cleaned = str(captcha_text).replace("[","").replace("]","").replace("'","")
            captcha_box = driver.find_element(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[1]/div/table/tbody/tr[6]/td[1]/table[1]/tbody/tr[1]/td[4]/div/table/tbody/tr[1]/td[2]/table/tbody/tr[1]/td/table/tbody/tr/td/input')
            captcha_box.clear()
            captcha_box.send_keys(captcha_text_cleaned)
            submit_btn = driver.find_element(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[1]/div/table/tbody/tr[6]/td[1]/table[2]/tbody/tr[2]/td[1]/table/tbody/tr/td[1]/input')
            time.sleep(1)
            submit_btn.click()
            time.sleep(3)
            table = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[1]/div[2]/table/tbody/tr/td/table[1]')
            if len(table) > 0:
                break
        while True:
            try:
                record = get_data(driver)
                for data in record:
                    if data.get('name') is not None and data.get('registration_number') is not None:
                        print("Record No:", chr(char))
                        DATA =  uae_crawler.prepare_data_object(data)
                        ENTITY_ID = uae_crawler.generate_entity_id(DATA['registration_number'], company_name=DATA['name'])
                        NAME = DATA['name']
                        BIRTH_INCORPORATION_DATE = ""
                        ROW = uae_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,DATA)
                        uae_crawler.insert_record(ROW)
                pagination_btn = driver.find_elements(By.CLASS_NAME, 'dxpButton')
                pagination_btn[1].click()
                time.sleep(5)
            except:
                break

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    uae_crawler.db_log(log_data)
    uae_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    uae_crawler.db_log(log_data)
display.stop()
