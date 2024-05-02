"""Set System Path"""
import re
import sys
from pathlib import Path
from textwrap import fill
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

def get_request_data(url):

    response_status = 500
    retry_count = -1
    while response_status != 200:

        try:
            response = requests.get(url)
            response_status = response.status_code
            if response_status == 200:
                return response
                
            else:
                retry_count += 1
                print('Element not found retrying.')
                if retry_count>4:
                    break
                time.sleep(10)
        except:
            print('Connection error')
            continue
    
def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''
    address_components = [record['address'], record['city'], record['state'], record['zip'], record['country']]
    general_address = ' '.join(component for component in address_components if component)

    addresses_detail = [
        {
            'type' : 'general_address',
            'address' : general_address
        }
    ] if record['address'] or record['city'] or record['country'] else []
    
    meta_detail = {
        'effective_date' : record['effective_date'],
        "purpose": record['purpose'],
    }

    additional_detail = []

    if record['stock_class'] or record['series'] or record['share_per_value'] or record['authorized_share'] or record['issued_share']:
        share_information = {
            'type': "share_information",
            'data': [
                {
                    'stock_class': record['stock_class'],
                    'series': record['series'],
                    'share_per_value': record['share_per_value'],
                    'authorized_share': record['authorized_share'],
                    'issued_share': record['issued_share'],
                },
            ],
        }
        additional_detail.append(share_information)

    if record['naics_code']:
        naics_information = {
            'type': "naics_code",
            'data': [
                {
                    'naics_code': record['naics_code'].replace("'", "''"),
                },
            ],
        }
        additional_detail.append(naics_information)

    additional_detail = [a for a in additional_detail if a]


    data_obj = {
        "name": record['name'].replace("'","''"),
        "status": "",
        "registration_number": str(record['identification_number']).replace("'","''"),
        "registration_date":'',
        "type": record['entity_type'].replace("'", "''"),
        "crawler_name": "rhode_island_kyb",
        "country_name": "Rhode Island",
        "company_fetched_data_status": "",
        "addresses_detail": addresses_detail,
        "meta_detail": meta_detail,
        "people_detail": record['people_list'],
        "fillings_detail": record['fillings_detail'],      
        "incorporation_date": record['incorporation_date'],
        "dissolution_date": record['dissolution_date'],
        "additional_detail": additional_detail,
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
    crawlers_name= 'rhode_island_kyb'
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(record['identification_number']+str(url)+crawlers_name)) # entity_id
    data_for_db.append(record['name'].replace("'","''")) #name
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
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url

        arguments = sys.argv
        c_id = int(arguments[1]) if len(arguments)>1 else 1

        while c_id <= 1999999: 

            print("record number", c_id)
            api_url = f'https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSummary.aspx?FEIN={c_id}' 
            response =  get_request_data(api_url)
            soup = BeautifulSoup(response.text, "html.parser")

            if "MainContent_lblMessage" in response.text:
                print("record not exist of id :", c_id)
                c_id += 1
                continue

            people_list = list()
            data = dict()

            data['name'] = soup.find(id='MainContent_lblEntityName').text.strip().replace("'", "''")
            data['entity_type'] = soup.find(id='MainContent_lblEntityType').text.strip().replace("'", "''")
            data['identification_number'] = soup.find(id='MainContent_lblIDNumber').text.split(':')[-1].strip().replace("'", "''")
            data['incorporation_date'] = soup.find(id='MainContent_lblOrganisationDate').text.strip().replace("'", "''") if  soup.find(id='MainContent_lblOrganisationDate') else ''
            data['effective_date'] = soup.find(id='MainContent_lblEffectiveDate').text.strip().replace("'", "''") if  soup.find(id='MainContent_lblEffectiveDate') else ''
            data['dissolution_date'] = soup.find(id='MainContent_lblInactiveDate').text.strip().replace("'", "''") if soup.find(id='MainContent_lblInactiveDate') else ''
            data['address'] = soup.find(id='MainContent_lblPrincipleStreet').text.strip().replace("'", "''")
            data['city'] = soup.find(id='MainContent_lblPrincipleCity').text.strip().replace("'", "''")
            data['state'] = soup.find(id='MainContent_lblPrincipleState').text.strip().replace("'", "''")
            data['zip'] = soup.find(id='MainContent_lblPrincipleZip').text.strip().replace("'", "''")
            data['country'] = soup.find(id='MainContent_lblPrincipleCountry').text.strip().replace("'", "''")

            registered_agent_name = soup.find(id='MainContent_lblResidentAgentName').text.strip().replace("'", "''")
            registered_agent_address = soup.find(id='MainContent_lblResidentStreet').text.strip().replace("'", "''")
            registered_agent_city = soup.find(id='MainContent_lblResidentCity').text.strip().replace("'", "''")
            registered_agent_state = soup.find(id='MainContent_lblResidentState').text.strip().replace("'", "''")
            registered_agent_zip = soup.find(id='MainContent_lblResidentZip').text.strip().replace("'", "''")
            registered_agent_country = soup.find(id='MainContent_lblResidentCountry').text.strip().replace("'", "''")

            registered_agent = dict()
            registered_agent['name'] = registered_agent_name
            components = [registered_agent_address, registered_agent_city, registered_agent_state, registered_agent_zip, registered_agent_country]
            registered_agent['address'] = ' '.join(component for component in components if component)
            registered_agent['designation'] = "registered_agent"

            people_list.append(registered_agent) if registered_agent_name else ''
           
            table_people_data = soup.find(id='MainContent_grdOfficers')
            if table_people_data:
                table_rows = table_people_data.find_all('tr')
                for row in table_rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        people = dict()
                        people['designation'] = cells[0].text.strip().replace("'", "''")
                        people['name'] = cells[1].text.strip().replace("'", "")
                        people['address'] = cells[2].text.strip().replace("'", "''")
                        people_list.append(people) if people['name'] != '' else ''

            data['people_list'] = people_list

            table_stock_data = soup.find(id='MainContent_grdStocks')
            if table_stock_data:
                table_rows = table_stock_data.find_all('tr')
                for row in table_rows:
                    cells = row.find_all('td')
                    if len(cells) > 3:
                        data['stock_class'] = cells[0].text.strip().replace("'", "''")
                        data['series'] = cells[1].text.strip().replace("'", "")
                        data['share_per_value'] = cells[2].text.strip().replace("'", "''")
                        data['authorized_share'] = cells[3].text.strip().replace("'", "''")
                        data['issued_share'] = cells[4].text.strip().replace("'", "''")
                    else:
                        data['stock_class'] = ''
                        data['series'] = ''
                        data['share_per_value'] = ''
                        data['authorized_share'] = ''
                        data['issued_share'] = ''
            else:
                data['stock_class'] = ''
                data['series'] = ''
                data['share_per_value'] = ''
                data['authorized_share'] = ''
                data['issued_share'] = ''


            naics_code_element = soup.find('input',id="MainContent_txtNIACS")

            if naics_code_element:
                data['naics_code'] = naics_code_element.get('value', '')

         

            purpose = soup.find(id='MainContent_txtComments') if soup.find(id='MainContent_txtComments') else ''
            data['purpose'] = purpose.text.strip().replace("'", "''").replace('\n', '').replace('\r', '') if purpose else ''
        

            viewstate = soup.find(id="__VIEWSTATE")
            viewstate_value = viewstate["value"]
            

            viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
            viewstate_generator = viewstategen["value"]

            event = soup.find(id="__EVENTVALIDATION")
            event_validation = event["value"]

            option = soup.find(
                "option", selected="selected", text="ALL FILINGS")
            lst_filling = option["value"]

            input_tag = soup.find(
                "input", attrs={"name": "ctl00$MainContent$btnViewFilings"})
            view_filling = input_tag["value"]

            BODY = {
                '__EVENTTARGET': "",
                '__EVENTARGUMENT': "",
                '__VIEWSTATE': viewstate_value,
                '__VIEWSTATEGENERATOR': viewstate_generator,
                '__SCROLLPOSITIONX': 0,
                ' __SCROLLPOSITIONY': 0,
                '__EVENTVALIDATION': event_validation,
                'ctl00$MainContent$txtComments':  "",
                'ctl00$MainContent$txtNIACS': "",
                'ctl00$MainContent$lstFilings': lst_filling,
                'ctl00$MainContent$btnViewFilings': view_filling,
            }

            nine_number_format = "{:09d}".format(int(c_id))

            file_url = f"https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSummary.aspx?FEIN={nine_number_format}"

            filling_response =  requests.post(file_url, data=BODY)
            filling_soup = BeautifulSoup(filling_response.text, "html.parser")

            filling_details = list()
            filing_table =  filling_soup.find("table", id="MainContent_grdSearchResults")
            base_url  ='https://business.sos.ri.gov/CorpWeb/CorpSearch/'
            if filing_table:

                table_rows = filing_table.find_all('tr')
                for row in table_rows[1:]:
                    cells = row.find_all('td')
                    filling_obj = dict()
                    filling_obj['title'] = cells[1].text.strip().replace("'", "")
                    filling_obj['date'] = cells[3].text.strip().split(" ")[0].replace("/", "-")
                    filling_obj['filing_code'] = cells[4].text.strip().replace("'", "''")
                    try:
                        file_link = base_url+cells[5].find('a')['href']
                    except:
                        file_link = ""
                    
                    if file_link:
                        filling_obj['meta_detail'] = {
                            'file_url': file_link,
                            'year': cells[2].text.strip().replace("'", "''")
                        }
                    else:
                        filling_obj['meta_detail'] = {
                            'file_url': '',
                            'year': cells[2].text.strip().replace("'", "''")
                        }
                    filling_details.append(filling_obj)

    
            data['fillings_detail'] = filling_details

            record_for_db = prepare_data(data, category,
                                                country, entity_type, source_type, name, url, description)

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print('record stored')
            json_data = json.loads(record_for_db[7])
            registration_number = json_data['registration_number']
            record_name = record_for_db[1].strip()
            if not (record_name == '' and registration_number.strip() == ''):
                crawlers_functions.db_connection(query)
            
           
    
            c_id += 1

        return c_id, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Rhode Island
    '''
    name = 'Rhode Island Secretary of State'
    description = "The Rhode Island Secretary of State website serves as the official online platform for the Office of the Secretary of State in the state of Rhode Island, USA. It provides a wide range of services and resources related to business filings, elections, and government information. The website offers various tools and features to assist individuals, businesses, and organizations in accessing important information and conducting official transactions."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Rhode Island'
    category = 'Official Registry'
    url = 'https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearch.aspx'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
