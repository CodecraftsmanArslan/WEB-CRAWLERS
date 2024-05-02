"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
from langdetect import detect
from selenium import webdriver
from dotenv import load_dotenv
from helpers.logger import Logger
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from helpers.crawlers_helper_func import CrawlersFunctions

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
'''DRIVER CONFIGURATION'''
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)



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
    data_for_db.append(shortuuid.uuid(record['name']+url_+'crawlers.custom_crawlers.kyb.bahrain.stock_market')) # entity_id
    data_for_db.append(record['name'].replace("'", "''")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(record)) # data
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME, driver  
        SOURCE_URL = url
        driver.get(SOURCE_URL)
        response = requests.get(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(driver.page_source)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        time.sleep(5)
        # Find the table element
        table = driver.find_element(By.ID,'bhbTable')

        # Find all the rows in the table
        rows = table.find_elements(By.XPATH,'.//tr')

        # Loop through each row and extract the data
        for row in rows[1:]:

           
            data = dict()
            # Find all the cells in the row
            cells = row.find_elements(By.XPATH,'.//td')

            if len(cells) > 10:
                reference_url = cells[1].find_element(By.TAG_NAME,'a').get_attribute('href')
                
                # Navigate to the sub-link URL
                driver.execute_script("window.open()")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(reference_url)

                time.sleep(5)

                data['name'] = driver.find_element(By.XPATH, '//*[@id="CompanyTitle1"]').get_attribute('textContent').strip().replace("'", "''")
                data['status'] = ''
                data['registration_number'] = ''
                data['dissolution_date'] = ''
                data['type'] = ''
                data['crawler_name'] = 'crawlers.custom_crawlers.kyb.bahrain.stock_market'
                data['country_name'] = country
                data['company_fetched_data_status'] = ''

                meta_details = dict()
               
                meta_details['email_address'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[10]/td[2]/a').get_attribute('text').strip().replace("'", "''")
                meta_details['internet_address'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[11]/td[2]/a').get_attribute('text').strip().replace("'", "''")
                meta_details['capital'] = driver.find_element(By.XPATH, '//*[@id="TabularMarketCaptial"]/ul/li[1]/div/h6[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['issued_fully_paid_shares'] = driver.find_element(By.XPATH, '//*[@id="TabularMarketCaptial"]/ul/li[2]/div/h6[2]').get_attribute('textContent').strip().replace("'", "''")

                meta_details['type_of_business'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/p[1]').get_attribute('textContent').strip().replace("'", "''")

                meta_details['shareholders'] = driver.find_element(By.XPATH, '//*[@id="hlKeyperson"]').get_attribute('href')

                meta_details['reuters_code'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[1]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['share_register'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[2]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['number_of_local_employees'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[3]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['number_of_non_local_employees'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[4]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['number_of_local_offices'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[5]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['number_of_foreign_offices'] = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[6]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['po_box_number']  = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[7]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['phone_number']  = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[8]/td[2]').get_attribute('textContent').strip().replace("'", "''")
                meta_details['fax_number']  = driver.find_element(By.XPATH, '//*[@id="overview"]/div/div[7]/table/tbody/tr[9]/td[2]').get_attribute('textContent').strip().replace("'", "''")

                data['meta_detail'] = meta_details

                address = driver.find_element(By.XPATH, '//*[@id="overview"]/div/p[2]').get_attribute('textContent')
                address_obj = dict()
                address_obj['type'] = 'address'
                address_obj['address'] = address.strip().replace("'", "''")

                data['addresses_detail'] = [address_obj]

                employee_table = driver.find_element(By.ID, 'BondsListing')
                employee_table_rows = employee_table.find_elements(By.XPATH,'.//tr')

                people_list = list()

                if len(employee_table_rows) > 0:

                    for employee in employee_table_rows:

                        cells = employee.find_elements(By.XPATH,'.//td')
                        if len(cells) > 2:
                            people = dict()
                            people['name'] = cells[0].get_attribute('textContent').strip().replace("'", "''")
                            people['type'] = cells[1].get_attribute('textContent').strip().replace("'", "''") if cells[2].get_attribute('textContent') else ''
                            people['designation'] = cells[2].get_attribute('textContent').strip().replace("'", "''") if cells[2].get_attribute('textContent') else cells[1].get_attribute('textContent').strip().replace("'", "''")

                            people_list.append(people)
                
                data['people_detail'] = people_list

                statement_elements = driver.find_elements(By.CLASS_NAME,'_fininner')
                fillings_detail = list()
                if len(statement_elements) > 0:
                    for statement_link in statement_elements:                        
                        statement = dict()
                        statement['description'] = statement_link.get_attribute('textContent').strip().replace("'", "''")
                        statement['file_url'] = statement_link.find_element(By.CLASS_NAME, '_finfile').get_attribute('href')

                        fillings_detail.append(statement)
                    
                data['fillings_detail'] = fillings_detail

                corporate_actions = driver.find_elements(By.CLASS_NAME, 'ann-block')  

                additional_detail = list()
                if len(corporate_actions) > 0:
                    additional_detail_obj = dict()
                    additional_detail_obj['type'] = 'corporate_actions'
                    action_data = list()
                    for actions_link in corporate_actions:
                        action = dict()
                        action['description'] = actions_link.find_element(By.CLASS_NAME, 'ann-link2').get_attribute('textContent').strip().replace("'", "''")
                        action['source_url'] = actions_link.find_element(By.CLASS_NAME, 'ann-link2').get_attribute('href')
                        action_data.append(action)
                    
                    additional_detail_obj['data'] = action_data
                    additional_detail.append(additional_detail_obj)


                data['additional_detail'] = additional_detail          
                driver.close()
                # Navigate back to the main page
                driver.switch_to.window(driver.window_handles[0])

                record_for_db = prepare_data(data, category,
                                            country, entity_type, source_type, name, url, description)
                        
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
                print("stored records")
                crawlers_functions.db_connection(query)
        
            
        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        print(e,tb)
        tb = traceback.format_exc()
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Bahrain stock market
    '''
    name = 'Bahrain Bourse'
    description = "Bahrain Bourse Company B S C C is a self-regulated multi-asset marketplace. Bahrain Bourse aims to offer to its investors, issuers, and intermediaries a comprehensive suite of exchange-related facilities including offering listing, trading, settlement, and depositary services for various financial instruments."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Bahrain'
    category = 'Stock Market'
    url = 'https://bahrainbourse.com/en/Quotes%20and%20Market/Stocks/Pages/Quotes.aspx'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
