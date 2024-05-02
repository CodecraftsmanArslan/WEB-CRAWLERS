"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
from bs4 import BeautifulSoup
import pandas as pd
import requests, json, os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
service = Service(ChromeDriverManager('114.0.5735.90').install())
driver = webdriver.Chrome(service=service, options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

arguments = sys.argv
page_number = arguments[1] if len(arguments)>1 else 1

def make_request(url, headers, timeout):
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except:
            time.sleep(10*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')
    
    print(f'Failed to make request after {max_retries} retries.')
    return None

def make_post_request(url, headers, payload, timeout):
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=timeout, verify=False)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except:
            time.sleep(10*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')
    
    print(f'Failed to make request after {max_retries} retries.')
    return None

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''
    meta_detail = dict()
    meta_detail['capital'] = record[4]
    meta_detail['fiscal_year'] = record[6]
    meta_detail['tax_description'] = record[8]
    meta_detail['visualize'] = record[12]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "registration_number":record[1],
        "registration_date":record[5],
        "status":record[3],
        "type":record[2],
        "incorporation_date":"",
        "jurisdiction":"",
        "jurisdiction_code": "",
        "industries": "",
        "tax_number":"",
        "dissolution_date": "",
        "inactive_date": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.estonia.estonia_kyb",
        "country_name": "Estonia",
        "meta_detail": meta_detail,
        "people_detail":record[7],
        "additional_detail":record[9],
        "announcements_detail":record[10],
        "fillings_detail":record[11]
    }
    
    return data_obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f'{record[1]}-{url_}-estonia_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')
    return data_for_db


