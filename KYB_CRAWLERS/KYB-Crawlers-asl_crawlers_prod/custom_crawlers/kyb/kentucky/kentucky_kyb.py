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
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
import re
from dateutil import parser
from selenium.common.exceptions import NoAlertPresentException
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

def create(record_, source_type, entity_type, country, category, url, name, description):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
        print(record_for_db[7])
        print("Stored record\n")
        crawlers_functions.db_connection(query)
    else:
        print("Something went wrong")


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
    entity_id_ = record['name'].replace("'", "")+record['organization_number']
    data_for_db.append(shortuuid.uuid(f"{entity_id_}{url_}-kentucky_kyb")) # entity_id
    data_for_db.append(record['name'].replace("'", "''")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'",""), "Name": name_}
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
    meta_detail = {}
    meta_detail['profit_or_non_profit'] = record['profit_or_non_profit']
    meta_detail['standing'] = record['standing']
    meta_detail['organization_date'] = format_date(record['organization_date'])
    meta_detail['last_annual_report'] = record['last_annual_report'].replace("/", "-")
    meta_detail['managed_by'] = record['managed_by']
    meta_detail['authority_date'] = record['authority_date']
    meta_detail['authorized_shares'] = record['authorized_shares']
    filtered_meta_detail = {key: value for key, value in meta_detail.items() if value}

    addresses_detail = []
    if record['principal_office']['address'] != "":
        addresses_detail.append(record['principal_office'])

    people_detail = []
    if 'registered_agent' in record:
        people_detail.extend(record['registered_agent'])

    people_detail.extend(record['current_officers'])
    if len(record['images_available']) > 0:
        fillings_detail = [*record['images_available']]
    elif len(record['activity_history']) > 0:
        fillings_detail = [*record['activity_history']]
    else:
        fillings_detail = []

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['name'].replace("'", "''") if 'name' in record else "",
        "registration_number": record['organization_number'],
        "registration_date": format_date(record['file_date']),
        "incorporation_date": "",
        "jurisdiction_code": record['state'],
        "meta_detail": filtered_meta_detail,
        "status": record['status'],
        "type": record['company_type'].replace("\n","") if 'company_type' in record else "",
        "crawler_name": "custom_crawlers.kyb.kentucky.kentucky_kyb",
        "addresses_detail": addresses_detail,
        "fillings_detail": fillings_detail,
        "people_detail": people_detail,
        "country_name": "Kentucky",
    }
    
    return data_obj

def remove_alert(driver):
    try:
        # Switch to the alert
        alert = driver.switch_to.alert

        # Get the text of the alert and print it
        alert_text = alert.text
        print("Alert Removed")

        # Accept (OK) the alert
        alert.accept()

    except NoAlertPresentException:
        # No alert found, handle the situation accordingly
        print("No alert found.")

def format_date(timestamp):
    try:
        # Parse the timestamp into a datetime object
        datetime_obj = parser.parse(timestamp)

        # Extract the date portion from the datetime object
        date_str = datetime_obj.strftime("%m-%d-%Y")

    except Exception as e:
        print("time format:", e)
        date_str = ""
    return date_str

def format_data(data):
    item = dict()
    item["organization_number"] = data['general_information']['Organization Number'] if "Organization Number" in data["general_information"] else ""
    item["name"] = data['general_information']['Name'] if "Name" in data["general_information"] else ""
    item["profit_or_non_profit"] = data['general_information']['Profit or Non-Profit'] if "Profit or Non-Profit" in data["general_information"] else ""
    item["company_type"] = data['general_information']['Company Type'] if "Company Type" in data["general_information"] else ""
    item["status"] = data['general_information']['Status'] if "Status" in data["general_information"] else ""
    item["standing"] = data['general_information']['Standing'] if "Standing" in data["general_information"] else ""
    item["state"] = data['general_information']['State'] if "State" in data["general_information"] else ""
    item["file_date"] = data['general_information']['File Date'] if "File Date" in data["general_information"] else ""
    item["organization_date"] = data['general_information']['Organization Date'] if "Organization Date" in data["general_information"] else ""
    item["last_annual_report"] = data['general_information']['Last Annual Report'] if "Last Annual Report" in data["general_information"] else ""
    item["principal_office"] = {
        "type": "office_address",        
        "address": data['general_information']['Principal Office'].replace("\n", " ").replace("'", "''") if "Principal Office" in data["general_information"] else ""
    }
    item["managed_by"] = data['general_information']['Managed By'] if "Managed By" in  data['general_information'] else ""
    item["authority_date"] = data['general_information']['Authority Date'] if 'Authority Date' in data['general_information'] else ""
    item['authorized_shares'] = data['general_information']['Authorized Shares'] if 'Authorized Shares' in data['general_information'] else ""

    if "Registered Agent" in data['general_information']:
        if '\n' in data['general_information']['Registered Agent']:
            agent_name, agent_address = data['general_information']['Registered Agent'].split('\n', 1)
            item["registered_agent"] = [{
                "name": agent_name.replace("'", ""),
                "address": agent_address.replace("\n", " "),
                "designation": "Registered Agent"
            }]

    item["current_officers"] = data['current_officers']
    item["images_available"] = data['images_available']
    item["activity_history"] = data['activity_history']

    return item

