"""Set System Path"""
from operator import le
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
import requests, json,os, re
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
from selenium.common.exceptions import TimeoutException
from dateutil import parser
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import urllib.parse

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
fillings_detail = list()
previous_names_detail = list()
people_list = list()


def get_request_data(url,body,cookies):
   
    HEADERS =  {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "cookie": cookies,
        "Referer": "https://bsd.sos.in.gov/PublicBusinessSearch",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    response_status = 500
    retry_count = -1
    while response_status != 200:

        try:
            response = requests.post(url, body, headers=HEADERS, timeout=200)
            cfbm_cookies = response.headers.get('Set-cookie').split(';')[0].split('=')[1] if len(response.headers.get('Set-cookie').split(';')[0].split('=')[1]) > 50 else ''
        
            response_status = response.status_code
            if response_status == 200:
                return response,cfbm_cookies
                
            else:
                retry_count += 1
                print('Element not found retrying.')
                if retry_count>4:
                    break
                time.sleep(10)
        except:
            print('Connection error')
            continue
            

def timestamp_to_str(timestamp):
    try:
        # Parse the timestamp into a datetime object
        datetime_obj = parser.parse(timestamp)
        # Extract the date portion from the datetime object
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        print("time format:", e)
        date_str = timestamp
    return date_str

def create(record_, source_type, entity_type, country, category, url, name, description, v):
    if len(record_) != 0:
        record_for_db = prepare_data(record_, category,
                                        country, entity_type, source_type, name, url, description)
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
        print("Category value", v)
        json_data = json.loads(record_for_db[7])
        registration_number = json_data['registration_number']
        record_name = record_for_db[1].strip()
        if not (record_name == '' and registration_number.strip() == ''):
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
    data_for_db.append(shortuuid.uuid(f"{record['registration_number']}{url_}-indiana_kyb"))
    data_for_db.append(record['name']) #name
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

def get_listed_object(record):
    global fillings_detail, previous_names_detail, people_list
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
    meta_detail['expiration_date'] = record['expiration_date']
    meta_detail['report_due_date'] = timestamp_to_str(record['report_due_date']) if record['report_due_date'] else ''
    meta_detail['years_due'] = record['years_due']
    meta_detail['formation_date'] = timestamp_to_str(record['formation_date']) if record['formation_date'] else ''

    address_details = [
        {
            'type': 'office_address',
            'address': record['address'].replace("NONE,", ''),
        } if record['address'] else ''
    ]
    address_details = [a for a in address_details if a]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record['name'],
        "registration_number": record['registration_number'],
        "incorporation_date": timestamp_to_str(record['incorporation_date']),
        "people_detail": record['people_detail'],
        "status": record['status'],
        "dissolution_date": "",
        "type": record['type'],
        "crawler_name": "custom_crawlers.kyb.indiana.indiana_kyb_category",
        "country_name": "Indiana",
        "registration_date": "",
        "company_fetched_data_status": "",
        "jurisdiction": record['jurisdiction'],
        "inactive_date": record['inactive_date'],
        "meta_detail": meta_detail,
        'addresses_detail': address_details,
        'people_detail': record['people_detail'],
        'fillings_detail': record['fillings_detail'],
        'previous_names_detail': record['previous_names_detail'],      
    }

    fillings_detail = []
    previous_names_detail = []
    people_list = []
    
    return data_obj

def get_filing_data_from_table(filing_table):
    global fillings_detail

    filing_table_rows = filing_table.find_all('tr')
    if len(filing_table_rows) >= 1:
        for filing in filing_table_rows[1:]:
            cells = filing.find_all('td')
            if len(cells) > 2:
                file_history = dict()
                file_history['date'] = cells[0].text.strip().replace("'", "''").replace("/","-")
                file_history['filing_code'] = cells[2].text.strip().replace("'", "''") if cells[2].text else ''
                if cells[3]:
                    anchor_tag = cells[3].find('a')
                    if anchor_tag:
                        file_history['filing_type'] = anchor_tag.text.strip().replace("'", "''") if anchor_tag else ''
                        file_history['file_url'] = 'https://bsd.sos.in.gov'+anchor_tag['href'] if anchor_tag['href'] else ''
                    else:
                        file_history['filling_type'] = ''
                        file_history['filling_url'] = ''
                file_history['meta_detail'] = {
                    'effective_date' : cells[1].text.strip().replace("'", "''").replace("/","-") if cells[2].text else ''
                } if cells[2].text else {}
                fillings_detail.append(file_history)

