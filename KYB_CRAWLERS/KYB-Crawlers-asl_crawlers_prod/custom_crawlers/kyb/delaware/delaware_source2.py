"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Division of Corporations Delaware',
    'COUNTRY' : 'Delaware',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx", 
                        "Source Description": "The Delaware Division of Corporations is a state agency that administers the corporate registry and laws. It oversees company incorporation, filings, and records for over 1 million legal entities registered in Delaware."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Delaware Official Registry Source Two"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

delaware_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  delaware_crawler.get_requests_helper()
s =  delaware_crawler.get_requests_session()
selinum_helper = delaware_crawler.get_selenium_helper()
driver = selinum_helper.create_driver(headless=True,Nopecha=True)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'icis.corp.delaware.gov',
    'Origin': 'https://icis.corp.delaware.gov',
    'Referer': 'https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

driver.get('https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx')
time.sleep(3)

arguments = sys.argv
DUMMY_COR = int(arguments[1]) if len(arguments)>1 else 100000
try:
    for search_num in range(DUMMY_COR, 7999999):
        print("\nCurrent Search Number", search_num)
        FileNumber = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_frmFileNumber').send_keys(search_num)
        submit_button = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_btnSubmit')
        submit_button.click()
        time.sleep(10)
        if driver.page_source.find('No Records Found.') != -1:
            print("\nSkip search number", search_num)
            continue
        try:
            captcha_elements = driver.find_element(By.CLASS_NAME, "g-recaptcha")
            if captcha_elements:
                selinum_helper.wait_for_captcha_to_be_solved(driver)
                time.sleep(5)
                wait = WebDriverWait(driver, 10)
                submit_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="hdr"]/table/tbody/tr[2]/td/table[3]/tbody/tr[3]/td/form/input')))
                submit_element.click()
                time.sleep(5)
                
        except NoSuchElementException:
            print("Element not found.")
        time.sleep(2)
        try:
            if driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_frmFileNumber').get_attribute('value')== "":
                FileNumber = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_frmFileNumber')
                FileNumber.clear()
                FileNumber.send_keys(search_num)
                submit_button = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_btnSubmit')
                submit_button.click()
                time.sleep(10)
        except:
            continue

        if driver.page_source.find('No Records Found.') != -1:
            print("Skip search number", search_num)
            continue
        
        __VIEWSTATE = driver.find_element(By.ID,'__VIEWSTATE').get_attribute("value")
        __VIEWSTATEGENERATOR = driver.find_element(By.ID, '__VIEWSTATEGENERATOR').get_attribute('value')

        payload = {
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$rptSearchResults$ctl00$lnkbtnEntityName",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": f"{__VIEWSTATE}",
            "__VIEWSTATEGENERATOR": f"{__VIEWSTATEGENERATOR}",
            "ctl00$hdnshowlogout": "",
            "ctl00$hdnfilingtype": "", 
            "as_sitesearch": "", 
            "ctl00$ContentPlaceHolder1$frmEntityName": "", 
            "ctl00$ContentPlaceHolder1$frmFileNumber": search_num,
            "ctl00$ContentPlaceHolder1$hdnPostBackSource": "",
            "ctl00$ContentPlaceHolder1$lblMessage": "" 
        }

        response = s.post('https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx',headers=headers, data=payload)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.content,'html.parser')
        table = soup.find_all('table',)[7]
        rows = table.find_all('tr')
        try:
            FileNumber =rows[1].find('span',id = 'ctl00_ContentPlaceHolder1_lblFileNumber').get_text(strip = True)
            IncDate = rows[1].find('span',id = 'ctl00_ContentPlaceHolder1_lblIncDate').get_text(strip = True)
            EntityName = rows[2].find('span',id = 'ctl00_ContentPlaceHolder1_lblEntityName').get_text(strip = True)
            EntityKind = rows[3].find('span',id = 'ctl00_ContentPlaceHolder1_lblEntityKind').get_text(strip = True)
            EntityType = rows[3].find('span',id = 'ctl00_ContentPlaceHolder1_lblEntityType').get_text(strip = True)
            Residency = rows[4].find('span',id = 'ctl00_ContentPlaceHolder1_lblResidency').get_text(strip = True)
            State = rows[4].find('span',id = 'ctl00_ContentPlaceHolder1_lblState').get_text(strip = True)
            AgentName = rows[8].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentName').get_text(strip = True)
            AgentAddress1 = rows[9].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentAddress1').get_text(strip = True)
            AgentCity = rows[10].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentCity').get_text(strip = True)
            AgentCounty = rows[10].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentCounty').get_text(strip = True)
            AgentState = rows[11].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentState').get_text(strip = True)
            PostalCode = rows[11].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentPostalCode').get_text(strip = True)
            AgentPhone = rows[12].find('span',id = 'ctl00_ContentPlaceHolder1_lblAgentPhone').get_text(strip = True)
        except:
            FileNumber, IncDate, EntityName, EntityKind, EntityType, Residency, State, AgentName, AgentAddress1, AgentCity, AgentCounty, AgentState, PostalCode, AgentPhone= "","","","","","","","","","","","","",""
        OBJ = {
            "registration_number":FileNumber,
            "incorporation_date":IncDate.replace("/","-"),
            "name":EntityName.replace("\"",""),
            "type":EntityKind,
            "category":EntityType,
            "domicile":Residency,
            "jurisdiction":State,
            "people_detail":[
                {
                    "name":AgentName,
                    "designation":"registered_agent",
                    "address":AgentAddress1+' '+AgentCounty+' '+AgentCity+' '+AgentState,
                    "phone_number":AgentPhone
                }
            ]
        }
        OBJ =  delaware_crawler.prepare_data_object(OBJ)
        ENTITY_ID = delaware_crawler.generate_entity_id(OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = delaware_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        delaware_crawler.insert_record(ROW)

    delaware_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    delaware_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    delaware_crawler.db_log(log_data) 
