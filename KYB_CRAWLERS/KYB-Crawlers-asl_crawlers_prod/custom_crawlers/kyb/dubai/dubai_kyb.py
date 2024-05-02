"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import undetected_chromedriver as uc 
from deep_translator import GoogleTranslator

meta_data = {
    'SOURCE' :'Dubai Economy and Tourism Department',
    'COUNTRY' : 'Dubai',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://eservices.dubaided.gov.ae", 
                        "Source Description": "The department's goal is to raise Dubai to become a global centre for business, investment and tourism by supporting the evolution of the city through supportive tourism initiatives and future-proof economic programmes."},
    'URL' : 'https://eservices.dubaided.gov.ae',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Dubai Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://eservices.dubaided.gov.ae'

dubai_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  dubai_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)
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
    
def generate_license_numbers(start_number):
    if start_number < 110000:
        start_number = 110000

    # Generate 6-digit numbers from the starting number to 900990
    for number in range(start_number, 900991):
        yield number

    # Generate 7-digit numbers from the starting number to 1250097
    for number in range(max(start_number, 1000000), 1250098):
        yield number

def get_next_span_txt(soup, keyword):
    spans = soup.find_all('span')
    for span in spans:
        if keyword in span.text.strip():
            next_span = span.find_next_sibling('span')
            if next_span is not None:
                return next_span.text.strip()
    return ""

def get_data(soup, arabic_name):
    item = {}
    addresses_detail = []
    contacts_detail = []
    item['name_in_arabic'] = arabic_name
    item['registration_number'] = get_next_span_txt(soup, 'License Nr')
    item['name'] = get_next_span_txt(soup, 'Trade Name')
    item['status'] = get_next_span_txt(soup, 'License Status')
    item['type'] = get_next_span_txt(soup, 'Legal Type')
    item['license_expiry_date'] = get_next_span_txt(soup, 'Expiry Date').replace('/', '-')
    telephone = get_next_span_txt(soup, 'Telephone')
    if telephone != '' and telephone != '-' and telephone != '0':
        contacts_detail.append({
            'type': 'telephone',
            'value': telephone
        })
    fax = get_next_span_txt(soup, 'Fax')
    if fax != '' and fax != '-' and fax != '0':
        contacts_detail.append({
            'type': 'fax',
            'value': fax
        })
    mobile_number = get_next_span_txt(soup, 'Mobile Nr')
    if mobile_number != '' and mobile_number != '-' and mobile_number != '0':
        contacts_detail.append({
            'type': 'mobile_number',
            'value': mobile_number
        })
    email = get_next_span_txt(soup, 'Email')
    if email != '' and email != '-' and email != '0' and email != '00' and email != '.':
        contacts_detail.append({
            'type': 'email',
            'value': email
        })
    general_address = googleTranslator(get_next_span_txt(soup, 'Address'))
    if general_address != '':
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address
        })

    area =  get_next_span_txt(soup, 'Area')
    sub_area =  get_next_span_txt(soup, 'Sub Area')
    community =  get_next_span_txt(soup, 'Community')
    landmark =  get_next_span_txt(soup, 'Landmark')
    street =  get_next_span_txt(soup, 'Street')
    building =  get_next_span_txt(soup, 'Building')
    floor =  get_next_span_txt(soup, 'Floor')
    parcel_id =  get_next_span_txt(soup, 'Parcel ID')

    postal_address = f"{area} {sub_area} {community} {landmark} {street} {building} {floor} {parcel_id}" 
    postal_address = postal_address.replace('\xa0', '').replace('[-]', '').replace('-', '').replace('  ', '')
    if postal_address != '':
        addresses_detail.append({
            'type': 'postal_address',
            'address': postal_address
        })

    item['units'] = get_next_span_txt(soup, 'Unit').replace('\xa0', '').replace('[', '').replace(']', '')

    gps_coordinates = get_next_span_txt(soup, 'GPS Coordinates')
    if gps_coordinates != 'Longitude\xa0-Latitude\xa0-':
        item['gps_coordinates'] = gps_coordinates.replace('\xa0', ' ')

    item['addresses_detail'] = addresses_detail
    item['contacts_detail'] = contacts_detail

    return item

try:
    max_retries = 1250097
    retries = 0
    wait = WebDriverWait(driver, 60)
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 110000 #583502
    while retries < max_retries:
        try:
            driver.get(BASE_URL)
            select_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[p/text()='Search License Information']")))
            select_btn.click()
            for reg_num in generate_license_numbers(start_number):
                print(f"Record No: {reg_num}")
                input_box = wait.until(EC.presence_of_element_located((By.ID, 'DEDLCNr')))
                input_box.clear()
                input_box.send_keys(reg_num)
                submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'DEDBtnSrch')))
                submit_btn.click()
                td_btns = driver.find_elements(By.XPATH, '//*[@id="DGSrcResult"]/tbody/tr[2]/td[1]/a')
                if len(td_btns) > 0:
                    name_in_arabic = driver.find_element(By.XPATH, '//*[@id="DGSrcResult"]/tbody/tr[2]/td[3]').text
                    td_btns[0].click()
                    # Get the handles of the main window and the popup window
                    main_window_handle = driver.current_window_handle
                    popup_window_handle = None

                    # Switch to the popup window
                    for handle in driver.window_handles:
                        if handle != main_window_handle:
                            popup_window_handle = handle
                            break

                    # Switch to the popup window
                    driver.switch_to.window(popup_window_handle)
                    time.sleep(3)
                    # Perform actions within the popup window
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    data = get_data(soup, name_in_arabic)

                    ENTITY_ID = dubai_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
                    BIRTH_INCORPORATION_DATE = ''
                    DATA = dubai_crawler.prepare_data_object(data)
                    ROW = dubai_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
                    dubai_crawler.insert_record(ROW)

                    # Close the popup window
                    driver.close()

                    # Switch back to the main window
                    driver.switch_to.window(main_window_handle)

        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Timeout exception occurred on {reg_num}. Retrying...")
            start_number = reg_num
            retries += 1

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    dubai_crawler.db_log(log_data)
    dubai_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    dubai_crawler.db_log(log_data)