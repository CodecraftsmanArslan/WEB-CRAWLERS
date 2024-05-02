"""Import required library"""
import sys, os, traceback, time, base64
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import nopecha as nopecha1
import nopecha as nopecha2
load_dotenv()
nopecha1.api_key = os.getenv('NOPECHA_API_KEY1')
nopecha2.api_key = os.getenv('NOPECHA_API_KEY2')


meta_data = {
    'SOURCE' :'Integrated Companies Registry Information System (ICRIS)',
    'COUNTRY' : 'Hong Kong S.A.R.',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.icris.cr.gov.hk/csci/cps_criteria.jsp", 
                        "Source Description": "The Integrated Companies Registry Information System (ICRIS) is an online platform used by the Companies Registry in Hong Kong. It serves as a central repository of information and a digital platform for conducting various company-related transactions and accessing corporate data. The system allows users to search and retrieve information about registered companies, file statutory documents, make online submissions, and perform other related activities."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.icris.cr.gov.hk/csci/cps_criteria.jsp'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Hong Kong S.A.R. Official Registry"
}

hong_kong_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  hong_kong_crawler.get_requests_helper()
selenium_helper =  hong_kong_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

# arguments = sys.argv
# PAGE = int(arguments[1]) if len(arguments)>1 else 1

start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
end_number = int(sys.argv[2]) if len(sys.argv) > 2 else 3289124

def resolve_captcha(driver):
    """
    Description: This function resolves the text captcha part using the provided Selenium WebDriver.
    @param:
    - driver (WebDriver): The Selenium WebDriver used for interacting with the website.
    @return:
    - str: The resolved captcha text.
    """
    el = driver.find_element(By.ID, 'CaptchaCode')
    el.screenshot('captcha/captcha.png')

    with open('captcha/captcha.png', 'rb') as image_file:
        image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')

    captcha_text = "abcd"
    try:
        try:
            captcha_text = nopecha1.Recognition.solve(
                type='textcaptcha',
                image_urls=[image_64_encode],
            )
        except nopecha1.InsufficientCreditError:
            captcha_text = nopecha2.Recognition.solve(
                type='textcaptcha',
                image_urls=[image_64_encode],
            )
    except Exception as e:
        print('Unable to use nopecha API because', e)

    if not captcha_text:
        captcha_text = "abcd"

    return captcha_text

