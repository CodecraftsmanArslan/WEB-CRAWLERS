"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import nopecha, base64,os
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import nopecha as nopecha
load_dotenv()

nopecha.api_key = os.getenv('NOPECHA_API_KEY2')

meta_data = {
    'SOURCE' :'Ministry of Economy and Innovation - Register of Legal Entities',
    'COUNTRY' : 'Lithuania',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.registrucentras.lt/jar/p_en/", 
                        "Source Description": "State Enterprise Centre of Registers (SECR) is a public entity of limited civil liability incorporated by the Government of the Republic of Lithuania on the basis of the State-owned property on 8 July 1997. Their mission is to meet the needs of society by managing the entrusted State information resources in an efficient and reliable manner."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.registrucentras.lt/jar/p_en/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Lithuania Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

lithuania_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = lithuania_crawler.get_requests_helper()
selenium_helper = lithuania_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=True, Nopecha=False)
driver.get('https://www.registrucentras.lt/jar/p_en/')
time.sleep(4)

action = ActionChains(driver=driver)

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 100000000
end_number = 399000000
try:
    for number in range(start_number, end_number):
        print("\nSearch Number =", number)
        search_code = driver.find_element(By.XPATH,'//*[@id="kod"]')
        search_code.send_keys(number)
        time.sleep(3)
        captcha_resolved = False
        while(not captcha_resolved):
            
            if len(driver.find_elements(By.XPATH,'//*[@id="F1"]/table/tbody/tr[4]/td[1]/img'))==0:
                continue
            el = driver.find_element(By.XPATH,'//*[@id="F1"]/table/tbody/tr[4]/td[1]/img')
            el.screenshot('captcha/captcha.png')

            with open('captcha/captcha.png', 'rb') as image_file:
                image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')
            try:
                captcha_text = nopecha.Recognition.solve(
                    type='textcaptcha',
                    image_urls=[image_64_encode],
                )
                if captcha_text:
                    captcha_resolved = True
                else:
                    print("Captcha not solved. Retrying...")
            except Exception as e:
                print('Unable to use Nopecha APi beacuse',)
                captcha_resolved = False


        captcha_code = driver.find_element(By.XPATH,'//*[@id="a"]')
        captcha_code.send_keys(captcha_text)
        time.sleep(2)
        search_btn = driver.find_element(By.XPATH,'//*[@id="F1"]/table/tbody/tr[5]/td[2]/table/tbody/tr/td[1]/input')
        search_btn.click()
        time.sleep(2)
        if 'Error: Wrong captcha code' in driver.page_source:
            captcha_resolved = False

        if 'No results found' in driver.page_source:
            search_code = driver.find_element(By.XPATH,'//*[@id="kod"]')
            action.move_to_element(search_code).double_click().send_keys(Keys.DELETE).perform()
            continue
    
        if len(driver.find_elements(By.CLASS_NAME,'res1')) == 0:
            continue
        table  = driver.find_element(By.CLASS_NAME,'res1')
        all_rows = table.find_elements(By.TAG_NAME,'tr')
        data = {}
        for row in all_rows[1:]:
            cells = row.find_elements(By.TAG_NAME,'td')
            code  = cells[0].text.strip()
            href = cells[0].find_element(By.TAG_NAME,'a').get_attribute('href')
            name_ = cells[1].text.strip().split('\n')[0].strip()
            address = cells[1].text.strip().split('\n')[-1].strip()
            try:
                address_url = cells[1].find_element(By.TAG_NAME,'a').get_attribute('href')
            except:
                address_url = ''
            Legal_form = cells[2].text.strip()
            status = cells[3].text.strip()
            data['code'] = code
            data['href'] = href
            data['name'] = name_
            data['type'] = Legal_form
            data['status'] = status
            data['address_url'] = address_url
            data['address'] = address

        filings_detail = []
        response = request_helper.make_request(data.get('href'))
        soup = BeautifulSoup(response.content, 'html.parser')
        doc_table = soup.find_all('table')[14]
        trs = doc_table.find_all('tr')
        for tr in trs[1:]:
            cells_ = tr.find_all('td')
            title = cells_[0].get_text(strip = True).split(' / ')
            doc_title = title[0].strip()
            try:
                description = title[1].strip()
            except:
                description = ''
            date = cells_[1].get_text(strip = True)
            receiving_date = cells_[2].get_text(strip = True)
            registered = cells_[3].get_text(strip = True)
            filings_detail.append({
                "title":doc_title,
                'date':date,
                'description':description,
                'meta_detail':{
                    "receiving_date":receiving_date,
                    'registered':registered
                    }
            })

        OBJ = {
                "registration_number":data.get('code',''),
                "name":data.get('name','').replace('\"',''),
                'type':data.get('type',''),
                'status':data.get('status',''),
                "addresses_detail":[
                    {
                    "type": "registered_address",
                    "address":data.get('address',''),
                    "meta_detail":{
                        "map_url": data.get('address_url','')
                        }
                    },
                ],
                "fillings_detail":filings_detail
            }

        OBJ =  lithuania_crawler.prepare_data_object(OBJ)
        ENTITY_ID = lithuania_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ''
        ROW = lithuania_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        lithuania_crawler.insert_record(ROW)
        search_code = driver.find_element(By.XPATH,'//*[@id="kod"]')
        action.move_to_element(search_code).double_click().send_keys(Keys.DELETE).perform()
    

    lithuania_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    lithuania_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    lithuania_crawler.db_log(log_data)