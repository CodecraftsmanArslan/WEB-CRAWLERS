"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import os, json
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

'''GLOBAL VARIABLES'''
DATA_SIZE = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

meta_data = {
    'SOURCE' :'Inuit Firm Registry',
    'COUNTRY' : 'Nunavut',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://inuitfirm.tunngavik.com/search-the-registry/#results", 
                        "Source Description": "The Inuit Firm Registry Database is maintained by Nunavut Tunngavik Inc.'s Policy & Planning Department. The database contains a list of Inuit firms that meet the criteria of Article 24 of the Nunavut Agreement"},
    'URL' : 'https://inuitfirm.tunngavik.com/search-the-registry/#results',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Nunavut Official Registry'
}

nunavut_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  nunavut_crawler.get_requests_helper()
selenium_helper = nunavut_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

driver.get("https://inuitfirm.tunngavik.com/search-the-registry/#results")
DATA_SIZE = len(driver.page_source)
time.sleep(2)
searchinput = driver.find_element(By.XPATH, "//*[@id='post-2734']/div/div[2]/div/form/div[17]/input")
searchinput.click()
time.sleep(2)
try:
    # Get the table element containing the search results
    table = driver.find_element(By.XPATH,'//*[@id="post-2734"]/div/div[2]/div/table')
    # Find all the rows in the table
    table_body = table.find_element(By.TAG_NAME, 'tbody')
    rows = table_body.find_elements(By.XPATH, './/tr')
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        urls = cells[1].find_element(By.TAG_NAME,'a').get_attribute('href')
        response = request_helper.make_request(urls)
        soup = BeautifulSoup(response.content,'html.parser')
        name = soup.find(class_ = 'subTitle').text.strip()
        registration_number = soup.find(class_ = 'if_business_as').text.strip()
        try:
            registration_date = soup.find(class_ = 'if_certification').text.strip()
        except:
            registration_date = ""
        try:
            aliases = soup.select_one('#post-2540 > div > div:nth-child(4)').text.strip()
        except:
            aliases = ""
        try:
            industries = soup.find(class_ = 'if_businesssummary').text.strip()
        except:
            industries = ""
        address = soup.find(class_ = 'firm_address').get_text(separator=" ", strip=True)+' '+soup.find(class_ ='if_region').text.strip()
        phone_num = soup.find(class_ = 'if_phone').text.strip().split(':')[-1] if soup.find(class_ = 'if_phone') else ""
        fax_num = soup.find(class_ = 'if_fax').text.strip().split(':')[-1] if soup.find(class_ = 'if_fax') else ""
        email = soup.find(class_ = 'if_email').text.strip().split(':')[-1] if soup.find(class_ = 'if_email') else ""
        person_name = soup.find(class_ = 'if_contact').text.strip() if soup.find(class_ = 'if_contact') else ""
        class_number = soup.find(class_ = 'if_classification').text.strip() if soup.find(class_ = 'if_classification') else ""
        naics_details = soup.find_all('div', class_='naics_details')
        data = []     
        for naics_detail in naics_details:
            code_names = naics_detail.find_all('div', class_='single_parent_item')
            code_descriptions = naics_detail.find_all('div', class_='single_child_group')
            for code_name, code_description in zip(code_names, code_descriptions):
                data.append({
                    "code_name": code_name.get_text(strip=True),
                    "code_description": code_description.get_text(strip=True)
                })
        
        OBJ = {
            "registration_number":registration_number,
            "name":name,
            "industries":industries,
            "aliases":aliases,
            "registration_date":registration_date,
            "class_number":class_number,
            "addresses_detail":[
                {
                    "type":"general_address",
                    "address":address
                }
            ],
            "contacts_detail":[
                {
                    "type":"phone_number",
                    "value":phone_num
                },
                {
                    "type":"fax_number",
                    "value":fax_num
                },
                {
                    "type":"email",
                    "value":email
                }
            ],
            "additional_detail":[
                {
                    "type": "NAICS_information",
                    "data":data
                }
            ],
            "people_detail":[
                {
                    "designation":"contact_person",
                    "name":person_name
                }
            ]
        }
        OBJ =  nunavut_crawler.prepare_data_object(OBJ)
        ENTITY_ID = nunavut_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = nunavut_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)

        nunavut_crawler.insert_record(ROW)

    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    nunavut_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    nunavut_crawler.db_log(log_data)



