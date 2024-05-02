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

meta_data = {
    'SOURCE' :'Ministry of National Economy (وزارة الاقتصاد الوطني) - Companies Controller',
    'COUNTRY' : 'State of Palestine',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "http://www.mne.gov.ps:9095/ords/f?p=200:298", 
                        "Source Description": "The Ministry of National Economy is the ministry responsible for the economy sector in the State of Palestine, and contribute to improving the situation of the Palestinian people through the formation of a development framework for the private sector, which supports and contributes to the economic boom, working to raise the standard of living and welfare of citizens, With relevant ministries, through a formal framework of cooperation. The Ministry is also involved with the relevant ministries to form consultative bodies in partnership with the private sector to formulate economic policies."},
    'URL' : 'http://www.mne.gov.ps:9095/ords/f?p=200:298',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'State of Palestine'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'http://www.mne.gov.ps:9095/ords/f?p=200:298'

palestine_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  palestine_crawler.get_selenium_helper()
request_helper = palestine_crawler.get_requests_helper()
proxy_response = request_helper.make_request('https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/sourceip/direct/turkey/')

options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=http://{proxy_response.text}')
options.add_argument('--headless=true')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = uc.Chrome(version_main=114, options=options)

def identify_spinner(browser):
    while True:
        try:
            if len(browser.find_elements(By.CLASS_NAME, 'u-Processing')) == 0:
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                table = soup.find('table', class_='t-Report-report')
                if table is not None:
                    break
        except Exception as e:
            print("Error")

def get_data(soup):
    data = []
    table = soup.find('table', class_='t-Report-report')
    header_row = table.find('thead').find('tr')
    headers = [th.text.strip() for th in header_row.find_all('th')]
    data_rows = table.find('tbody').find_all('tr')
    for row in data_rows:
        cells = [cell.text.strip() for cell in row.find_all('td')]
        row_data = dict(zip(headers, cells))
        data.append(row_data)
    return data

try:
    flag = True
    start_char = sys.argv[1] if len(sys.argv) > 1 else "a"
    urdu_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'ا', 'ب', 'پ', 'ت', 'ٹ', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ڈ', 'ذ', 'ر', 'ڑ', 'ز', 'ژ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن', 'ں', 'و', 'ہ', 'ھ', 'ء', 'ی', 'ے']
    for letter in urdu_alphabet:
        if letter != start_char and flag:
            continue
        else:
            flag = False
        wait = WebDriverWait(driver, 60)
        driver.get(BASE_URL)
        search_button_locator = (By.ID, 'B243567842050195006')
        search_button = wait.until(EC.element_to_be_clickable(search_button_locator))
        search_button.click()
        input_box_locator = (By.ID, 'P28_SEARCH')
        input_box = wait.until(EC.presence_of_element_located(input_box_locator))
        input_box.send_keys(letter)
        while True:
            identify_spinner(driver)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            records = get_data(soup)
            for record in records:
                print('letter:', letter)
                address =  f"{record['الدولة']} {record['المحافظة']} {record['المدينة']}"
                data = {
                    'type': record['طبيعة التاجر'],
                    'registration_number': record['الرقم'],
                    'entity_name': record['اسم التاجر او الشركة'],
                    'name': record['الاسم التجاري'],
                    'status': record['الحالة'],
                    'registration_date': record['تاريخ التسجيل'].replace('/', '-'),
                    'addresses_detail' : [{
                        'type': 'general_address',
                        'address': address,
                    }],
                    'jurisdiction': record['المحافظة'],
                    'industries': record['الغايات'],
                }
                ENTITY_ID = palestine_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
                BIRTH_INCORPORATION_DATE = ''
                DATA = palestine_crawler.prepare_data_object(data)
                ROW = palestine_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
                palestine_crawler.insert_record(ROW)
            try:
                next_page_btn = driver.find_element(By.CLASS_NAME, 't-Report-paginationLink--next')
                next_page_btn.click()
            except:
                driver.quit()
                break


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    palestine_crawler.db_log(log_data)
    palestine_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    palestine_crawler.db_log(log_data)