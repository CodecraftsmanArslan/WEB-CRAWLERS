import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from helpers.logger import Logger
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
API_KEY_TRANSLATION = os.getenv("API_KEY_TRANSLATION")

def get_listed_object(record, entity_type, category_, countries, aliases):
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
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['aliases'] = str(aliases.replace("'","''")) 

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[2].replace("'","''"),
        "status": record[4].replace("'","''"),
        "registration_number": str(record[0])+str(record[1]),
        "registration_date": "",
        "dissolution_date": "",
        "type": record[3].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.georgia.georgia_kyb",
        "country_name": "Georgia",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail
    }

    return data_obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, aliases):
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
    data_for_db.append(shortuuid.uuid(shortuuid.uuid(f'{record[0]+record[1]}-{url_}-georgia_kyb'))) # entity_id
    data_for_db.append(record[2].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record, entity_type, category, country, aliases))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
    data_for_db.append(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    data_for_db.append(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
        response = requests.get(SOURCE_URL, stream=True, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        API_URL = "https://enreg.reestri.gov.ge/main.php"
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'MMR_PUBLIC=ack5ict0r2kbc24v306v06llm5',
            'Host': 'enreg.reestri.gov.ge',
            'Origin': 'https://enreg.reestri.gov.ge',
            'Referer': 'https://enreg.reestri.gov.ge/main.php?m=new_index',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        payload = {'data':"c=search&m=find_legal_persons&p={}"}
        
        page_number = 1
        DATA = []
        CHUNK = []
        while page_number < 3236:
            print("Page Number: ", page_number)
            response = requests.post(API_URL, data=payload['data'].format(page_number), headers=headers, timeout=60)
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                page_number+=1
                if not rows:
                    break

                for row in rows:
                    if row.find_all("td"):
                        columns = row.find_all("td")
                        if len(columns) == 6:
                            id_code = columns[1].text.strip()
                            per_number = columns[2].text.strip()
                            firm_name = columns[3].text.strip()
                            aliases = firm_name
                            firm_type = columns[4].text.strip()
                            firm_status = columns[5].text.strip()

                            record = [id_code, per_number, firm_name, firm_type, firm_status]
                            DATA.append(record)

                            record = list(record)
                            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description, aliases)
                            query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)

                            if record_for_db[1] != "":
                                print("Stored record.")
                                crawlers_functions.db_connection(query)
   
        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Georgia
    '''
    name = 'Georgian National Agency of Public Registry'
    description = "Official corporate registry search platform maintained by the Georgian National Agency of Public Registry. The website provides information on companies registered in Georgia and provides a range of relevant details such as the company name, registration status, and date of incorporation."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Georgia'
    category = 'Official registry'
    url = 'https://enreg.reestri.gov.ge/main.php?m=new_index'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()