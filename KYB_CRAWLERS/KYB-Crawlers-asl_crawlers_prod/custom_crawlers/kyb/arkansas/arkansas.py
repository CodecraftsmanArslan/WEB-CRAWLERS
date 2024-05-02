import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
import time, os, base64
import nopecha as nopecha
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display

nopecha.api_key = os.getenv('NOPECHA_API_KEY2')

ssl._create_default_https_context = ssl._create_unverified_context

meta_data = {
    'SOURCE' :'Arkansas Secretary of State, Business and Commercial Services',
    'COUNTRY' : 'Arkansas',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ark.org/corp-search/index.php", 
                        "Source Description": "The Business and Commercial Services (BCS) Division provides a wide range of services to individuals and companies who conduct business within Arkansas, whether they''re based inside the state or elsewhere. The BCS division combines several departments under one convenient umbrella to streamline customer service."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.ark.org/corp-search/index.php'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Arkansas Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

# display = Display(visible=0,size=(800,600))
# display.start()
arkansas_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = arkansas_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False,Nopecha=False)
driver.set_page_load_timeout(30)
actions = ActionChains(driver)

def generate_merged_numbers(start_number):
    if 10000000 <= start_number <= 199999999:
        range1 = range(start_number, 199999999)
        range2 = range(200000000, 399999999)
        range3 = range(800000000, 899999999)
    elif 200000000 <= start_number <= 399999999:
        range1 = range(0)
        range2 = range(start_number, 399999999)
        range3 = range(800000000, 899999999)
    elif 800000000 <= start_number <= 899999999:
        range1 = range2 = range(0)
        range3 = range(start_number, 899999999)

    for num in range1:
        yield num
    for num in range2:
        yield num
    for num in range3:
        yield num

def get_image_text(browser):
    max_retries = 5
    for retry in range(1, max_retries + 1):
        try:
            time.sleep(2)
            tag = browser.find_element(By.XPATH, '/html/body/main/img')
            tag.screenshot('captcha/captcha.png')
            with open('captcha/captcha.png', 'rb') as image_file:
                image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')
                captcha_text = nopecha.Recognition.solve(
                    type='textcaptcha',
                    image_urls=[image_64_encode],
                )
                captcha_text_cleaned = str(captcha_text).replace("[", "").replace("]", "").replace("'", "").strip()
                return captcha_text_cleaned
        except Exception as e:
            print(e)
            if retry < max_retries:
                print(f"Retrying... Attempt {retry} of {max_retries}")
            else:
                print(f"Maximum retries ({max_retries}) reached. Giving up.")

def identify_captcha_txt(browser):
    img = browser.find_element(By.XPATH, '/html/body/main/img')
    img.screenshot('custom_crawlers/kyb/arkansas/captcha/captcha.png')
    with open('custom_crawlers/kyb/arkansas/captcha/captcha.png', 'rb') as image_file:
        image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')
        captcha_text = nopecha.Recognition.solve(
            type='textcaptcha',
            image_urls=[image_64_encode],
        )
        captcha_text_cleaned = str(captcha_text).replace("[", "").replace("]", "").replace("'", "").strip()
        return captcha_text_cleaned

