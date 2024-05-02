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
from deep_translator import GoogleTranslator
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from helpers.crawlers_helper_func import CrawlersFunctions
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
'''DRIVER CONFIGURATION'''
options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
service = Service(ChromeDriverManager(os.getenv('CHROME_VERSION')).install())
# driver = webdriver.Chrome(options=options)

driver = webdriver.Chrome(service=service, options=options)

def googleTranslator(record_):
    """Description: This method is used to translate any language to english. 
        It take name as input and return the translated name
    
    @param record_
    @return: translated_record
    """
    translated = GoogleTranslator(source='auto', target='en')
    translated_record = translated.translate(record_)
    return translated_record.replace("'","''")
 

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''
    # preparing additional_detail dictionary object
    additional_detail = []
    if record[3] !="":
        add_dict=  {
            "type":"reference_links",
            "data":[record[3]]
        }
    additional_detail.append(add_dict)
    
    
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['aliases'] = record[1]
    meta_detail['original_name'] = record[0].replace("'","''")   
    meta_detail['reference_url'] = record[2] 

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": googleTranslator(record[0].replace("'","''")),
        "crawler_name": "crawlers.custom_crawlers.kyb.macau.macau_crawler_kyb",
        "country_name": "Macau S.A.R",
        "additional_detail": additional_detail,
        "meta_detail": meta_detail
    }
    if data_obj['additional_detail'][0]['data'][0]=={}:
        del data_obj['additional_detail']
    
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
    data_for_db.append(shortuuid.uuid(f'{record[2]}{url_}-macau_crawler_kyb')) # entity_id
    data_for_db.append(googleTranslator(record[0].replace("'", ""))) #name
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME, driver  
        SOURCE_URL = url
        driver.get(SOURCE_URL)
        response = requests.get(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(driver.page_source)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Wait for the page to load
        time.sleep(3)
        # Find the table element
        table = driver.find_element(By.XPATH,'//*[@id="content"]/div/div[2]/table')

        # Find all the rows in the table
        rows = table.find_elements(By.XPATH,'.//tr')

        # Loop through each row and extract the data
        for row in rows:
            data = []
            # Find all the cells in the row
            cells = row.find_elements(By.XPATH,'.//td')
            extract_name = cells[0].find_element(By.XPATH,'.//div/h4').text.replace("'","''")
            try:
                aliese = cells[0].find_element(By.XPATH,'.//div/ul/li').text.replace("'","''")
            except:
                aliese = "" 
            
            data.append(extract_name)
            data.append(aliese)
            # Extract the href link from the last cell
            reference_url = cells[0].find_element(By.XPATH,'.//h4/a').get_attribute('href')
            data.append(reference_url)
            # Navigate to the sub-link URL
            driver.execute_script("window.open()")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(reference_url)
            # Scrape further URLs from the sub-link page
            sub_links = driver.find_elements(By.XPATH, '/html/body/div/div/div/div/ul/li/a')
            # Write the data and sub-links to the CSV files
            child_links = dict()
            for index, sub_link in enumerate(sub_links):
                sub_link_url = sub_link.get_attribute('href')
                child_links[f"link_{index+1}"] = sub_link_url

            data.append(child_links)
            # Navigate back to the main page
            driver.switch_to.window(driver.window_handles[0])
        
            record_for_db = prepare_data(data, category,country, entity_type, source_type, name, url, description)
            
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}', '{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            crawlers_functions.db_connection(query)
            print("Stored Records")
        
        
        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        driver.close()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Macau
    '''
    name = 'Government of the Macau Special Administrative Region, China'
    description = "Official directory of gambling companies operating in Macau, China. The website is provided by the government of the Macau Special Administrative Region and lists both local and foreign companies involved in the gambling industry in Macau. The directory includes information such as the company's name, address, and contact information, as well as the nature of their gambling activities. "
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Macau S.A.R'
    category = 'Official Registry'
    urls_list = ['https://www.io.gov.mo/pt/entities/priv/cat/public',
                'https://www.io.gov.mo/pt/entities/priv/cat/tertiary',
                'https://www.io.gov.mo/pt/entities/priv/cat/concessionaires',
                'https://www.io.gov.mo/pt/entities/priv/cat/insurance',
                'https://www.io.gov.mo/pt/entities/priv/cat/money',
                'https://www.io.gov.mo/pt/entities/priv/cat/banks',
                'https://www.io.gov.mo/pt/entities/priv/cat/accountants',
                'https://www.io.gov.mo/pt/entities/priv/cat/allassoc',
                'https://www.io.gov.mo/pt/entities/priv/cat/gambling']
   
    for url in urls_list:
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url, name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