def get_filling_history(total_pages, business_id, cfbm_cookies, session_id, request_verification_token, cookies):
   
    for i in range(2,total_pages+1):

        if cfbm_cookies:
            cookies = f"ASP.NET_SessionId={session_id};__cf_bm={cfbm_cookies};__RequestVerificationToken={request_verification_token};"
    
        filing_pagination_url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessFilings'
        filing_pagination_body = f"businessid={business_id}&isBack=true&source=&sortby=&stype=a&pidx={i}"

        company_detail_response, cfbm_cookies   = get_request_data(filing_pagination_url, filing_pagination_body, cookies)
        filing_soup = BeautifulSoup(company_detail_response.text, "html.parser")
        filing_pagination_table = filing_soup.find('table', id='xhtml_grid')

        if filing_pagination_table:
            get_filing_data_from_table(filing_pagination_table)

def get_naming_data(name_history_table):
    global previous_names_detail
    name_history_rows = name_history_table.find_all('tr')
    if len(name_history_rows) > 0:
        for names_data_row in name_history_rows[1:]:
            names_cells = names_data_row.find_all('td')
            if len(names_cells) > 2:
                name_history = dict()
                name_history['name'] = names_cells[3].text.strip().replace("'", "''") if names_cells[3] else ''
                name_history['update_date'] = names_cells[1].text.strip().replace("'", "''").replace("/", "-") if names_cells[1] else ''
                name_history['meta_detail'] = {
                    'filing_date' : names_cells[0].text.strip().replace("'", "''").replace("/", "-") if names_cells[0] else '',
                    'filing_number': names_cells[2].text.strip().replace("'", "''") if names_cells[2] else ''
                } if names_cells[0] or names_cells[2] else {}
                previous_names_detail.append(name_history)

def get_incorporate_people(incorporator_table):
    global people_list
    incorporator_table_rows = incorporator_table.find_all('tr')
    if len(incorporator_table_rows) >= 1:
        for people in incorporator_table_rows[1:]:
            cells = people.find_all('td')
            if len(cells) > 1:
                people = dict()
                people['designation'] = cells[0].text.strip().replace("'", "''")
                people['name'] = cells[1].text.strip().replace("'", "''") if cells[2] else ''
                people['address'] = cells[2].text.strip().replace("'", "''").replace("NONE", "").replace("..", "") if cells[2] else ''
                people_list.append(people)

def get_governing_people(governing_table):
    global people_list
    governing_table_rows = governing_table.find_all('tr')
    if len(governing_table_rows) >= 1:
        for people in governing_table_rows[1:]:
            cells = people.find_all('td')
            if len(cells) > 1:
                people = dict()
                people['designation'] = cells[0].text.strip().replace("'", "''")
                people['name'] = cells[1].text.strip().replace("'", "''") if cells[2] else ''
                people['address'] = cells[2].text.strip().replace("'", "''").replace("NONE", "").replace("..", "") if cells[2] else ''
            people_list.append(people)    

def get_naming_history(total_pages, business_id, cfbm_cookies, session_id, request_verification_token, cookies):

    for i in range(2, total_pages+1):

        if cfbm_cookies:
            cookies = f"ASP.NET_SessionId={session_id};__cf_bm={cfbm_cookies};__RequestVerificationToken={request_verification_token};"
        naming_pagination_url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessNameHistory'
        naming_pagination_body = f"businessid={business_id}&isBack=true&source=&sortby=&stype=a&pidx={i}"

        naming_pagination_response, cfbm_cookies   = get_request_data(naming_pagination_url, naming_pagination_body, cookies)
        filing_soup = BeautifulSoup(naming_pagination_response.text, "html.parser")
        naming_pagination_table = filing_soup.find('table', id='xhtml_grid')

        if naming_pagination_table:
            get_naming_data(naming_pagination_table)

