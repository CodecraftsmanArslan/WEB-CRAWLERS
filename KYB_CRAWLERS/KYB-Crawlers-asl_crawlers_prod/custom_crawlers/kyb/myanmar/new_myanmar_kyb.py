"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

meta_data = {
    'SOURCE' :'Directorate of Investment andassociation_category_span.text Company Administration (DICA) in Myanmar',
    'COUNTRY' : 'Myanmar',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.myco.dica.gov.mm/", 
                        "Source Description": "Official website of the Directorate of Investment and Company Administration (DICA) in Myanmar. The website serves as a valuable resource for investors and businesses looking to understand the regulatory landscape in Myanmar and take advantage of investment opportunities in the country. It includes information on the laws and procedures related to investment and company registration in Myanmar, as well as resources and tools to help businesses navigate these processes."},
    'URL' : 'https://www.myco.dica.gov.mm/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Myanmar Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

myanmar_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  myanmar_crawler.get_requests_helper()
selenium_helper =  myanmar_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False)

def get_records(page_number, page_size=10):
    max_retries = 10
    retry_count = 0
    print("\nPage_number =",page_number)
    while retry_count < max_retries:
        try:
            url = f"https://www.myco.dica.gov.mm/Api/Corp/SearchCorp?Term=__o&ExcludePending=true&ExcludeNotReReg=false&UseGenericSearch=false&PaginationPageSize={page_size}&PaginationCurrentPage={page_number}&OrderAscending=true&OrderBy=Name"
            response = request_helper.make_request(url)
            if response.status_code == 200:
                return response.json()
        except:
            print("Error occurred")
            retry_count += 1
            time.sleep(60)
            if retry_count < max_retries:
                print("Retrying...")
            else:
                print("Maximum retry attempts reached")

try:
    arguments = sys.argv
    start_page_no = int(arguments[1]) if len(arguments)>1 else 14600
    # page_number = 1
    for page_number in range(start_page_no, 15500):
        record = get_records(page_number)
        if len(record['records']) == 0:
            continue
        for data in record['records']:

            try:
                driver.get(f"https://www.myco.dica.gov.mm/Corp/EntityProfile.aspx?id={data.get('CorpId')}")
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                annual_return_date_span = soup.find('span', {'id': 'txtAnnualReturnDueDate'})
                annual_return_date = annual_return_date_span.text if annual_return_date_span is not None else ''
                foreign_span = soup.find('label', string='Foreign Company')
                try:
                    foreign_company = foreign_span.find_next_sibling('span').text if foreign_span is not None and foreign_span.find_next_sibling('span') is not None else ''
                except:
                    foreign_company = ""
                small_company_span = soup.find('label', string='Small Company')
                try:
                    small_company = small_company_span.find_next_sibling('span').text if small_company_span.find_next_sibling('span') is not None else ''
                    small_company = small_company if small_company is not None and small_company.replace('-', '') != '' else ''
                except:
                    small_company = ''
                association_category_span = soup.find('span', {'id': 'txtCategoryOfAssociation'})
                association_category = association_category_span.text if association_category_span is not None else ''
            except TimeoutException:
                print("Timeout error: The page or element did not load within the specified time.")

            business_activities = data.get('BusinessActivities')
            principal_activity = ', '.join(business_activities)
            additional_detail = []
            previous_names_detail = []
            previous_names_detail.append({
                "name": data.get('NameMatch').replace('%', '%%') if data.get('NameMatch') is not None else ''
            })
            if principal_activity !="":
                additional_detail.append({
                    'type': 'industries_information',
                    'activity': principal_activity
                })

            NAME = data.get('Name').replace('%', '%%') if data.get('Name') is not None else ''
            item = {
                "name": NAME,
                "aliases": data.get('AltName'),
                "registration_number": data.get('RegistrationNumberFormatted'),
                "registration_date": data.get('RegistrationDateFormatted').replace('/', '-') if data.get('RegistrationDateFormatted') is not None else "",
                "type": data.get('Type'),
                "status": data.get('Status'),
                "additional_detail": additional_detail,
                "previous_names_detail": previous_names_detail,
                'foreign_company': foreign_company,
                'small_company': small_company,
                'association_category': association_category,
                'annual_return_date': annual_return_date.replace('/', '-') if annual_return_date is not None else ""
            }
            
            ENTITY_ID = myanmar_crawler.generate_entity_id(company_name=NAME, reg_number=item.get('registration_number'))
            BIRTH_INCORPORATION_DATE = ''
            DATA = myanmar_crawler.prepare_data_object(item)
            ROW = myanmar_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            myanmar_crawler.insert_record(ROW)
        page_number += 1

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    myanmar_crawler.db_log(log_data)
    myanmar_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    myanmar_crawler.db_log(log_data)