def login(driver):
    """
    Descirption:This function performs the login process on a specific website using the provided Selenium WebDriver.
    @param:
    - driver (WebDriver): The Selenium WebDriver used for interacting with the website.
    @return:
    - List[Dict]: A list of dictionaries containing cookie information after successful login.
    """
    driver.get('https://www.icris.cr.gov.hk/csci/')
    time.sleep(10)
    try:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
    except:
        driver.find_element(By.XPATH, '/html/body/p/table/tbody/tr[4]/td/b/font/a').click()
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
    unregistrreduser = driver.find_element(By.XPATH,'/html/body/table/tbody/tr[5]/td/table/tbody/tr/td[3]/a')
    unregistrreduser.click()
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    chinese_name = driver.find_element(By.XPATH,"/html/body/form/table/tbody/tr/td/div/div/div/table/tbody/tr[1]/td[2]/input")
    chinese_name.send_keys('勒穆赫')
    eng_name = driver.find_element(By.ID, 'eng_sur_name')
    eng_name.send_keys('abc')
    other_eng_name = driver.find_element(By.ID, 'eng_other_name')
    other_eng_name.send_keys('deg')
    radio = driver.find_element(By.XPATH,'/html/body/form/table/tbody/tr[4]/td/div/div[2]/div[4]/table/tbody/tr[3]/td[1]/input')
    radio.click()
    select_id = Select(driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/div[2]/div[4]/table/tbody/tr[3]/td[3]/select'))
    select_id.select_by_value('3')
    select_pk = Select(driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/div[2]/div[4]/table/tbody/tr[5]/td[3]/select'))
    select_pk.select_by_value('PAK')
    driver.find_element(By.XPATH,'/html/body/form/table/tbody/tr[4]/td/div/table/tbody/tr[1]/td/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/a/img').get_attribute('src')
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/div[2]/div[4]/table/tbody/tr[6]/td[3]/input').send_keys('123')
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/div[2]/div[4]/table/tbody/tr[7]/td[3]/input').send_keys('5432324336834')
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/table/tbody/tr[6]/td[2]/input[1]').click()
    time.sleep(2)

    captcha_resolved = False
    while(not captcha_resolved):
        captcha_text = resolve_captcha(driver)
        
        verification_code = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/input')
        captcha_text_cleaned = str(captcha_text).replace("[","").replace("]","").replace("'","")
        verification_code.send_keys(captcha_text_cleaned)
        time.sleep(3)
        submit = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div/table/tbody/tr[22]/td/input[2]')
        submit.click()
        time.sleep(3)
        if driver.page_source.find('Incorrect VERIFICATION CODE entered.') != -1:
            back = driver.find_element(By.XPATH,'/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[3]/td/input')
            back.click()
            time.sleep(2)
        else:
            captcha_resolved = True
  
    return driver.get_cookies()

# time.sleep(1200)
cookies = login(driver)

def wait_for_captcha_resolve():
    """
    Descirption: Waits for the resolution of a captcha on the current webpage using the global Selenium WebDriver 'driver'.
    This function captures a screenshot of the captcha, sends it to an external service (Nopecha API),
    and enters the resolved captcha text into the verification code input field. It handles incorrect
    verification codes and refreshes the captcha if needed.

    @return:
    - None
    """
    global driver
    captcha_resolved = False
    while(not captcha_resolved):
        
        captcha_text = resolve_captcha(driver)

        verification_code = driver.find_element(By.XPATH, '/html/body/div/div/table[3]/tbody/tr[1]/td/form/table/tbody/tr[3]/td/input[1]')
        captcha_text_cleaned = str(captcha_text).replace("[","").replace("]","").replace("'","")
        verification_code.send_keys(captcha_text_cleaned)
        time.sleep(3)
        submit = driver.find_element(By.XPATH, '/html/body/div/div/table[3]/tbody/tr[1]/td/form/table/tbody/tr[3]/td/input[2]')
        submit.click()
        time.sleep(3)
        if driver.page_source.find('Incorrect VERIFICATION CODE entered.') != -1:
            driver.back()
            time.sleep(2)
            driver.execute_script('''
                        javascript:document.body.style.cursor = 'wait';RefreshCaptcha3();
                ''')
            time.sleep(6)
        else:
            captcha_resolved = True

def main_function():
    """
    Description: This function performs the main crawling process for data from a Hong Kong government website.
    @return:
    - Tuple: The status code, data size, and content type of the crawled data.
    """
    COOKIES = ''
    for cookie in cookies:
        COOKIES += f"{cookie['name']}={cookie['value']};"

    DATA_API = "https://www.icris.cr.gov.hk/csci/cps_criteria.do"

    HEADERS = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type":"application/x-www-form-urlencoded",
        "Cookie": COOKIES[:-1]
    }
    RETRY = False
    for number in range(start_number,end_number+1):
        if RETRY:
            time.sleep(10)
            number = number-1
        cr_no = str(number).zfill(7)
        print("cr_no",cr_no)
        body = f"nextAction=cps_criteria&searchPage=True&DPDSInd=true&searchMode=BYCRNO&CRNo={cr_no}&LPFbrn=&radioButton=BYCRNO&ViewOfCRNo={number}&language=en&companyName=&mode=EXACT+NAME&showMedium=true&page=1w"
        data_res = request_helper.make_request(DATA_API,method='POST',headers=HEADERS,data=body)
        if data_res is None:
            RETRY = True
            continue
        STATUS_CODE = data_res.status_code
        DATA_SIZE = len(data_res.content)
        CONTENT_TYPE = data_res.headers['Content-Type'] if 'Content-Type' in data_res.headers else 'N/A'
        
        soup = BeautifulSoup(data_res.content, 'html.parser')
        # Extract information from the first table
        
        table1 = soup.find('table', width='99%')
        data_rows = []
        try:
            data_rows = table1.find_all('tr')
        except Exception as e :
            print('checking if captcha there')
            if data_res.text.find('Please enter the VERIFICATION CODE of the above picture to continue') != -1:
                print('captcha found')
                driver.get(DATA_API)
                wait_for_captcha_resolve()
                RETRY=True
                continue
            else:
                RETRY=False

        result = {}
        for row in data_rows:
            cells_ = row.find_all('td')
            if len(cells_) == 2:
                key = cells_[0].text.strip().rstrip(':')
                value = cells_[1].text.strip()
                result[key] = value

        # Extract information from the second table
        table2 = soup.find('table', class_='data')
        try:
            data_rows = table2.find_all('tr')[1:]  # Skip the header row
        except:
            RETRY = True
            continue
        # Extract the data from each row
        rows = []
        for row in data_rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                try:
                    date = cells[0].text.strip()
                except:
                    date = ""
                name_used = cells[1].text.strip()
    
                rows.append({'Effective Date': date, 'Name Used': name_used})

        result['History'] = rows
        dissolution_date = ''
        if result["Date of Dissolution / Ceasing to Exist"] != "-":
            dissolution_date = result["Date of Dissolution / Ceasing to Exist"]
        OBJ = {
                    "name": result["Company Name"].split("\r")[0].replace("(","").replace(")",""),
                    "aliases":result['Company Name'].split("\r")[-1].replace("(","").replace(")",""),
                    "registration_number": result["CR No."],
                    "registration_date":"",
                    "status":result["Active Status"],
                    "type": result["Company Type"],
                    "incorporation_date":result["Date of Incorporation"],
                    "dissolution_date":dissolution_date,
                    "remarks":result["Remarks"].replace("-",""),
                    "winding_up_mode":result["Winding Up Mode"].replace("-",""),
                    "register_of_charges":result["Register of Charges"].replace("-",""),
                    "announcements_detail":[
                        {
                            "description":result["Important Note"].replace("-","")
                        }
                    ],
                    "previous_names_detail": [
                        {
                            "name": perious["Name Used"],
                            "update_date": perious["Effective Date"]
                        } for perious in result['History']
                    ]
                }
        
        
        OBJ =  hong_kong_crawler.prepare_data_object(OBJ)
        ENTITY_ID = hong_kong_crawler.generate_entity_id(OBJ['registration_number'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = OBJ["incorporation_date"]
        ROW = hong_kong_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        hong_kong_crawler.insert_record(ROW)
        RETRY=False
        
    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = main_function()

    hong_kong_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    hong_kong_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    hong_kong_crawler.db_log(log_data)           
    

    