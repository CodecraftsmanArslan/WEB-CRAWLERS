"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from lxml import etree
import re
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException

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


def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @param countries
    @param category_
    @param entity_type
    @return dict
    '''

    meta_detail = dict()
    meta_detail['type_of_business'] = record[1].replace("'","''")
    meta_detail['isin_code'] = record[2].replace("'","''")
    meta_detail['auditors'] = record[3].replace("'","''")
    meta_detail['address'] = record[4].replace("'","''")
    meta_detail['phone_number'] = record[5].replace("'","''")
    meta_detail['mobile_number'] = record[6].replace("'","''")
    meta_detail['email_address'] = record[7].replace("'","''")
    meta_detail['internet_address'] = record[8].replace("'","''")
    meta_detail['establishing_date'] = record[9].replace("'","''")
    meta_detail['initial_capital'] = record[10].replace("'","''")
    meta_detail['listing_date'] = record[11].replace("'","''")
    meta_detail['issued_capital'] = record[12].replace("'","''")
    meta_detail['oustanding_shares'] = record[13].replace("'","''")
    meta_detail['peoples_detail'] = record[14]
    meta_detail['announcements'] = record[15]
    meta_detail['news'] = record[16]
    meta_detail['financials'] = record[17]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.iraq.stock_market",
        "country_name": "Iraq",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{url_}{record[2]}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record))) # data
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
        # Set up the Selenium WebDriver (assuming you have the appropriate driver executable in your system PATH)
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # Load the webpage
        driver.get(url)
        # Accept the alert by clicking "OK"
        try:
            # Switch to the alert
            alert = driver.switch_to.alert
            # Accept the alert by clicking "OK"
            alert.accept()
        except NoAlertPresentException:
            pass


        # Find the table by ID
        name_ = driver.find_element(By.ID, 'subTitleDiv').text.strip()
        # Find the element by ID and click on it
        element = driver.find_element(By.ID, "TAB2")
        element.click()
        time.sleep(3)
        main_activity = driver.find_element(By.CLASS_NAME, 'profile-content').text.strip()
        # Find all elements with the class name "profile-content"
        elements = driver.find_elements(By.CLASS_NAME,"profile-content")
        # Get the second and third elements
        second_element = elements[1]
        third_element = elements[2]
        isin_code = second_element.find_elements(By.TAG_NAME, "div")[1].text.strip()
        auditors = third_element.find_elements(By.TAG_NAME, "div")[1].text.strip()
        
        profile_rows = driver.find_elements(By.CLASS_NAME, "profile-datarow")
        address = profile_rows[0].find_elements(By.TAG_NAME, "div")[1].text.strip()
        phone = profile_rows[1].find_elements(By.TAG_NAME, "div")[1].text.strip()
        mobile = profile_rows[2].find_elements(By.TAG_NAME, "div")[1].text.strip()
        email = profile_rows[3].find_elements(By.TAG_NAME, "div")[1].text.strip()
        website = profile_rows[4].find_elements(By.TAG_NAME, "div")[1].text.strip()
        establishing_date = profile_rows[5].find_elements(By.TAG_NAME, "div")[1].text.strip()
        initial_capital = profile_rows[6].find_elements(By.TAG_NAME, "div")[1].text.strip()
        listing_date = profile_rows[7].find_elements(By.TAG_NAME, "div")[1].text.strip()
        issued_capital = profile_rows[8].find_elements(By.TAG_NAME, "div")[1].text.strip()
        oustanding_shares = profile_rows[9].find_elements(By.TAG_NAME, "div")[1].text.strip()
        par_value = profile_rows[10].find_elements(By.TAG_NAME, "div")[1].text.strip()

        board_member_rows = driver.find_elements(By.CLASS_NAME, "profile-datarow2")
        board_members = []
        for row in board_member_rows:
            board_member = {}
            board_member['designation'] = row.find_elements(By.TAG_NAME, "div")[0].text.strip()
            board_member['name'] = row.find_elements(By.TAG_NAME, "div")[1].text.strip()
            board_members.append(board_member)
        
        element = driver.find_element(By.ID, "TAB3")
        element.click()
        time.sleep(3)

        announcements_elements = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[4]/div/div[2]/div/table/tbody/tr/td/span/a')
        # Extract the href attributes
        announcements = []
        for element in announcements_elements:
            announcements.append(element.get_attribute("href"))

        element = driver.find_element(By.ID, "TAB4")
        element.click()
        time.sleep(3)

        news_elements = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[4]/div/div[2]/div/table/tbody/tr/td/span/a')
        # Extract the href attributes
        news = []
        for element in news_elements:
            news.append(element.get_attribute("href"))


        element = driver.find_element(By.ID, "TAB5")
        element.click()
        time.sleep(3)

        table = driver.find_element(By.CLASS_NAME, 'table-allcontent')
        tds = table.find_elements(By.TAG_NAME, 'td')

        # Extract the href attributes
        financials = []
        for td in tds:
            try:
                financial = td.find_element(By.TAG_NAME, 'a').get_attribute('href')
                financials.append(financial)
            except:
                pass
            
        # Close the browser
        driver.quit()

        DATA = []
        DATA.append([
            name_,
            main_activity,
            isin_code,
            auditors,
            address,
            phone,
            mobile,
            email,
            website,
            establishing_date,
            initial_capital,
            listing_date,
            issued_capital,
            oustanding_shares,
            board_members,
            announcements,
            news,
            financials
        ])

        for record_ in DATA:
            record_for_db = prepare_data(record_, category,
                                            country, entity_type, source_type, name, url, description)
                        
            
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: API Crawler for Iraq
    '''
    name = 'Iraq Stock Exchange (ISX)'
    description = "The Iraq Stock Exchange (ISX) is the primary stock exchange in Iraq, located in Baghdad. It was established in 2004. The ISX plays a crucial role in the development of Iraq's capital market and serves as a platform for companies to raise capital and for investors to trade securities."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Iraq'
    category = 'Stock Market'
    urls = pd.read_csv(".//kyb/iraq/input/stock_market.csv")
    for url in urls.iterrows():
        url = url[1][0]
        print(url)
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