try:
    start_number = 10000000 #811412545
    merged_generator = generate_merged_numbers(start_number)
    wait = WebDriverWait(driver, 10)
    max_retries = 5
    timeout_max_retries = 3
    for num in merged_generator:
        timeout_retries = 0
        while timeout_retries < timeout_max_retries:
            try:
                driver.get("https://www.ark.org/corp-search/index.php")
                img_element = driver.find_elements(By.XPATH, '/html/body/main/img')
                if len(img_element) > 0:
                    retries = 0
                    while retries < max_retries:
                        try:
                            captcha_txt = identify_captcha_txt(driver)
                            send_text = driver.find_element(By.XPATH, '/html/body/main/form/input[1]')
                            send_text.clear()
                            send_text.send_keys(captcha_txt)
                            verify_button = driver.find_element(By.XPATH, "//input[@type='submit']")
                            verify_button.click()
                            time.sleep(3)
                            driver.find_element(By.CSS_SELECTOR,"input#FilingNum")
                            break
                        except Exception as e:
                            pass
                        retries += 1
                print(f"Record No: {num}")
                search_filling_number = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#FilingNum")))
                search_filling_number.send_keys(num)
                click_on_button = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[@type='submit']")))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("arguments[0].click();", click_on_button)
                # click_on_button.click()
                links = wait.until(EC.element_to_be_clickable((By.XPATH,'//td[@class="name text-primary pe-auto"]')))
                links.click()
                time.sleep(3)

                soup=BeautifulSoup(driver.page_source,"html.parser")
                people_detail=[]
                addresses_detail=[]
                corp_name = soup.find(id="corp_name").text
                fictitious_name=soup.find(id="fictitious-name")
                if fictitious_name:
                    fictitious_name_value=fictitious_name.text

                filing_number = soup.find(id="filing-number").text
                file_under_act = soup.find(id="file-under-act").text
                reg_agent = soup.find(id="reg-agent").text
                aggent_address=soup.find(id="agent-address").text
                people_detail.append({
                    'designation': 'registered_agent',
                    'name':reg_agent,
                    'address':aggent_address
                })
                filing_type = soup.find(id="filing-type").text
                status = soup.find(id="status").text
                state_origin=soup.find(id="state-origin")
                if state_origin:
                    state_origin=state_origin.text
                    
                principal_address = soup.find(id="principal-address")
                if principal_address:
                    principal_address_value=principal_address.text
                    addresses_detail.append({
                        "type": "general_address",
                        "address":principal_address_value,
                    })
                date_filed = soup.find(id="date-filed").text.replace('/', '-') if soup.find(id="date-filed") is not None else ''
                officers = soup.find(id="officers")
                if "SEE FILE" not in soup.find(id="officers").text:
                    if officers:
                        try:
                            officers_txt = officers.get_text()
                            officers_lines = [line.strip() for line in officers_txt.split('\n') if line.strip()]
                            people_detail = []
                            for officers_line in officers_lines:
                                txt = officers_line.split(',')
                                people_detail.append({
                                    'designation': txt[1].strip(),
                                    'name':txt[0].strip()
                                })
                        except:
                            people_detail.append({
                                'designation': 'officer',
                                'name':officers.text.replace("  ", "").replace("\n", " ")
                            })

                foreign_name = soup.find(id="foreign-name")
                if foreign_name:
                    foreign_name=foreign_name.text

                foreign_address = soup.find(id="foreign-address")
                if foreign_address:
                    addresses_detail.append({
                            "type": "foreign_address",
                            "address":foreign_address.text,
                        })

                OBJ = {
                    'name':corp_name,
                    'aliases':fictitious_name,
                    'registration_number':filing_number,
                    'type':filing_type,
                    'file_under_act':file_under_act,
                    'status':status,
                    'jurisdiction':state_origin if state_origin is not None else '',
                    'registration_date':date_filed,
                    'foreign_name':foreign_name,
                    'addresses_detail':addresses_detail,
                    'people_detail':people_detail,
                
                }
                OBJ =  arkansas_crawler.prepare_data_object(OBJ)
                ENTITY_ID = arkansas_crawler.generate_entity_id(company_name=OBJ['name'], reg_number=OBJ['registration_number'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = ""
                ROW = arkansas_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                arkansas_crawler.insert_record(ROW)
                break
            except TimeoutException:
                print(f"Timeout exception occurred on record {num}. Retrying...")
                timeout_retries += 1
                # time.sleep(60)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    arkansas_crawler.db_log(log_data)
    arkansas_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    

    arkansas_crawler.db_log(log_data)
# display.stop()