def activity_history(driver):
    try:
        table_data = []
        button = driver.find_element(By.ID, "MainContent_BtnActHist")
        button.click()
        time.sleep(3)
        remove_alert(driver)
        table_element = driver.find_element(By.ID, "MainContent_GVActivities")
        table_html = table_element.get_attribute("innerHTML")
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")

        for row in rows[1:]:
            item = {}
            columns = row.find_all("td")
            if len(columns) > 5:
                effective_date = columns[8].text.replace("/", "-").replace("\n","")
                item['title'] = columns[6].text.strip().replace("'", "''")
                item['date'] = columns[7].text.replace("/", "-").replace("\n","")
                if effective_date != "":
                    item['meta_detail'] = {
                        'effective_date': columns[8].text.replace("/", "-").replace("\n","")
                    }
                item['file_url'] = columns[9].a.get('href').replace("../", "https://web.sos.ky.gov/bussearchnprofile/") if columns[9].a.get('href') != None else ""
                table_data.append(item)
    except Exception as e:
        print("activity history table not found")
    return table_data


def images_available(driver):
    try:
        table_data = []
        button = driver.find_element(By.ID, "MainContent_BtnImages")
        button.click()
        time.sleep(3)
        remove_alert(driver)
        table_element = driver.find_element(By.ID, "MainContent_GvImages")
        table_html = table_element.get_attribute("innerHTML")
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")

        for row in rows[1:]:
            item = {}
            columns = row.find_all("td")
            if len(columns) > 5:
                item['title'] = columns[6].text.strip().replace("'", "''")
                item['file_url'] = columns[6].a.get('href') if columns[6].a.get('href').find('genpdf.aspx')==-1 else f"https://web.sos.ky.gov/bussearchnprofile/{columns[6].a.get('href').replace('../','')}"
                item['date'] = columns[7].text.strip().replace("/", "-")
                table_data.append(item)
    except Exception as e:
        print("images available table not found")

    return table_data


def current_officers(driver):
    try:
        table_data = []
        button = driver.find_element(By.ID, "MainContent_BtnCurrent")
        button.click()
        time.sleep(3)
        remove_alert(driver)
        # Find the table element
        # table_element = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[2]/div[2]/div/div/form/div[6]/table")
        table_element = driver.find_element(By.ID, "MainContent_GvOff")
        # Get the HTML source of the table
        table_html = table_element.get_attribute("innerHTML")

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(table_html, "html.parser")

        # Find the table rows
        rows = soup.find_all("tr")

        for row in rows:
            item = {}
            columns = row.find_all("td")
            if len(columns) > 4:
                item["designation"] = columns[4].text.strip().replace("'", "''")
                item["name"] = columns[5].text.strip().replace("'", "''")
                table_data.append(item)
    except Exception as e:
        print("current officers table not found")
    return table_data

def general_information(driver):
    # Find the table element
    table_elements = driver.find_elements(By.XPATH, "/html/body/div[1]/div[4]/div/div[2]/div[2]/div/div/form/div[3]/div[3]/table")

    if len(table_elements) == 0:
        return False
    
    # Get the HTML source of the table
    table_html = table_elements[0].get_attribute("innerHTML")

    # Replace <br> tags with newline characters
    table_html = re.sub(r"<br\s*/?>", "\n", table_html)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(table_html, "html.parser")

    # Find all rows in the table body
    rows = soup.find("tbody").find_all("tr")

    # Extract the table data
    table_data = []
    for row in rows:
        columns = row.find_all("td")
        row_data = [column.text.strip().replace("'", "''") for column in columns]
        table_data.append(row_data)


    data = [[value for value in sublist if value != ''] for sublist in table_data]
    result = {item[0]: item[1] for item in data if len(item) >= 2}

    return result


def get_page_data(driver, url):
    driver.get(url)
    remove_alert(driver)
    time.sleep(2)
    result = dict()
    general_info = general_information(driver)
    if general_info:
        result['general_information'] = general_info
        result['current_officers'] = current_officers(driver)
        result['images_available'] = images_available(driver)
        result['activity_history'] = activity_history(driver)
        return result
    else:
        return False


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
        service = Service(ChromeDriverManager('114.0.5735.90').install())
        driver = webdriver.Chrome(service=service, options=options)
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        # Check if a command-line argument is provided
        if len(sys.argv) > 1:
            start_number = int(sys.argv[1])
        else:
            # Assign a default value if no command-line argument is provided
            start_number = 1

        for i in range(start_number, 1300656):
            item = {}
            print(i)
            url_ = f"{url}{i}"
            item = get_page_data(driver, url_)

            if item:
                formated_data = format_data(item)
                DATA_SIZE += 1
                create(formated_data, source_type, entity_type, country, category, url_, name, description)            

        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","")
    

if __name__ == '__main__':
    '''
    Description: Crawler for Kentucky
    '''
    name = "Kentucky Secretary of State"
    description = "The Kentucky Secretary of State website serves as the official online platform for the Office of the Secretary of State in the state of Kentucky, USA. It provides a wide range of services, resources, and information related to business filings, elections, and government matters. The website offers various tools and features to assist individuals, businesses, and organizations in accessing important information and conducting official transactions."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Kentucky'
    category = 'Official Registry'
    url = "https://web.sos.ky.gov/bussearchnprofile/Profile/?ctr="
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