def incorporate_people_pagination(total_pages,business_id, cfbm_cookies, session_id, request_verification_token, cookies):
    for i in range(2, total_pages+1):
        if cfbm_cookies:
            cookies = f"ASP.NET_SessionId={session_id};__cf_bm={cfbm_cookies};__RequestVerificationToken={request_verification_token};"
        incorporate_pagination_url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessIncorporatorsList'
        incorporate_pagination_body = f"BusinessId={business_id}&sortby=&stype=a&pidx={i}"

        incorporate_pagination_response, cfbm_cookies   = get_request_data(incorporate_pagination_url, incorporate_pagination_body, cookies)
        incorporate_soup = BeautifulSoup(incorporate_pagination_response.text, "html.parser")
        incorporate_pagination_table = incorporate_soup.find('table', id='xhtml_grid')

        if incorporate_pagination_table:
            get_incorporate_people(incorporate_pagination_table)

def governing_people_pagination(total_pages,business_id, cfbm_cookies, session_id, request_verification_token, cookies):
    for i in range(2, total_pages+1):
        if cfbm_cookies:
            cookies = f"ASP.NET_SessionId={session_id};__cf_bm={cfbm_cookies};__RequestVerificationToken={request_verification_token};"
        governing_pagination_url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessPrincipalsList'
        governing_pagination_body = f"BusinessId={business_id}&sortby=&stype=a&pidx={i}"

        governing_pagination_response, cfbm_cookies   = get_request_data(governing_pagination_url, governing_pagination_body, cookies)
        governing_soup = BeautifulSoup(governing_pagination_response.text, "html.parser")
        governing_pagination_table = governing_soup.find('table', id='xhtml_grid')

        if governing_pagination_table:
            get_governing_people(governing_pagination_table)

