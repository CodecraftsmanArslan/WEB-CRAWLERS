"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
from bs4 import BeautifulSoup
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from requests.exceptions import RequestException
from helpers.crawlers_helper_func import CrawlersFunctions

arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 1

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
    @return dict
    '''
    # preparing addresses_detail dictionary object
    addresses_detail = []
    general_address = dict()  
    general_address["type"]="general_address"
    general_address["address"]=record["Place of Business"].replace("'","''") if 'Place of Business' in record else ""
    general_address["description"]=""
    general_address["meta_detail"]={} 
    registered_office_address = dict()
    registered_office_address["type"]= "registered_office_address"
    registered_office_address["address"]= record["Registered Office Address"].replace("'","''") if "Registered Office Address" in record else ""
    registered_office_address["description"]= ""
    registered_office_address["meta_detail"]= {}
       
    if general_address['address'] !="":
        addresses_detail.append(general_address)
    elif registered_office_address['address'] !="":
        addresses_detail.append(registered_office_address)
    
    # preparing meta_detail dictionary object
    meta_detail = dict()  
    meta_detail['registry_type'] = record['Registry Type'].replace("'","''") if 'Registry Type' in record  else ""
    meta_detail['is_in_liquidation'] = record['Is in Liquidation?'] if 'Is in Liquidation?' in record else ""
    meta_detail['presence_of_charges'] = record['Presence of Charges'] if 'Presence of Charges' in record else ""
    meta_detail['receiver(s)_appointed'] = record['Receiver(s) Appointed?'] if 'Receiver(s) Appointed?' in record else ""
    meta_detail['strike-off_details'] = record['Strike-Off Details'].replace("'","''") if 'Strike-Off Details' in record else ""
    meta_detail['dissolution_details'] = record['Dissolution Details'].replace("'","''") if 'Dissolution Details' in  record else ""
    meta_detail['additional_information'] = record['Additional Information'].replace("'","''") if 'Additional Information' in record else ""
    
    # preparing people_detail dictionary object
    people_detail = []
    people_details = dict()
    people_details["designation"]= "registered_agent"
    people_details["name"] = record['Agent'] if 'Agent' in record else ""
    people_details["address"]= record["Registered Office Address"].replace("'","''") if "Registered Office Address" in record else ""

    if people_details['name'].strip() != "" and people_details['address'].strip() != "":
        people_detail.append(people_details)
    
   
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['Name'].replace("'","''").replace('\"',""),
        "status": record['Status'].replace("'","''"),
        "registration_number": record['Number'] if 'Number' in record else "",
        "registration_date": record['Date of Registration'] if 'Date of Registration' in record else "",
        "dissolution_date": record['Dissolved Date or Struck Off Date'] if 'Dissolution Date or Struck Off Date' in record else "",
        "incorporation_date":record['Date of Incorporation'] if 'Date of Incatenation' in record else "",
        "inactive_date":record['Ceased Date'] if 'Ceased Date' in record else "",
        "type": record['Company Type'].replace('"',"''") if 'Company Type' in record else "",
        "crawler_name": "crawlers.custom_crawlers.kyb.isle_of_man.isle_of_man_kyb",
        "country_name": "Isle of Man",
        "people_detail":people_detail,
        "addresses_detail":addresses_detail,
        "previous_names_detail":record['Previous_name_datil'],
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
    data_for_db.append(shortuuid.uuid(record['Number']+'isle_of_man_kyb')) # entity_id
    data_for_db.append(record["Name"].replace("'", "")) #name
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

def make_request(url, headers, timeout):
        max_retries = 3
        for retry in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
                return response
            except RequestException as e:
                time.sleep(10*60)
                print(f'Request failed. Retrying ({retry+1}/{max_retries})...')
                print(f'Error: {e}')
        
        print(f'Failed to make request after {max_retries} retries.')
        return None

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
        page = PAGE
        while True: #7255
            data_list = []
            url_template = f'https://services.gov.im/ded/services/companiesregistry/companysearch.iom?SortBy=Name&SortDirection=0&searchtext=_&search=Search&page={page}'
            url_ = url_template.format(page=page)
            print('page Number = ',page)
            headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            response = requests.get(url_,headers=headers,timeout=60)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            soup = BeautifulSoup(response.text, 'html.parser')
            table_ = soup.find('table',class_ = 'table')
            trs =  soup.find_all('tr')
            if trs == None:
                break
            for tr in trs:
                td = tr.find('td')
                a_tags=td.find_all('a')
                for a in a_tags:
                    href= a.get("href").strip()
                    base_url = 'https://services.gov.im/ded/services/companiesregistry/'
                    # base_url = 'https://services.gov.im/ded/services/companiesregistry/viewcompany.iom?Id=rEerKEHQ6DnRVvUGydz%2fTg%3d%3d'
                    nex_link = base_url+href
                    time.sleep(3)
                    # Usage
                    response2 = make_request(nex_link, headers=headers, timeout=120)
                    if response2 == None:
                        continue
                    soup2 = BeautifulSoup(response2.text, 'html.parser')
                    # Find all the tables on the page
                    tables = soup2.find_all("table")
                    # Iterate over each table
                    data_dict = {}
                    for table in tables:
                        # Find all the rows in the table
                        rows = table.find_all("tr")
                        keys = ""
                        values = ""
                        # Iterate over each row
                        for row in rows:
                            header_cell = row.find("th")
                            if header_cell:
                                keys = header_cell.get_text(strip=True)
                            value_cell = row.find("td")
                            if value_cell:
                                values = value_cell.get_text(strip=True)
                            if keys and values:
                                data_dict[keys] = values
                    data_list.append(data_dict)  
                    
                    table_ = soup2.find_all("table")[1] 
                    table_rows = table_.find_all("tr")
                    Previous_name_datil = []
                    for row_ in table_rows[1:]:
                        columns = row_.find_all('td')
                        if len(columns) == 2:
                            Previous_name_datil.append({
                                    "name": columns[0].get_text(strip=True).replace("'","''").replace("%","%%"),
                                    "meta_detail":{
                                        "status":columns[1].get_text(strip=True).replace("'","''") if columns[1].get_text(strip=True) is not None else ""
                                    }
                                })
                    data_dict['Previous_name_datil'] = Previous_name_datil
                    try:
                        table_2 = soup2.find_all("table")[2] 
                        table_rows2 = table_2.find_all("tr")[1:]
                        for row2 in table_rows2:
                            columns2 = row2.find_all('td')
                            if len(columns2) == 2:
                                Previous_name_datil.append({
                                    "name":columns2[0].get_text(strip=True).replace("'","''").replace("%","%%"),
                                    "meta_detail":{
                                        "status":columns2[1].get_text(strip=True).replace("'","''") if columns2[1].get_text(strip=True) is not None else ""
                                    }
                                })
                        data_dict['Previous_name_datil'] = Previous_name_datil
                    except Exception as e:
                        print(e)
                        pass
            
            for record_ in data_list:
                print(record_)
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                
                print("stored records\n")
                crawlers_functions.db_connection(query)
            
            page += 1

        return len(data_list), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for 
    '''
    name = 'Department for Enterprise - Companies Registry'
    description = "This web information about companies registered in the Isle of Man by entering search criteria such as the company name or registration number."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Isle of Man'
    category = 'Official Registry'
    url = 'https://services.gov.im/ded/services/companiesregistry/companysearch.iom?SortBy=Name&SortDirection=0&searchtext=_&search=Search&page=1'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
