"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from selenium.common.exceptions import TimeoutException

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Jersey Financial Services Commission',
    'COUNTRY' : 'Jersey',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.jerseyfsc.org/registry/", 
                        "Source Description": "The Jersey Financial Services Commission (JFSC) is the regulatory authority responsible for the supervision and regulation of financial services in the jurisdiction of Jersey. Jersey is a self-governing British Crown Dependency located in the English Channel. The JFSC's main objective is to maintain the integrity, stability, and reputation of Jersey's financial services sector."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.jerseyfsc.org/registry/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Jersey",
}
display = Display(visible=0,size=(800,600))
display.start()
jersy_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = jersy_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False,Nopecha=True)

# handle the navigation with retries
def navigate_with_retry(driver, url, max_retries=3, timeout=10):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            print("Navigation successful!")
            return  # Exit the loop if navigation is successful
        except TimeoutException:
            print(f"Timeout occurred (Attempt {retries + 1}/{max_retries})")
            retries += 1
            time.sleep(timeout)  # Wait for a while before retrying
    print("Max retries reached. Navigation failed.")

def wait_for_captcha_to_be_solved(browser):
        while True:
            try:
                time.sleep(3)
                iframe_class = browser.find_element(By.CLASS_NAME, "h-captcha")
                iframe_element = iframe_class.find_element(By.TAG_NAME, 'iframe')
                browser.switch_to.frame(iframe_element)
                print('trying to resolve captcha')
                div_element = browser.find_element(By.CLASS_NAME, "check")
                style_attribute = div_element.get_attribute("style")
                browser.switch_to.default_content()
                if "display: block" in style_attribute:
                    print("Captcha has been Solved")
                    return browser
            except Exception as e:
                print(e, 'captcha solution timeout error, retrying...')

def has_specific_style_attribute(tag):
    return tag.name == 'div' and tag.has_attr('style') and 'font-weight:bold;float:left' in tag['style']

def get_page_data(soup):
    data = {}
    registration_number = ""
    type_ = ""
    status = ""
    registered_on = ""

    name = soup.find('h1').text.strip().replace("%", "%%") if soup.find('h1') is not None else ""
    elements = soup.find_all(has_specific_style_attribute)
    for element in elements:
        text = element.text.strip()
        if text == "Registration Number:":
            registration_number = element.find_next_sibling().text.strip().replace("%", "%%") if element.find_next_sibling() is not None else ""
        elif text == "Type:":
            type_ = element.find_next_sibling().text.strip().replace("%", "%%") if element.find_next_sibling() is not None else ""
        elif text == "Status:":
            status = element.find_next_sibling().text.strip().replace("%", "%%") if element.find_next_sibling() is not None else ""
        elif text == "Registered on:":
            registered_on = element.find_next_sibling().text.strip().replace("/", "-") if element.find_next_sibling() is not None else ""
        data = {"name": name, "registration_number": registration_number, "type": type_ , "status": status, "registration_date": registered_on}
    return data

try:   
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    for num in range(start, 794100):
        formatted_num = f"{num:06d}"
        print("Record No:", formatted_num)
        url = f"https://www.jerseyfsc.org/registry/registry-entities/entity/{formatted_num}"
        navigate_with_retry(driver, url)
        if (len(driver.find_elements(By.CLASS_NAME, 'h-captcha')) > 0):
            wait_for_captcha_to_be_solved(driver)
            try:
                wait = WebDriverWait(driver, 10)
                input_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-success")))
                input_element.click()
                time.sleep(5)
            except:
                continue
        html_content = driver.page_source
        DATA_SIZE = len(html_content)
        soup = BeautifulSoup(html_content, "html.parser")
        data = get_page_data(soup)
        if len(data) == 0:
            continue
        if data.get("name") == "" and data.get("name") is not None and data.get("registration_number") == "" and data.get("registration_number") is not None:
            continue
        ENTITY_ID = jersy_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
        BIRTH_INCORPORATION_DATE = ''
        DATA = jersy_crawler.prepare_data_object(data)
        ROW = jersy_crawler.prepare_row_for_db(ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
        jersy_crawler.insert_record(ROW)


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    jersy_crawler.db_log(log_data)
    jersy_crawler.end_crawler()
    display.stop()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    jersy_crawler.db_log(log_data)
