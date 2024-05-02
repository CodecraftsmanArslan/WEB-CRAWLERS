"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import pandas as pd
import requests, json,os
from langdetect import detect
from selenium import webdriver
from dotenv import load_dotenv
from helpers.logger import Logger
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
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
# options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


def get_listed_object(record, entity_type, category_, countries):
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
    entity_status = ['Any','Registered','Ceased','','Undergoing Strike Off','','Dissolved','Struck Off','Undergoing Dissolution (Voluntary)','Undergoing Dissolution (Creditors Winding Up)','Undergoing Dissolution (Court Winding Up)','Non-Compliance','Active']
    entity_types = ["Business Name", "Private Company","Public Company","Foreign Branch","","Statutory Body",
"Cooperatives","Non-ROCBN Registered Entity","Individual",]
    # preparing addresses_detail dictionary object
    addresses_detail = dict()
    addresses_detail["type"]= "general_address"
    if record["address"] is not None:

        components = [record['address']['address1'], record['address']['address2'], record['address']['address3'], record['address']['village'], record['address']['mukim'], record['address']['district']['name'] if record['address']['district'] is not None else "", record['address']['postalCode'], record['address']['country']['name'] if record['address']['country'] is not None else ""]
        addresses_detail["address"] = ' '.join(component.replace("'", "''").replace("000000", "").replace("NULL", "") for component in components if component and component != "Not Specified")
       
        ADDRESSES_DETAIL = [addresses_detail]
    else: 
        ADDRESSES_DETAIL = []
    
    # preparing meta_detail dictionary object
    meta_detail = dict()

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record['name'].replace("'","''").replace("•","").replace("null",""),
        "status": entity_status[record['entityStatus']],
        "registration_number": record['registrationNo'],
        "registration_date": record['registrationDate'][:10],
        "dissolution_date": "",
        "type": entity_types[record['entityTypeId']],
        "crawler_name": "crawlers.custom_crawlers.kyb.brunei_kyb",
        "country_name": "Brunei",
        "company_fetched_data_status": "",
        "addresses_detail": ADDRESSES_DETAIL,
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
    data_for_db.append(shortuuid.uuid(f'{record["registrationNo"]}-{record["entityTypeId"]}-brunei_kyb')) # entity_id
    data_for_db.append(record['name'].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record, entity_type, category, country))) # data
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


def get_req_data(token, num_records):
        """_summary_

        Args:
            token (str): token to be sent in request
            num_records (int): number of records to retrieve

        Returns:
            Object: response object
        """
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json','User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        data = {"isPageLoad":False,
                "searchType":1,
                "isSearching":False,
                "basicSearchValue":"",
                "searchOperator":2,
                "registerType":0,
                "entityTypeId":0,
                "entityStatus":0,
                "dateSelectionOption":0,
                "startDate":None,
                "endDate":None,
                "businessActivityId":0,
                "pagination":{"page":1,"pageSize":num_records}}
        
        response = requests.post(api_url, headers=headers, json=data)
        return response
    
def check_is_none(value):
    """_summary_

    Args:
        value (Str): value to check if it is None

    Returns:
        Str: value to return
    """
    return value if value is not None else ''
def get_records(source_type, entity_type, country, category, url, api_url, login_url, name, description):
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
        driver.get(login_url)
        time.sleep(5)
        foreign_passport = driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div/div[2]/div/div/form/div[2]/div/label[2]")
        foreign_passport.click()
        user_name = driver.find_element(By.ID,"Username")
        user_name.send_keys("AH0546041")
        password = driver.find_element(By.ID,"Password")
        password.send_keys("Zxcvbnm12345!")
        country_select = Select(driver.find_element(By.ID,'NationalityId'))
        country_select.select_by_visible_text('Pakistan')
        login_button = driver.find_element(By.XPATH,'/html/body/div[2]/main/div/div/div[2]/div/div/form/div[6]/button')
        login_button.click()
        time.sleep(10)
        auth_data = driver.execute_script("return localStorage.getItem('oidc.user:https://accounts.ocp.mofe.gov.bn:eservice_portal_prod_onprem_env')")
        auth_data = json.loads(auth_data)
        token = auth_data["access_token"]
        driver.close()
        # print('i came here')
        # print({'Authorization': f'Bearer {token}'})
        
        response = get_req_data(token,1)
        print(response.json()['totalItems'],'totalItems')
        response = get_req_data(token, response.json()['totalItems'])
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        data = response.json()['lists']
        for rec in data:
            record_for_db = prepare_data(rec, category,
                                                country, entity_type, source_type, name, url, description)
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
            if record_for_db[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)
                print('record inserted successfully for: ',record_for_db[1])
        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Brunei
    '''
    name = 'Ministry of Finance and Economy in Brunei Darussalam'
    description = "This portal provides a range of online services to individuals and businesses in Brunei Darussalam, such as applying for government permits and licenses, paying taxes, and accessing government information and resources."
    entity_type = 'Company/Organization'
    source_type = 'HTML/JSON'
    countries = 'Brunei'
    category = 'Official Registry'
    url = 'https://ocp.mofe.gov.bn/'
    login_url = 'https://eservices.ocp.mofe.gov.bn/login'
    api_url = 'https://gw.ocp.mofe.gov.bn/public/api/entitySearch/entityRegisterSearch'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,api_url, login_url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
