"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
meta_data = {
    'SOURCE' :'Secretary of the Commonwealth of Massachusetts',
    'COUNTRY' : 'Massachusetts',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx", 
                        "Source Description": "The official website of the Secretary of the Commonwealth of Massachusetts serves as a comprehensive resource for various aspects of governance and public services within the state. The website provides information and services related to business registration, elections, public records, and more."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Massachusetts Official Registry"
}
display = Display(visible=0,size=(800,600))
display.start()

massachusetts_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  massachusetts_crawler.get_requests_helper()
selenium_helper = massachusetts_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=False)

url = "https://corp.sec.state.ma.us/CorpWeb/CorpSearch/CorpSearch.aspx"
driver.get(url)
time.sleep(6)

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 1
end_number = 1999999
try:
    for number in range(start_number,end_number):
        search_number = str(number).zfill(9)
        print("\nSearch_Number",search_number)
        Identification = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'MainContent_rdoByIdentification')))
        Identification.click()
        time.sleep(6)
        txtIdentificationNumber = driver.find_element(By.ID, 'MainContent_txtIdentificationNumber')
        txtIdentificationNumber.send_keys(search_number)
        time.sleep(2)
        btnSearch = driver.find_element(By.ID, 'MainContent_btnSearch')
        btnSearch.click()
        time.sleep(5)
    
        if '* No records found; try a new search using different criteria' in driver.page_source:
            print('No data found')
            driver.refresh()
            time.sleep(2)
            continue
        
        soup = BeautifulSoup(driver.page_source,'html.parser')
        c_el = soup.find('span',id='MainContent_lblEntityNameHeader')
        c_name = c_el.text if c_el else ''
        aliases = soup.find('span',id = 'MainContent_lblEntityName').text if soup.find('span',id = 'MainContent_lblEntityName') else ''
        type_ = soup.find('span',id = 'MainContent_lblEntityType').text if soup.find('span',id = 'MainContent_lblEntityType') else ''
        registration_number = soup.find('span',id = 'MainContent_lblIDNumber').text if soup.find('span',id = 'MainContent_lblIDNumber') else ''
        registration_number = registration_number.split(':')[-1].strip()
        old_el = soup.find('span',id ='MainContent_lblOldIDNumber')
        old_registration_number = old_el.text if old_el else ''
        registration_date = soup.find('span',id ='MainContent_lblOrganisationDate').text if soup.find('span',id ='MainContent_lblOrganisationDate') else ''
        reinstated_date = soup.find('span',id ='MainContent_lblRevivalDate').text if soup.find('span',id ='MainContent_lblRevivalDate') else ''
        org_el = soup.find('span',id = 'MainContent_lblOrganisationDate')
        organization_date = org_el.text if org_el else ''
        rev_el = soup.find('span',id = 'MainContent_lblRevivalDate')
        revival_date = rev_el.text if rev_el else ''
        dis_el = soup.find('span',id = 'MainContent_lblInactiveDate')
        dissolution_date = dis_el.text if dis_el else ''
        last_certain_date = soup.find('span',id = 'MainContent_lblCertainDate').text if soup.find('span',id = 'MainContent_lblCertainDate') else ''
        current_el = soup.find('span',id = 'MainContent_lblFiscalDateCurrent')
        current_fiscal = current_el.text if current_el else ''
        previos_el = soup.find('span',id = 'MainContent_lblFiscalMonthPrevioud')
        previous_fiscal = previos_el.text if previos_el else ''
        address_el = soup.find('span',id = 'MainContent_lblPrincipleStreet')
        pricipal_office_address = address_el.text if address_el else ''
        city_el = soup.find('span',id = 'MainContent_lblPrincipleCity')
        pricipal_city = city_el.text if city_el else ''
        state_el = soup.find('span',id = 'MainContent_lblPrincipleState')
        pricipal_state = state_el.text if state_el else ''
        zipp_el = soup.find('span',id = 'MainContent_lblPrincipleZip')
        pricipal_zip =zipp_el.text if zipp_el else ''
        country_el = soup.find('span',id = 'MainContent_lblPrincipleCountry')
        pricipal_country = country_el.text if country_el else ''
        office_address = soup.find('span',id = 'MainContent_lblOfficeStreet')
        massachusetts_office = office_address.text if office_address else ''
        city_ell = soup.find('span',id = 'MainContent_lblOfficeCity')
        office_city = city_ell.text if city_ell else ''
        state_ell = soup.find('span',id = 'MainContent_lblOfficeState')
        office_state = state_ell.text if state_ell else ''
        zip_ell = soup.find('span',id = 'MainContent_lblOfficeZip')
        office_zip = zip_ell.text if zip_ell else ''
        count_ell = soup.find('span',id = 'MainContent_lblOfficeCountry')
        office_country = count_ell.text if count_ell else ''
        agent_name_el = soup.find('span',id = 'MainContent_lblResidentAgentName')
        agent_name = agent_name_el.text if agent_name_el else ''
        agent_address_el = soup.find('span',id = 'MainContent_lblResidentStreet')
        agent_address = agent_address_el.text if agent_address_el else ''
        agent_city_el = soup.find('span',id = 'MainContent_lblResidentCity')
        agent_city = agent_city_el.text if agent_city_el else ''
        agent_state_el = soup.find('span',id = 'MainContent_lblResidentState')
        agent_state = agent_state_el.text if agent_state_el else ''
        agent_zip_el = soup.find('span',id = 'MainContent_lblResidentZip')
        agent_zip = agent_zip_el.text if agent_zip_el else ''
        agent_coun_el = soup.find('span',id = 'MainContent_lblResidentCountry')
        agent_country = agent_coun_el.text if agent_coun_el else ''
        people_detail = []
        try:
            table = soup.find('table',id= 'MainContent_grdOfficers')
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    title = cells[0].text.strip()
                    name_ = cells[1].text.strip()
                    try:
                        address_ = cells[2].text.strip()
                    except:
                        address_ = ""
                    new_detail = {
                    "designation":title,     
                    "name":name_,
                    "address":address_              
                    }
                    people_detail.append(new_detail)
        except:
            table = soup.find('table',id= 'MainContent_grdManagers')
            if table:
                rows = table.find_all('tr')
                people_detail = []
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    title = cells[0].text.strip()
                    name_ = cells[1].text.strip()
                    try:
                        address_ = cells[2].text.strip()
                    except:
                        address_ = ""
                    new_detail = {
                    "designation":title,     
                    "name":name_,
                    "address":address_              
                    }
                    people_detail.append(new_detail)
            
        
        grdPersons_table = soup.find('table',id= 'MainContent_grdPersons')
        if grdPersons_table:
            grdPersons_rows = grdPersons_table.find_all('tr')
            for _row in grdPersons_rows[1:]:
                _cells = _row.find_all(['td', 'th'])
                _title = _cells[0].text.strip()
                _name = _cells[1].text.strip()
                try:
                    _address = _cells[2].text.strip()
                except:
                    _address = ""
                new_detail = {
                "designation":_title,     
                "name":_name,
                "address":_address              
                }
                people_detail.append(new_detail)
        
        if agent_name != '':
            agent_info = {
                "designation": "registered_agent",
                "name": agent_name,
                "address": str(agent_address + ' ' + agent_country + ' ' + agent_city + ' ' + agent_state + ' ' + agent_zip).strip()
            }
            people_detail.append(agent_info)


        ViewFilings = driver.find_element(By.ID, 'MainContent_btnViewFilings')
        ViewFilings.click()
        time.sleep(5)
        fsoup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            filing_table = fsoup.find('table', id = 'MainContent_grdSearchResults')
            filing_details = []
            if filing_table:
                filing_rows = filing_table.find_all('tr')
                base_url = 'https://corp.sec.state.ma.us/CorpWeb/CorpSearch/'
                for filing_row in filing_rows[1:]:
                    filing_cells = filing_row.find_all('td')
                    filing_name = filing_cells[0].text.strip()
                    filing_year = filing_cells[1].text.strip()
                    filing_date = filing_cells[2].text.strip()
                    filing_no = filing_cells[3].text.strip()
                    try:
                        filing_url = base_url+filing_cells[4].find('a')['href']
                    except:
                        filing_url  = ''
                    
                    filing_dict= {
                            "title":filing_name,
                            "date":filing_date.replace("/","-"),
                            "filing_code":filing_no,
                            'filing_url':filing_url,
                            "meta_detail":{
                            "year":filing_year.replace("/","-"),
                        },
                    }
                    filing_details.append(filing_dict)
        except:
            filing_details = []
        driver.back()
        time.sleep(5)
        driver.back()

        OBJ = {
                    "name": c_name.replace('"',''),
                    "aliases": aliases,
                    "type": type_,
                    "registration_number": registration_number,
                    "old_registration_number": old_registration_number,
                    "registration_date": registration_date,
                    "reinstated_date": reinstated_date,
                    "organization_date":organization_date,
                    "revival_date":revival_date,
                    "dissolution_date":dissolution_date,
                    "last_certain_date":last_certain_date,
                    "current_fiscal_month_day":current_fiscal,
                    "previous_fiscal_month_fay":previous_fiscal,
                    "additional_detail":[
                        {
                            "type": "organized_under_the_laws_of",
                            "data":[
                                {
                                "state":pricipal_state,
                                "country":pricipal_country,
                                "date":registration_date
                                }
                            ]
                        }
                    ],
                    "addresses_detail":[
                        {
                            "type": "pricipal_office_address",
                            "address":str(pricipal_office_address.replace("UNKNOWN","")+' '+pricipal_country+' '+pricipal_city.replace("UNKNOWN,","")+' '+pricipal_state+' '+pricipal_zip).strip()
                        },
                        {
                            "type":"massachusetts_office",
                            "address":massachusetts_office+' '+office_country+' '+office_city+' '+office_state+' '+office_zip
                        }
                    ],
                    "people_detail":people_detail,
                    "fillings_detail": filing_details
                }
        
        OBJ =  massachusetts_crawler.prepare_data_object(OBJ)
        ENTITY_ID = massachusetts_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = massachusetts_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        massachusetts_crawler.insert_record(ROW)    


    massachusetts_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    massachusetts_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    massachusetts_crawler.db_log(log_data)
