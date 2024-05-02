"""Import Required Library"""
import sys, os, traceback, time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from load_env.load_env import ENV

"""Crawler Meta Data Details"""
meta_data = {
    'SOURCE' :'Ministry of Industry, Investment and Commerce - Companies Office (ORC)',
    'COUNTRY' : 'Jamaica',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.orcjamaica.com/CompanySearch.aspx?cId1=3f497b36-e763-4d95-8380-847f0733032d", 
                        "Source Description": "The COJ has four (4) main roles; to register and regulate companies and businesses, maintaining accurate and up to date records on those commercial entities, administer the National Security Interests in Personal Property Online Registry and our Beneficial Owner Online Registry. It registers local and overseas companies and individuals and firms carrying on business in Jamaica. It actively encourages voluntary compliance of companies and businesses with the Companies Act of 2004, the Companies (Amendment Act) 2013, 2017 and 2023, the Registration of Business Names Act of 1934 and strives to maintain up-to-date records of all companies and businesses registered."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.orcjamaica.com/CompanySearch.aspx?cId1=3f497b36-e763-4d95-8380-847f0733032d'
}

"""Crawler Configuration"""
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Jamaica Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

jamaica_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = jamaica_crawler.get_requests_helper()
selenium_helper = jamaica_crawler.get_selenium_helper()

"""Input Arguments"""
start_year = int(sys.argv[1]) if len(sys.argv)>1 else 1980
end_year = int(sys.argv[2]) if len(sys.argv)>2 else 2023

start_num = int(sys.argv[3]) if len(sys.argv)> 3 else 0
end_num = int(sys.argv[4]) if len(sys.argv)> 4 else 100000

"""Combine Years and Numbers for Searching"""
combination_numbers = []
for year in range(start_year, end_year + 1):
    for number in range(start_num, end_num + 1):
        combination_numbers.append(f"{year}/{number}")

"""Intialize Webdriver"""
driver = selenium_helper.create_driver(headless=True, Nopecha=False)

def main_function(URL, combination_numbers):
    """
    Description: Main Function for inserting data in DB and papare data object
    @param:
    - URL: (str)
    @return:
    - Data Size: (int)
    """
    driver.get(URL)
    time.sleep(8)
    DATA_SIZE = len(driver.page_source)
    for number_ in combination_numbers:
        print('\nSearch Number =', number_,'\n')
        
        if 'We apologize for the inconvenience, but our website is currently offline' in driver.page_source:
            print("\n**** The website is currently offline. ****\n")
            break
        elif 'WEBSITE OFFLINE' in driver.page_source:
            print("\n**** The website is currently offline. ****\n")
            print("\n****The website will be offline between the hours of 1:30 A.M. to 3:30 A.M. Need to try after this time.****\n")
            break
        
        if len(driver.find_elements(By.ID,'ctl00_Space_org_name')) ==0:
            continue
        search_number = driver.find_element(By.ID,'ctl00_Space_org_name')
        search_number.send_keys(number_)
        time.sleep(2)
        if len(driver.find_elements(By.ID,'ctl00_Space_btnSearch')) == 0:
            continue
        search_btn = driver.find_element(By.ID,'ctl00_Space_btnSearch')
        search_btn.click()
        time.sleep(15)
        if 'Error Occurred' in driver.page_source:
            print("No Data Found")
            driver.back()
            time.sleep(2)
            clear_btn = driver.find_element(By.XPATH,'//*[@id="main-wrap"]/section/div/div/div[5]/button[1]')
            clear_btn.click()
            continue
        
        table = driver.find_element(By.CLASS_NAME,'resultstables')
        data = {}
        if table:
            rows = table.find_elements(By.TAG_NAME,'tr')
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME,'td')
                number = cells[0].text.strip()
                entity_name = cells[1].text.strip()
                element = cells[1].find_element(By.CLASS_NAME, "table_link")
                data_content_value = element.get_attribute("data-content")
                directors = cells[2].text.strip()
                status = cells[3].text.strip()
                entity_type = cells[4].text.strip()
                reg_date = cells[5].text.strip()
                data['name'] = entity_name
                data['registration_number'] = number
                data['directors'] = directors
                data['type'] = entity_type
                data['registration_date'] = reg_date
                data['address'] = data_content_value

        people_details = []
        try:
            name = data.get('directors','').split('-')[0].strip()
            designation = data.get('directors','').split('-')[1].strip()
        except:
            name, designation = "",""
        if name != "":
            people_details.append({
                "name":name,
                "designation":designation
            })
        try:
            business_location = data.get('registration_number','').split(' (')[1].replace(")","").strip()
            registration_number = data.get('registration_number','').split(' (')[0].strip()
        except:
            registration_number = data.get('registration_number','')
            business_location = ""
        
        address_detail = []
        if data.get("address","") != "":
            address_detail.append({
                    "type": "general_address",
                    "address":data.get('address', '').replace(' , , ',"").strip(),
                    })
        OBJ = {
                "registration_number":registration_number,
                "registration_date":data.get('registration_date',''),
                "business_location":business_location,
                "name":data.get('name',''),
                "addresses_detail":address_detail,
                "people_detail":people_details,
            }

        OBJ =  jamaica_crawler.prepare_data_object(OBJ)
        ENTITY_ID = jamaica_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ''
        ROW = jamaica_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        jamaica_crawler.insert_record(ROW)
        search_again = driver.find_element(By.XPATH,'//*[@id="main-wrap"]/section/div/div/div[1]/p/a')
        search_again.click()
        time.sleep(2)

    return DATA_SIZE

try:
    DATA_SIZE = main_function('https://www.orcjamaica.com/CompanySearch.aspx', combination_numbers)
    """Success DB logs"""
    jamaica_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    jamaica_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    """Error DB logs with path"""
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    jamaica_crawler.db_log(log_data)