def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url

        BASE_URL = "https://ariregister.rik.ee/{}"
        SEARCH_URL = 'https://ariregister.rik.ee/eng/company_search'
        API_URL = "https://ariregister.rik.ee/eng/company_search_result/{}?page={}"
        Registry_URL = "https://ariregister.rik.ee/eng/company/{}/tab/register?search_id=dcf79b8&product_id=2&parent_nonce=3163616231376539%7Cf9e2102cec2acc090fd8468a2f820e7b&_=1685701780629"
        Beneficiary_URL = "https://ariregister.rik.ee/eng/company/{}/tab/register?search_id=dcf79b8&product_id=19&parent_nonce=3336386538313265%7C2bb70c290ded9a578f1aeefb28df700b&_=1685712984620"
        Documents_URL = "https://ariregister.rik.ee/eng/company/{}/tab/proceeding_info?parent_nonce=3463653664343931%7Ced4802e36bfc2213577c4924044c1a0d&search_id=dcf79b8&_=1685945363262"
        Reports_URL = "https://ariregister.rik.ee/eng/company/{}/tab/fiscal_year_reports?parent_nonce=3361333961643066%7Cf7565d9743ea39137ffb48e133d7a679&search_id=dcf79b8&pos=2&_=1685946105279"

        headers = {
            'Authority': 'ariregister.rik.ee',
            'Method': 'GET',
            'Path': '/eng/company_search_result/dcf79b8',
            'Scheme': 'https',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://ariregister.rik.ee/eng/company_search_result/dcf79b8?name_or_code=',
            'Cookie': 'pk_id.1.851e=da1d7173ca8824c0.1686637028.; cookies_accepted=true; _cfuvid=N4vVBGzq2w0CsVWAqE0l6BRX_.UC3lx82w42QK.SLX8-1686638919986-0-604800000; __Host-ariregweb=eKpIiNcqCGXNR7mmzqmSK7HCa1iCGcdCEi4qqhaRES4ir8iLzespGqRNzdnNHQpf; _pk_ses.1.851e=1; __cf_bm=G2ZVaaSCkiFYv6CnrK7R_KHNCnOtEDCUgiTm9X_oIt4-1686658416-0-AUp81Ag62bJo2ywcXTc9FI4mwicwPNbtQxAt9wzoev6oRdPc8FOv6D4D1qhuzet9Yt5IwiPROVnX0/vo+UdE3hkUSSNtiFgyDp0oCZK9KiUX',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        print("Starting Page Number: ", page_number, "\n")
        page_no = int(page_number)
        wait = WebDriverWait(driver, 20)
        driver.get(SEARCH_URL)
        search_input = wait.until(EC.presence_of_element_located((By.ID, 's__company_name')))
        search_input.send_keys('*')
        search_input.submit()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_changes(driver.current_url))
        session_id = driver.current_url.split('/')[-1].split('?')[0]
        driver.get(API_URL.format(session_id,page_no))
        DATA = []
        while True:
            print("Page Number: ", page_no)

            # response = requests.get(API_URL.format(page_no), headers=headers, timeout=600)
            response = make_request(API_URL.format(session_id,page_no), headers, 600)

            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            soup = BeautifulSoup(response.content, 'html.parser')

            page_no+=1
            valid_page = soup.select_one("table > tbody > tr > td.max-width-50rem > div.text-truncate.max-width-50rem > a")
            if not valid_page:
                print('Not Valid!')
                time.sleep(20)

                response = make_request(API_URL.format(session_id,page_no), headers, 600)
                soup = BeautifulSoup(response.content, 'html.parser')
                valid_page = soup.select_one("table > tbody > tr > td.max-width-50rem > div.text-truncate.max-width-50rem > a")
                if not valid_page:
                    print("Invalid!")
                    break

            companies = soup.find("table").find_all('tr')
            for each in companies:
                if each.find('a') is not None:
                    link = each.find('a').get('href')
                    company_id = link.split("/")[3]

                    response = make_request(BASE_URL.format(link), headers, 500)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    people_details = []
                    additional_detail = []
                    announcements_detail = []
                    fillings_detail = []
                    contacts_detail = []

                    company_name = soup.select_one("div.h2.text-primary.mb-2.header-name-print").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if soup.select_one("div.h2.text-primary.mb-2.header-name-print") else ""
                    registration_number = soup.find("div", string="Registry code").find_next().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Registry code") else ""
                    company_type = soup.find("div", string="Legal form").find_next().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Legal form") else ""
                    company_status = soup.find("div", string="Status").find_next().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Status") else ""
                    capital = soup.find("div", string="Capital").find_next().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Capital") else ""
                    registered_date = soup.find("div", string="Registered").find_next().text.replace("\n","").replace(".","").replace("  ","")  if soup.find("div", string="Registered") else ""
                    fiscal_year = soup.find("div", string="Period of the financial year").find_next().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace(".","-")  if soup.find("div", string="Period of the financial year") else ""
                    visualize = BASE_URL.format(soup.select_one("div:nth-child(1) > div > div.mt-4.mb-2 > a:nth-child(3)").get("href").replace("\\","").replace("'","")) if soup.select_one("div:nth-child(1) > div > div.mt-4.mb-2 > a:nth-child(3)") else ""
                    
                    address = soup.find("div", string="Address").find_next_sibling().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Address") else ""
                    email = soup.find("div", string="E-mail address").find_next_sibling().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="E-mail address") else ""
                    ph_number = soup.find("div", string="Mobile phone").find_next_sibling().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Mobile phone") else ""
                    contacts_detail.append({"type" : "address", "value" : address, "meta_detail":{}})
                    contacts_detail.append({"type" : "email", "value" : email, "meta_detail":{}})
                    contacts_detail.append({"type" : "phone_number", "value" : ph_number, "meta_detail":{}})

                    cp_address = soup.find("div", string="Address of the contact person").find_next_sibling().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace("Open map","")  if soup.find("div", string="Address of the contact person") else ""
                    cp_email = soup.find("div", string="Contact person's email address").find_next_sibling().get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.find("div", string="Contact person's email address") else ""
                    if cp_address != "" and cp_email != "":
                        people_details.append({"name": "", "address": cp_address, "postal_address": "", "designation": "contact_person",      
                                                "appointment_date":"", "termination_date":"", "nationality": "", "email":cp_email, "phone_number":"",
                                                "fax_number":"", "social_link": [], "meta_detail":{}})
                    
                    tax_information = soup.select_one("div.emta_tax_debt_container").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")  if soup.select_one("div.emta_tax_debt_container") else ""

                    registry_response = make_request(Registry_URL.format(company_id), headers, 500)

                    try:
                        data = json.loads(registry_response.content)
                        registry_soup = BeautifulSoup(data['data']['html'], 'html.parser')
                    except:
                        egistry_soup = BeautifulSoup(registry_response.content, 'html.parser')

                #   Extracting People Details
                    details = registry_soup.find("div", id="product__personal_and_general")
                    if details:
                        tables = details.select("div > div > div.table-responsive")
                        for table_ in tables:
                            if "Persons entered on the registry card" in str(table_.find_parent()):
                                table_representative = table_.select('table tbody tr')
                                for row in table_representative:
                                    if len(row.select('td')) == 6:
                                        representative_name = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(2)") else ""
                                        date_of_birth = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(3)") else ""
                                        designation = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(1)") else ""
                                        residence = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(4)") else ""
                                        representative_email = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(5)") else ""
                                        people_details.append({"name": representative_name, "address": residence, "postal_address": "", "designation": designation,      
                                                            "appointment_date":"", "termination_date":"", "nationality": "", "email":representative_email, "phone_number":"",
                                                            "fax_number":"", "social_link": [], "meta_detail":{'identification_code/date_of_birth':date_of_birth}})
                            
                            elif 'Shareholders' in str(table_.find_parent()):
                                table_shareholder = table_.select('table tbody tr')
                                for row in table_shareholder:
                                    if len(row.select('td')) == 7:
                                        contribution = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")
                                        type_of_ownership = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")
                                        shareholder_name = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace("\\n","")
                                        id_code = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")
                                        location = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")
                                        source_shareholder = row.select_one("td:nth-child(6)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","")
                                        people_details.append({"name": shareholder_name, "address": location, "postal_address": "", "designation": "Shareholders",      
                                                        "appointment_date":"", "termination_date":"", "nationality": "", "email":"", "phone_number":"",
                                                        "fax_number":"", "social_link": [], "meta_detail":{'type_of_ownership':type_of_ownership, 'contribution':contribution, 
                                                                                                        'identification_code/date_of_birth':id_code, 'source':source_shareholder}})
                            
                            elif 'Other persons outside the registry card' in str(table_.find_parent()):
                                table_shareholder_ = table_.select('table tbody tr')
                                for row in table_shareholder_:
                                    if len(row.select('td')) == 7:
                                        sh_designation = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(1)") else ""
                                        sh_name = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace("\\n","") if row.select_one("td:nth-child(2)") else ""
                                        sh_id_code = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(3)") else ""
                                        sh_residence = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(4)") else ""
                                        sh_contribution = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(5)") else ""
                                        sh_source = row.select_one("td:nth-child(6)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(6)") else ""
                                        people_details.append({"name": sh_name, "address": sh_residence, "postal_address": "", "designation": sh_designation,      
                                                        "appointment_date":"", "termination_date":"", "nationality": "", "email":"", "phone_number":"",
                                                        "fax_number":"", "social_link": [], "meta_detail":{'contribution':sh_contribution, 
                                                                                                        'identification_code/date_of_birth':sh_id_code, 'source':sh_source}})
                
                #   Extracting Industry Details and Articles of Association
                    industry_type = soup.select_one("div:nth-child(1) > div.col-8").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if soup.select_one("div:nth-child(1) > div.col-8") else ""
                    emtak_code = soup.select_one("div:nth-child(2) > div.col-8").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if soup.select_one("div:nth-child(2) > div.col-8") else ""
                    nace_code = soup.select_one("div:nth-child(3) > div.col-8").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if soup.select_one("div:nth-child(3) > div.col-8") else ""
                    industry_source = soup.select_one("div:nth-child(4) > div.col-8").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if soup.select_one("div:nth-child(4) > div.col-8") else ""
                    industry_detials = {'industry_type':industry_type, "EMTAC_code":emtak_code, "NACE_code":nace_code, 'source':industry_source}

                    if any(value != "" for value in industry_detials.values()):
                        additional_detail.append({"type":"industry_details", "data":[industry_detials]})
                    
                    tr_tags = soup.select('tr', {'id':'#statute_row__9010010866'})
                    for trs in tr_tags:
                        if 'articles of association' in str(trs).lower():
                            effective_date = trs.find_next_sibling().find_all('td')[0].text.replace(".","-").replace("'","") if trs.find_next_sibling() else ""
                            valid_until = trs.find_next_sibling().find_all('td')[1].text.replace("'","") if trs.find_next_sibling() else ""
                            approval_date = trs.find_next_sibling().find_all('td')[2].text.replace(".","-").replace("'","") if trs.find_next_sibling() else ""
                            association_status = trs.find_next_sibling().find_all('td')[3].text.replace("'","") if trs.find_next_sibling() else ""
                            articles_of_association = {"effective_date":effective_date, "valid_until":valid_until, "approval_date":approval_date, "association_status":association_status}
                            additional_detail.append({"type":"articles_of_association", "data":[articles_of_association]})

                #   Extracting Beeficiary Details
                    beneficiary_details = []
                    beneficiary_response = make_request(Beneficiary_URL.format(company_id), headers, 500)
 
                    beneficiary_soup = BeautifulSoup(beneficiary_response.content, 'html.parser')
                    beneficiary_data = beneficiary_soup.select_one("div", {"id":"product__beneficiaries"})
                    beneficiary_table = beneficiary_data.select("div > div > div > div > table > tbody > tr ")

                    for row in beneficiary_table:
                        if len(row.find_all('td')) >= 3:
                            beneficiary_name = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","") if row.select_one("td:nth-child(2)") else ""
                            beneficiary_id_code = row.select_one("td:nth-child(1)").text.replace("  ","").replace(".","-").replace("\\n","").replace("'","") if row.select_one("td:nth-child(1)") else ""
                            beneficiary_residence = row.select_one("td:nth-child(3)").text.replace("  ","").replace(".","-").replace("'","") if row.select_one("td:nth-child(3)") else ""
                            beneficiary_details.append({"name":beneficiary_name, "identification_code/date_of_birth":beneficiary_id_code,
                                                        "residence":beneficiary_residence})
                    
                    if beneficiary_details:
                        additional_detail.append({"type":"beneficial_owners", "data":beneficiary_details})

                #   Extracting Report Details
                    document_response = make_request(Documents_URL.format(company_id), headers, 500)

                    document_soup = BeautifulSoup(document_response.content, 'html.parser')
                    document_data = document_soup.select_one("div", {"id":"tab_content__proceeding_info"})
                    document_table = document_data.select("div > div:nth-child(3) > table > tbody > tr")

                    for row in document_table:
                        if len(row.find_all('td')) >= 5:
                            document_type = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(1)") else ""
                            document_date = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('.', '-') if row.select_one("td:nth-child(2)") else ""
                            document_status = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(3)") else ""
                            document_not_number = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(4)") else ""
                            document_foundation = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(5)") else ""
                            announcements_detail.append({"date":document_date, "title":"document_submission", "description":"", "meta_detail":{'type':document_type, 
                                                                                        'status':document_status, 'notorial_number':document_not_number,
                                                                                        'foundation_number':document_foundation}})

                    ruling_data = document_soup.select_one("div", {"id":"tab_content__proceeding_info"})
                    ruling_table = ruling_data.select("div > div:nth-child(5) > table > tbody > tr")
                    for row in ruling_table:
                        if len(row.find_all('td'))>= 5:
                            ruling_number = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(1)") else ""
                            ruling_type = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(2)") else ""
                            ruling_date = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('.', '-') if row.select_one("td:nth-child(3)") else ""
                            ruling_status = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(4)") else ""
                            ruling_deadline = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace("'","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(5)") else ""
                            announcements_detail.append({"date":ruling_date, "title":"ruling_details", "description":"", "meta_detail":{'type':ruling_type, 
                                                                                        'status':ruling_status, 'ruling_number':ruling_number,
                                                                                        'ruling_deadline':ruling_deadline}})

                    entries_data = document_soup.select_one("div", {"id":"tab_content__proceeding_info"})
                    entries_table = entries_data.select("div > div:nth-child(9) > table > tbody > tr")
                    for row in entries_table:
                        if len(row.find_all('td')) == 5:
                            entry_number = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(1)") else ""
                            entry_type = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(2)") else ""
                            entry_date = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('.', '-').replace("'","") if row.select_one("td:nth-child(3)") else ""
                            ruling_number_entry = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(4)") else ""
                            type_of_ruling = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(5)") else ""
                            announcements_detail.append({"date":entry_date, "title":"entry_details", "description":"", "meta_detail":{'type':entry_type, 
                                                                                        'ruling_number':ruling_number_entry, 'entry_number':entry_number,
                                                                                        'type_of_ruling':type_of_ruling}})
                    
                #   Extracting Report Details
                    reports_details = []
                    reports_response = make_request(Reports_URL.format(company_id), headers, 500)
 
                    reports_soup = BeautifulSoup(reports_response.content, 'html.parser')
                    reports_data = reports_soup.select_one("div", {"id":"tab_content__fiscal_year_reports"})
                    
                    reports_table = reports_data.select("div > table > tbody > tr")
                    
                    for row in reports_table:
                        if len(row.find_all('td')) == 7:
                            if "annual report" in str(row).lower():
                                report_year = row.select_one("td:nth-child(1)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","") if row.select_one("td:nth-child(1)") else ""
                                time_period = row.select_one("td:nth-child(2)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('.', '-').replace("'","") if row.select_one("td:nth-child(2)") else ""
                                date_of_submission = row.select_one("td:nth-child(3)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('.', '-').replace("'","") if row.select_one("td:nth-child(3)") else ""
                                report_status = row.select_one("td:nth-child(4)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","").replace("'","") if row.select_one("td:nth-child(4)") else ""
                                report_type = row.select_one("td:nth-child(5)").get_text().strip().encode().decode('unicode_escape').strip().replace("\n","").replace('\\', '').replace("'","").replace("'","") if row.select_one("td:nth-child(5)") else ""
                                report_url = row.select_one("td:nth-child(7) button").get('data-target_url').replace('\\', '').replace("'","") if row.select_one("td:nth-child(7) button") else ""
                                reports_details.append({"year":report_year, "time_period":time_period, "date_of_submission":date_of_submission, "status":report_status,
                                                       "type":report_type, "document_url":BASE_URL.format(report_url)})
                            if "balance" in str(row).lower():
                                balance_url =  row.select_one("td:nth-child(7) button").get('data-target_url').replace('\\', '').replace("'","").replace("\n","").replace('\"','') if row.select_one("td:nth-child(7)") else ""
                                fillings_detail.append({"date": "", "description": "", "filing_code": "", "filing_type": "balance_statement", "file_url": BASE_URL.format(balance_url),
                                                        "title": "", "meta_detail": {}})
                            if "income statement" in str(row).lower():
                                income_statement_url =  row.select_one("td:nth-child(7) button").get("data-target_url").replace('\\', '').replace("'","") if row.select_one("td:nth-child(7)") else ""
                                fillings_detail.append({"date": "", "description": "", "filing_code": "", "filing_type": "income_statement_format_1", "file_url": BASE_URL.format(income_statement_url),
                                                        "title": "", "meta_detail": {}})
                    
                    if reports_details:
                        additional_detail.append({"type":"reports_detail", "data":reports_details})
                    
                    record = [company_name, registration_number, company_type, company_status, capital, registered_date, fiscal_year,
                              people_details, tax_information, additional_detail, announcements_detail, fillings_detail, visualize]
        
                    DATA.append(record)
                    record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                                
                    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                    
                    if record_for_db[1] != "":
                        print("Stored record.")
                        crawlers_functions.db_connection(query)
        driver.close()
        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")



if __name__ == '__main__':
    '''
    Description: HTML Crawler for Estonia
    '''
    countries = "Estonia"
    entity_type = "Company/Organization"
    category = "Official Registry"
    name = "Estonian Business Register"
    description = "This is the Estonian Business Register, which is run by the Center of Registers and Information Systems. The Estonian Business Register is responsible for the registration of companies and businesses in Estonia, and maintains a database of registered companies."
    source_type = "HTML"
    url = "https://ariregister.rik.ee/eng/company_search" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url, name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()