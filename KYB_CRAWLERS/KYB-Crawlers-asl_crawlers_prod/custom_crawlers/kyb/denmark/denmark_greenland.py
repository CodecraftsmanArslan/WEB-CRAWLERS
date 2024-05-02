"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Central Business Register of Denmark',
    'COUNTRY': 'Denmark, Greenland',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://datacvr.virk.dk/soegeresultater?fritekst=*&sideIndex=8&size=10",
                      "Source Description": "Central Business Register of Denmark, maintained by the Danish Business Authority. The website provides access to information on all registered businesses and institutions in Denmark, including data on their legal form, tax status, ownership, financial statements, and more."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://datacvr.virk.dk/soegeresultater?fritekst=*&sideIndex=8&size=10'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Denmark, Greenland Official Registry",
}

denmark_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper =  denmark_crawler.get_requests_helper()
proxy_response = request_helper.make_request('https://proxy.webshare.io/api/v2/proxy/list/download/dclobvygwpkwhkglwkfazlkbouwzulwdvcfabqpf/-/any/sourceip/direct/denmark/')
proxy_ips = proxy_response.text.split('\n')
options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=http://{proxy_ips[-2]}')
options.add_argument('--headless=true')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = uc.Chrome(version_main=119, options=options)

def get_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(strip=True)
    return text

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 10000000
end_number = 899000000
try:
    for search_number in range(start_number,end_number):
        driver.get(f"https://datacvr.virk.dk/enhed/virksomhed/{search_number}?fritekst={search_number}&sideIndex=0&size=10")
        
        if driver.page_source.find('Virksomheden kunne ikke findes') != -1:
            print("Skip search number", search_number)
            time.sleep(2)
            continue
        
        if len(driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/h1'))==0:
            continue
        Name = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/h1').text.strip()
        try:
            db_dede_elements = driver.find_elements(By.CLASS_NAME, "virksomhed-stamdata")
            db_items = {}
            for element_ in db_dede_elements:
                containers_ = element_.find_elements(By.CLASS_NAME, "row")
                for container_ in containers_:
                    label_rows_ = container_.find_elements(By.CLASS_NAME, "col-6.col-lg-3")
                    for label_row_ in label_rows_:
                        if len(label_row_.find_elements(By.XPATH, "following-sibling::div")) > 0:
                            value_div = label_row_.find_element(By.XPATH, "following-sibling::div")
                            key = re.search(r'>(.*?)<', label_row_.get_attribute("innerHTML")).group(1)
                            db_items[key] = str(value_div.get_attribute("innerHTML"))   
        except:
            pass
        #company_information
        if len(driver.find_elements(By.ID,'accordion-udvidede-virksomhedsoplysninger')) == 0:
            continue
        Udvidede = driver.find_element(By.ID,'accordion-udvidede-virksomhedsoplysninger') 
        Udvidede_elements = Udvidede.find_elements(By.CLASS_NAME, "accordion-content-inner")
        company_items = {}
        for element in Udvidede_elements:
            containers = element.find_elements(By.CLASS_NAME, "row")
            for container in containers:
                label_rows = container.find_elements(By.CLASS_NAME, "col-12.col-lg-3")
                for label_row in label_rows:
                    if len(label_row.find_elements(By.XPATH, "following-sibling::div")) > 0:
                        value_div = label_row.find_element(By.XPATH, "following-sibling::div")
                        key = re.search(r'>(.*?)<', label_row.get_attribute("innerHTML")).group(1)
                        company_items[key] = str(value_div.get_attribute("innerHTML"))
        
        #peoples_details
        people_details = []
        try:
            Tegning = driver.find_element(By.ID,'accordion-personkreds-content')
            Tegning_elements = Tegning.find_elements(By.CLASS_NAME, "accordion-content-inner")
            peoples_items = {}
            for Tegning_element in Tegning_elements:
                Tegning_containers = Tegning_element.find_elements(By.CLASS_NAME, "row")
                for Tegning_container in Tegning_containers:
                    label_rows = Tegning_container.find_elements(By.CLASS_NAME, "col-12.col-lg-4")
                    for label_row in label_rows:
                        if len(label_row.find_elements(By.XPATH, "following-sibling::div")) > 0:
                            value_div = label_row.find_element(By.XPATH, "following-sibling::div")
                            key = re.search(r'>(.*?)<', label_row.get_attribute("innerHTML")).group(1)
                            peoples_items[key] = str(value_div.get_attribute("innerHTML"))
        except:
            peoples_items = {}


        try:
            peoples_soup = BeautifulSoup(peoples_items.get('Direktion',''),'html.parser')
            designation = peoples_soup.find_all('div')[0].text.strip()
            chariman_name = peoples_soup.find('span').text.strip()
            chariman_address = peoples_soup.find_all('div')[1].text.strip()
            chariman_dict = {
                "designation":designation.replace("(","").replace(")","").lower(),
                "name":chariman_name,
                "address":chariman_address.replace("\n"," ")
            }
            people_details.append(chariman_dict)
        except:
            chariman_dict = {}
            people_details.append(chariman_dict)
        
        try:
            peoples_soup1 = BeautifulSoup(peoples_items.get('Stiftere',''))
            board_name = peoples_soup.find('span').text.strip()
            board_address = peoples_soup.find_all('div')[1].text.strip()   
            designation_ = 'Stiftere' 
            board_dict = {
                "name":board_name,
                "designation":designation_,
                "address":board_address.replace("\n"," ")
            }
            people_details.append(board_dict)
        except:
            board_dict = {}
            people_details.append(board_dict)
        
        try:
            ejerforhold = driver.find_element(By.ID,'accordion-ejerforhold-content')
            ejerforhold_elements = ejerforhold.find_elements(By.CLASS_NAME, "accordion-content-inner")
            ejerforhold_items = {}
            for ejerforhold_element in ejerforhold_elements:
                ejerforhold_containers = ejerforhold_element.find_elements(By.CLASS_NAME, "row")
                for ejerforhold_container in ejerforhold_containers:
                    label_rows = ejerforhold_container.find_elements(By.CLASS_NAME, "col-12.col-lg-3.bold")
                    for label_row in label_rows:
                        if len(label_row.find_elements(By.XPATH, "following-sibling::div")) > 0:
                            value_div = label_row.find_element(By.XPATH, "following-sibling::div")
                            key = label_row.get_attribute("innerHTML")
                            ejerforhold_items[key] = str(value_div.get_attribute("innerHTML"))
        
            ejere_soup = BeautifulSoup(ejerforhold_items.get('Legale ejere',''),'html.parser')
            legal_owner_name = ejere_soup.find('a').text.strip()
            legal_owner_address = ejere_soup.find_all('div')[2].text.strip()
            legal_owner_date = ejere_soup.find_all('div')[3].text.strip().split(':')[-1].strip()
            share_percentage = ejere_soup.find_all('div')[3].text.strip().split(":")[1].strip().split("E")[0]
            voting_percentage = ejere_soup.find_all('div')[3].text.strip().split(":")[3].strip().split("S")[0]
            legal_owner_designation  = "legal_owner"
            legal_owner_dict = {
                "name":legal_owner_name,
                "address":legal_owner_address.replace("\n"," "),
                "designation":legal_owner_designation,
                "meta_detail":{
                    "change_date":legal_owner_date,
                    "share_percentage":share_percentage.replace("%","%%"),
                    "voting_percentage":voting_percentage.replace("%","%%")
                }
            }
            people_details.append(legal_owner_dict)
        except:
            legal_owner_dict = {}
            people_details.append(legal_owner_dict)
        try:
            if ejerforhold_items.get('Reelle ejere',''):
                real_owner_name = ejere_soup.find('a').text.strip()
                real_owner_address = ejere_soup.find_all('div')[2].text.strip()
                real_owner_designation  = "real_owner"
                real_owner_dict = {
                    "name":real_owner_name,
                    "address":real_owner_address.replace("\n"," "),
                    "designation":real_owner_designation,
                    "meta_detail":{
                        "change_date":ejere_soup.find_all('div')[3].text.strip().split(':')[-1].strip()
                    }
                }
                people_details.append(real_owner_dict)
        except:
            real_owner_dict = {}
            people_details.append(real_owner_dict)


        # Get all filling_detail
        filling_detail = []
        try:
            filing_type = "Årsrapport"
            main_div = driver.find_element(By.ID, "accordion-regnskaber-content")
            elements = main_div.find_elements(By.CLASS_NAME, "accordion-content-inner")
            for element in elements:
                items = {}
                containers = element.find_elements(By.CLASS_NAME, "row")
                for container in containers:
                    label_rows = container.find_elements(By.CLASS_NAME, "col-12.col-lg-3")
                    for label_row in label_rows:
                        if len(label_row.find_elements(By.XPATH, "following-sibling::div")) > 0:
                            value_div = label_row.find_element(By.XPATH, "following-sibling::div")
                            key = re.search(r'>(.*?)<', label_row.get_attribute("innerHTML")).group(1)
                            items[key] = str(value_div.get_attribute("innerHTML"))
                try:
                    soup = BeautifulSoup(items['Årsrapport'], 'html.parser')
                    file_url = soup.find('a').get('href')
                except:
                    file_url = ""
                filing_dict = {
                        "date":items.get('Offentliggørelsesdato',"").replace(".","-"),
                        "filing_type":filing_type,
                        "file_url":file_url,
                        "meta_detail":{
                            "chairman":items.get('Dirigent',""),
                            "reporting_period":items.get('Godkendelsesdato','').replace(".","-"),
                            "approval_date":items.get('Godkendelsesdato','').replace(".","-")
                        }
                    }
                filling_detail.append(filing_dict)
        except:
            filling_detail = []
        # Get all additional_detail
        additiona_detail =  []
        try:
            p_unit = driver.find_element(By.ID,'accordion-produktionsenheder-content')
            p_unit_elements = p_unit.find_elements(By.CLASS_NAME, "accordion-content-inner")
            production_unit = {}
            for p_unit_element in p_unit_elements:
                p_unit_containers = p_unit_element.find_elements(By.CLASS_NAME, "row")
                for p_unit_container in p_unit_containers:
                    label_rows = p_unit_container.find_elements(By.CLASS_NAME, "col-6.col-lg-3")
                    for label_row in label_rows:
                        if len(label_row.find_elements(By.XPATH, "following-sibling::div")) > 0:
                            value_div = label_row.find_element(By.XPATH, "following-sibling::div")
                            key = re.search(r'>(.*?)<', label_row.get_attribute("innerHTML")).group(1)
                            production_unit[key] = str(value_div.get_attribute("innerHTML"))
            
            production_unit_dict = {
                "type": "production_unit_information",
                "data": [
                    {
                        "name": production_unit.get('Navn',''),
                        "address": f"{get_text(production_unit.get('Adresse',''))} {get_text(production_unit.get('Postnummer og by',''))}",
                        "unit_number": get_text(production_unit.get('P-nummer','')),
                        "start_date": production_unit.get('Startdato','').replace(".", "-"),
                        "industries": production_unit.get('Branchekode',''),
                        "email": production_unit.get('Email','')
                    }
                ]
            }
            additiona_detail.append(production_unit_dict)
        except:
            additiona_detail = []
        # Get all previous_names_detail
        previous_names_detail = []
        time.sleep(2)
        try:
            registing_hist= driver.find_element(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer"]/div[1]')
            
            registing_hist.click()
            time.sleep(3)

            for details in driver.find_elements(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer-content"]/div/div'):
                update_date = details.find_element(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer-content"]/div/div[1]/div/div[1]/div/span[1]').text.strip()
                cvr_number = details.find_element(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer-content"]/div/div[1]/div/div[2]/div/span').text.strip()
                cvr_number = cvr_number.split(":")[-1]
                address = details.find_element(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer-content"]/div/div[1]/div/div[3]/div/span[3]').text.strip()
                name_ = details.find_element(By.XPATH,'//*[@id="accordion-virksomhedRegistreringer-content"]/div/div[1]/div/div[3]/div/span[2]').text.strip()
                previous_dict = {
                    "update_date":update_date.replace(".","-"),
                    "name":name_,
                    "meta_detail":{
                        "cvr_number":cvr_number,
                        "address":address
                    }
                }
                previous_names_detail.append(previous_dict)
        except:
            previous_names_detail = []

        try:
            antal_ansatte = driver.find_element(By.ID,'accordion-antal-ansatte-content')
            antal_elements = antal_ansatte.find_element(By.CLASS_NAME, "accordion-content-inner")
            table = antal_elements.find_element(By.CLASS_NAME,'table')
            data_ = []
            for table_row in table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip the header row 
                table_soup = BeautifulSoup(table_row.get_attribute('innerHTML'),'html.parser')
                cols = table_soup.find_all("td")
                periode = cols[0].text.strip()
                ansatte = cols[1].text.strip()
                arsvaerk = cols[2].text.strip()
                
                aw = {
                    "period":periode,
                    "number_of_employees":ansatte,
                    "full_time_equivalent":arsvaerk
                }
                
                data_.append(aw)

            number_of_em_dict = {
                    "type":"employee_information",
                    "data":data_
                }
            additiona_detail.append(number_of_em_dict)
        except :
            number_of_em_dict = {}
            if number_of_em_dict != {}:
                additiona_detail.append(number_of_em_dict)
        try:
            latest_articles_of_association = ""
            accounting_period  =""
        except:
            latest_articles_of_association = ""
            accounting_period  =""
        
        OBJ = {
            "name":Name,
            "registration_number":db_items.get('CVR-nummer',''),
            "addresses_detail":[
                {
                    "type":'general_address',
                    "address":get_text(db_items.get('Adresse',''))+''+db_items.get('Postnummer og by','')+''+company_items.get('Kommune',"")
                }
            ],
            "registration_date":db_items.get('Startdato','').replace(".","-"),
            "type":db_items.get('Virksomhedsform',''),
            "advertising_protection":db_items.get('Reklamebeskyttelse',''),
            "status":db_items.get('Status',''),
            "contacts_detail":[
                {
                    "type":"phone_number",
                    "value":company_items.get('Telefon','')
                },
                {
                    "type":"email",
                    "value":company_items.get('Mail','')
                },
                {
                    "type":"fax_number",
                    "value":company_items.get('Fax','')
                }
            ],
            "industries":company_items.get('Branchekode',''),
            "description":company_items.get('Formål',''),
            "aliases":get_text(company_items.get('Binavne','')),
            "financial_year":company_items.get('Regnskabsår','').replace(".","-"),
            "latest_statute_date":company_items.get('Seneste vedtægtsdato','').replace(".","-"),
            "latest_articles_of_association":latest_articles_of_association,
            "capital_classes":get_text(company_items.get('Kapitalklasser','')),
            "registered_capital":get_text(company_items.get('Registreret kapital','')),
            "accounting_period":accounting_period,
            "drawing_rule":peoples_items.get('Tegningsregel',''),
            "people_detail":people_details,
            "additional_detail":additiona_detail,
            "fillings_detail":filling_detail,
            "previous_names_detail":previous_names_detail
        }


        OBJ = denmark_crawler.prepare_data_object(OBJ)
        ENTITY_ID = denmark_crawler.generate_entity_id(OBJ['registration_number'],OBJ['name'])
        BIRTH_INCORPORATION_DATE = ''
        ROW = denmark_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
        denmark_crawler.insert_record(ROW)

    denmark_crawler.end_crawler()
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}

    denmark_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": 'fail',
                "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    denmark_crawler.db_log(log_data)