def get_data_from_table(driver, total_page, source_type, entity_type, country, category, url, name, description, v):

    global people_list,fillings_detail,previous_names_detail
    cookies = driver.get_cookies()
    cf_bm = None
    session_id = None
    request_verification_token = None
    for cookie in cookies:
        if cookie['name'] == '__cf_bm':
            cf_bm = cookie['value']
        if cookie['name'] == '__RequestVerificationToken':
            request_verification_token = cookie['value']
        if cookie['name'] == 'ASP.NET_SessionId':
            session_id = cookie['value']

    search_page_url = "https://bsd.sos.in.gov/PublicBusinessSearch"
    cookies = f"ASP.NET_SessionId={session_id}; __cf_bm={cf_bm}; __RequestVerificationToken={request_verification_token}"

    existing_anchors = set()
    existing_pagination = set()
    existing_business_ids = set()

    with open('category_anchors.txt', 'r') as file:
        for line in file:
            existing_anchors.add(line.strip())

    with open('category_pagination.txt', 'r') as file:
        for line in file:
            existing_pagination.add(line.strip())

    with open('category_business_ids.txt', 'r') as file:
        for line in file:
            existing_business_ids.add(line.strip())

    for i in range(1, total_page+1):

        print(i)
        if str(i) not in existing_pagination:
            search_page_body = f"undefined&sortby=&stype=a&pidx={i}"
            response, cfbm_cookies  = get_request_data(search_page_url, search_page_body, cookies)
            search_page_soup = BeautifulSoup(response.text, "html.parser")

            request_verification_token_element = search_page_soup.find('input', {'name': '__RequestVerificationToken'})
            request_token = request_verification_token_element['value']

            company_table = search_page_soup.find('table', id="grid_businessList")
            tags = company_table.find_all('a')
            # Open the file for writing and iterate over the anchor tags to write them, skipping duplicates
            with open('category_anchors.txt', 'a') as file:
                for anchor in tags:
                    if anchor is not None:
                        anchor_str = str(anchor)
                        if anchor_str not in existing_anchors:
                            file.write(anchor_str + '\n')
                            existing_anchors.add(anchor_str)
            
            with open('category_pagination.txt', 'a') as file:
                file.write(str(i) + '\n')
                existing_pagination.add(i)

        elif i == total_page:
            search_page_body = f"undefined&sortby=&stype=a&pidx={i}"
            response, cfbm_cookies  = get_request_data(search_page_url, search_page_body, cookies)
            search_page_soup = BeautifulSoup(response.text, "html.parser")
            request_verification_token_element = search_page_soup.find('input', {'name': '__RequestVerificationToken'})
            request_token = request_verification_token_element['value'] 

    with open('category_anchors.txt', 'r') as file:
        for line in file:
            tag_soup = BeautifulSoup(line, 'html.parser')
            tag = tag_soup.find('a')

            if cfbm_cookies:
                cookies = f"ASP.NET_SessionId={session_id};__cf_bm={cfbm_cookies};__RequestVerificationToken={request_verification_token};"
            businessid = urllib.parse.quote(tag['businessid'])
            businesstype = urllib.parse.quote(tag['businesstype'])
            id = urllib.parse.quote(tag['id'])
            isseries = urllib.parse.quote(tag['isseries'])

            if str(businessid) not in existing_business_ids:

                url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessInformationFromIndex'
                body = f"BusinessID={businessid}&BusinessType={businesstype}&ID={id}&IsSeries={isseries}&__RequestVerificationToken={request_token}"

                company_detail_response, cfbm_cookies   = get_request_data(url, body, cookies)
                soup = BeautifulSoup(company_detail_response.text, "html.parser")
        
                data = dict()
                
                business_name_el = soup.find("td", string=re.compile("Business Name:"))
                data['name'] = business_name_el.find_next('strong').text.strip().replace("'", "''") if business_name_el else ''

                entity_type_el = soup.find("td", string="Entity Type:")
                data['type'] = entity_type_el.find_next('strong').text.strip().replace("'", "''") if entity_type_el else ''
                
                business_status_el = soup.find("td", string="Business Status:")
                data['status'] = business_status_el.find_next('strong').text.strip().replace("'", "''") if business_status_el else ''

                business_id_el = soup.find("td", string="Business ID:")
                data['registration_number'] = business_id_el.find_next('strong').text.strip().replace("'", "''") if business_id_el else ''

                creation_date_el = soup.find("td", string=re.compile("Creation Date:"))
                data['incorporation_date'] = creation_date_el.find_next('strong').text.strip() if creation_date_el else ''
                try:
                    inactive_date_el = soup.find("td", string=re.compile("Inactive Date:"))
                    inactive_date_td = inactive_date_el.find_next('td') if inactive_date_el else ''
                    data['inactive_date'] = inactive_date_td.find('strong').text.strip().replace("/","-")
                except:
                    data['inactive_date'] = ""
                principal_office_address_el = soup.find("td", string="Principal Office Address:")
                data['address'] =  principal_office_address_el.find_next('strong').text.strip().replace("'", "''") if principal_office_address_el and principal_office_address_el.find_next('strong').text != 'NONE' else ''

                original_formation_el = soup.find("td", string=re.compile("Original Formation Date:")) if soup.find("td", string=re.compile("Original Formation Date:")) else ''
                original_formation_date_td = original_formation_el.find_next('td') if original_formation_el else ''
                data['formation_date'] = original_formation_date_td.find('strong').text.strip().replace("/", "-") if original_formation_date_td and original_formation_date_td.find('strong') else ''

                expiration_date_el = soup.find("td", string=re.compile("Expiration Date:"))
                data['expiration_date'] = expiration_date_el.find_next('strong').text.strip() if expiration_date_el else ''

                jurisdiction_formation_el = soup.find("td", string="Jurisdiction of Formation:")
                data['jurisdiction'] = jurisdiction_formation_el.find_next('strong').text.strip().replace("'", "''") if jurisdiction_formation_el else ''

                report_due_date_el = soup.find("td", string=re.compile("Business Entity Report Due Date:"))
                data['report_due_date'] = report_due_date_el.find_next('strong').text.strip() if report_due_date_el else ''
                
                years_due_el = soup.find("td", string=re.compile("Years Due:"))
                data['years_due'] = years_due_el.find_next('strong').text.strip().replace("\n", '') if years_due_el else ''

            
                incorporator_table = soup.find('table', id="grid_incorporatoslist") if soup.find('table', id="grid_incorporatoslist") else None
                if incorporator_table:
                    get_incorporate_people(incorporator_table)
                    hdnTotalPgCounts = soup.find_all('input', {'name': 'hdnTotalPgCount'})

                    if len(hdnTotalPgCounts) > 0:
                        incorporate_total_page_count = int(hdnTotalPgCounts[0]['value']) if hdnTotalPgCounts[0] else 0
                        if incorporate_total_page_count > 1:
                            incorporate_people_pagination(incorporate_total_page_count, businessid, cfbm_cookies, session_id, request_verification_token, cookies)
            
                governing_table = soup.find('table', id="grid_principalList") if soup.find('table', id="grid_principalList") else None
                if governing_table:
                    get_governing_people(governing_table)
                    hdnTotalPgCounts = soup.find_all('input', {'name': 'hdnTotalPgCount'})
                    if len(hdnTotalPgCounts) > 1:
                        governing_total_page_count = int(hdnTotalPgCounts[1]['value']) if hdnTotalPgCounts[1] else 0
                        if governing_total_page_count > 1:
                            governing_people_pagination(governing_total_page_count, businessid, cfbm_cookies, session_id, request_verification_token, cookies)
                    else:
                        governing_total_page_count = int(hdnTotalPgCounts[0]['value']) if hdnTotalPgCounts[0] else 0
                        if governing_total_page_count > 1:
                            governing_people_pagination(governing_total_page_count, businessid, cfbm_cookies, session_id, request_verification_token, cookies)
                        

                registered_agent = soup.find('td', string='Registered Agent Information')

                if registered_agent:
                    registered_agent_obj = dict()
                    registered_agent_type_el = registered_agent.find_next("td", string=re.compile('Type:'))
                    registered_agent_name_el = registered_agent.find_next("td",string=re.compile('Name:'))
                    registered_agent_obj['name'] = registered_agent_name_el.find_next('td').text.strip().replace("'", "''") if registered_agent_name_el else ''
                    registered_agent_obj['designation'] = 'registered_agent'
                    registered_agent_address_el = registered_agent.find_next("td",string=re.compile('Address:'))
                    registered_agent_obj['address'] = registered_agent_address_el.find_next('td').text.strip().replace("'", "''") if registered_agent_address_el else ''
                    registered_agent_obj['meta_detail'] = {
                        'entity_type': registered_agent_type_el.find_next('td').text.strip().replace("'", "''")
                    }
                    people_list.append(registered_agent_obj) if registered_agent_obj['name'] != '' else ''
                        
                url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessFilings'
                filing_body = f"businessId={businessid}&source="

                filing_detail_response, cfbm_cookies   = get_request_data(url, filing_body, cookies)
                filing_soup = BeautifulSoup(filing_detail_response.text, "html.parser")
                
                filing_table = filing_soup.find('table', id='xhtml_grid')
                filing_pagination_count_el = filing_soup.find('input', {'name': 'hdnTotalPgCount'})
                filing_page = int(filing_pagination_count_el['value']) if filing_pagination_count_el else 0

                if filing_table:
                    get_filing_data_from_table(filing_table)
                if filing_page > 1:
                    get_filling_history(filing_page, businessid, cfbm_cookies, session_id, request_verification_token, cookies)

                name_page_url = 'https://bsd.sos.in.gov/PublicBusinessSearch/BusinessNameHistory'
                name_body = f"businessId={businessid}&source="
            

                name_detail_response, cfbm_cookies = get_request_data(name_page_url, name_body, cookies)
                naming_soup = BeautifulSoup(name_detail_response.text, "html.parser")
                name_history_table = naming_soup.find('table', id='xhtml_grid')     

                naming_pagination_count_el = naming_soup.find('input', {'name': 'hdnTotalPgCount'})
                naming_page = int(naming_pagination_count_el['value']) if naming_pagination_count_el else 0

                if name_history_table:
                    get_naming_data(name_history_table)
                if naming_page > 1:
                    get_naming_history(naming_page, businessid, cfbm_cookies, session_id, request_verification_token, cookies)

                
                data['people_detail'] = people_list
                data['fillings_detail'] = fillings_detail
                data['previous_names_detail'] = previous_names_detail
                create(data, source_type, entity_type, country, category, url, name, description, v)
                with open('category_business_ids.txt', 'a') as file:
                    file.write(str(businessid) + '\n')
                    existing_business_ids.add(businessid)
   
  
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME, fillings_detail
        NOPECHA_KEY = os.getenv('NOPECHA_API_KEY2')
        
        # Set up the Selenium WebDriver (assuming you have the appropriate driver executable in your system PATH)
        options = Options()

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--headless=new')

        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        with open('ext.crx', 'wb') as f:
            f.write(requests.get('https://nopecha.com/f/ext.crx').content)
        options.add_extension('ext.crx')

        time.sleep(10)

        service = Service(ChromeDriverManager('114.0.5735.90').install())
        driver = webdriver.Chrome(service=service, options=options)
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Download the latest NopeCHA crx extension file.
        # You can also supply a path to a directory with unpacked extension files.
        time.sleep(20)
        print('extension added to ChromeDriverManager')
     
        # Set the subscription key for the extension by visiting this URL.
        driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY}")
    
        # selected_values = ["2", "34", "3", "4", "5", "6", "7", "8", "9", "39", "32", "10", "36", "11", "41", "14", "35", "15", "16", "17", "18", "19", "20", "21", "40", "33", "22", "37", "23", "42"]
        selected_values =['46', '45,46', '2', '34', '3', '4', '5', '6', '7', '8', '9', '39', '32', '10', '36', '11', '41', '14', '35', '15', '16', '17', '18', '19', '20', '21', '40', '33', '22', '37', '23', '42', '45']
        
        existing_values = set()
        with open('category_values.txt', 'r') as file:
            for line in file:
                existing_values.add(line.strip())

        for v in selected_values:

            if str(v) not in existing_values:
        
                driver.get(url)
                print("wait for solve captcha...")

                while True:
                    try:
                        iframe_element = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                        driver.switch_to.frame(iframe_element)
                        wait = WebDriverWait(driver, 10000)
                        print('trying to resolve captcha')
                        checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
                        print("Captcha has been Solved")
                        break
                    except TimeoutException:
                        print("Timed out waiting for the captcha to be resolved.")
                
                driver.switch_to.default_content()
                type_dropdown = Select(driver.find_element(By.ID, 'BusinessEntityType'))
                type_dropdown.select_by_value(v) 

                search_btn = driver.find_element(By.ID, 'btnSearch')
                search_btn.click()
                time.sleep(10)
                print("category value:", v)
                tota_page = int(driver.find_element(By.ID, 'hdnTotalPgCount').get_attribute("value"))
                get_data_from_table(driver,tota_page, source_type, entity_type, country, category, url, name, description,v)

                with open('category_values.txt', 'a') as file:
                    file.write(str(v) + '\n')
                    existing_values.add(v) 

                file_paths = ["category_pagination.txt", "category_anchors.txt"]
                for file_path in file_paths:
                    with open(file_path, mode='w') as file:
                        file.truncate()
       
        file_paths = ["category_values.txt", "category_business_ids.txt"]
        for file_path in file_paths:
            with open(file_path, mode='w') as file:
                file.truncate()
        return DATA_SIZE, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")
    

if __name__ == '__main__':
    '''
    Description: Crawler INBiz
    '''
    name = "INBiz"
    description = "INBiz, the state of Indiana''s one-stop resource for registering and managing  business and ensuring it complies with state laws and regulations. From registering business''s name to filing required paperwork, provides a streamlined and expedited process for business needs."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Indiana'
    category = 'Official Registry'
    url = "https://bsd.sos.in.gov/PublicBusinessSearch"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()