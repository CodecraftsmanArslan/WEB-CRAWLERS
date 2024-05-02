"""Set System Path"""
import sys
from pathlib import Path
import zipfile
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import pandas as pd
import shortuuid,time
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import zipfile, wget
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from dateutil import parser

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

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

def make_request(url, headers, timeout):
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout, verify=False)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except:
            time.sleep(10*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')

    print(f'Failed to make request after {max_retries} retries.')
    return None

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    
    @param record
    @return dict
    '''

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[0].replace("'","''"),
        "status": record[2].replace("'","").replace("  ", "").replace("\n",""),
        "registration_number": record[1],
        "dissolution_date": record[3],
        "type": record[4].replace("'","''"),
        "incorporation_date":format_date(str(pd.to_datetime(record[5]))),
        "crawler_name": "crawlers.custom_crawlers.kyb.united_kingdom.united_kingdom_kyb",
        "country_name": "United Kingdom",
        "previous_names_detail": record[6],
        "fillings_detail":record[7],
        "people_detail":record[8],
        "additional_detail":record[9],
        "addresses_detail":record[10],
        "announcements_detail":record[11]
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
    data_for_db.append(shortuuid.uuid(f'{record[1]}-{url_}-united_kingdom_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[5]))])) #dob
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

def download_and_extract_zip(url, output_folder):
    print("Downloading!")
    if not os.path.exists(f'{output_folder}/companies_data.zip'):
        wget.download(url,f'{output_folder}/companies_data.zip')
    with zipfile.ZipFile(f'{output_folder}/companies_data.zip', 'r') as zip_ref:
        csv_file = None
        for file_name in zip_ref.namelist():
            if file_name.endswith(".csv"):
                csv_file = file_name
                break
        if csv_file:
            zip_ref.extract(csv_file, path="input/")
            os.rename(f'{output_folder}/{csv_file}', f'{output_folder}/{"data.csv"}')
    print("Extracted!")

def get_announcement_details(BASE_URL, company_no):
    announcement_url = "{}/charges".format(company_no)
    announcement_response = make_request(BASE_URL.format(announcement_url), {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 200)
    announcement_details = []
    soup_announcement = BeautifulSoup(announcement_response.content, 'html.parser')

    announcements = soup_announcement.find("div", {"id":"mortgage-content"})
    if not announcements:
        return announcement_details
    if not announcements.find_all("div"):
        return announcement_details
    for each in announcements.find_all("div"):
        if 'mortgage-' in str(each).lower():
            if not each.find("h2"):
                continue
            dummy = {'name':each.find("h2").find('a').text.strip().replace("'", ""), 'source_url':BASE_URL.format(each.find("h2").find('a').get('href')),
                    'creation_date':'', 'delivered_date':'', 'status':'', 'persons_entitled':[], 'short_particulars':''}
            for items in each.find_all("dl"):
                if 'Created' in str(items.find("dt")).lower():
                    dummy["creation_date"] = items.find("dd").text.strip().replace("'", "")
                elif 'Delivered' in str(items.find("dt")).lower():
                    dummy["delivered_date"] = items.find("dd").text.strip().replace("'", "")
                elif 'Status' in str(items.find("dt")).lower():
                    dummy["status"] = items.find("dd").text.strip().replace("'", "")
            
            persons_entitled = soup_announcement.find("h3", string="Persons entitled").find_next().find_all("li") if soup_announcement.find("h3", string="Persons entitled") else ""
            for persons_ in persons_entitled:
                dummy["persons_entitled"] = persons_.text.strip().replace("'", "")

            dummy["short_particulars"] = soup_announcement.find('h3', string="Short particulars").find_next().text.replace("...",".").strip().replace("'", "") if soup_announcement.find('h3', string="Short particulars") else ""
            if dummy["name"] is not None and dummy["name"] != "":
                meta_detail = {
                    "source_url":dummy["source_url"],
                    "creation_date":dummy["creation_date"],
                    "delivered_date":dummy["delivered_date"],
                    "status":dummy["status"],
                    "persons_entitled":dummy["persons_entitled"],
                    "short_particulars":dummy["short_particulars"]
                }
                meta_detail = {key: value for key, value in meta_detail.items() if value and (not isinstance(value, list) or len(value) > 0)}
                announcement_details.append({
                    "title":dummy["name"],
                    "meta_detail": meta_detail
                })

    return announcement_details

def get_beneficial_owners(BASE_URL, company_no):
    beneficials_url = "{}/persons-with-significant-control".format(company_no)
    beneficials_response = make_request(BASE_URL.format(beneficials_url), {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 200)
    beneficials_details = []
    soup_beneficials = BeautifulSoup(beneficials_response.content, 'html.parser')

    beneficieries = soup_beneficials.find("p", {"id":"company-pscs"})
    if not beneficieries:
        return beneficials_details
    if not beneficieries.find_next_sibling("div"):
        return beneficials_details
    for each in beneficieries.find_next_sibling("div"):
        if 'appointment-' in str(each).lower():
            if not each.find("b"):
                continue
            dummy = {'name':each.find("b").text.strip().replace("'", ""), 'correspondence_address':each.find("dd").text.strip().replace("'", ""),
                    'notified_date':'', 'nature_of_control':'', 'governing_law':'', 'legal_form':'', 'principal_office_address':''}
            for items in each.find_all("dl"):
                if 'notified on' in str(items.find("dt")).lower():
                    dummy['notified_date'] = format_date(items.find("dd").text.strip().replace("'", ""))
                elif '' in str(items.find("dt")).lower():
                    dummy['country_of_residence'] = items.find("dd").text.strip().replace("'", "")
                elif 'governing law' in str(items.find("dt")).lower():
                    dummy['governing_law'] = items.find("dd").text.strip().replace("'", "")
                elif 'legal form' in str(items.find("dt")).lower():
                    dummy['legal_form'] = items.find("dd").text.strip().replace("'", "")
                elif 'principal office address' in str(items.find("dt")).lower():
                    dummy['principal_office_address'] = items.find("dd").text.strip().replace("'", "")
                elif 'nature of control' in str(items.find("dt")).lower():
                    dummy['nature_of_control'] = [it.text.strip().replace("'", "") for it in items.find_all('dd')]
            beneficials_details.append(dummy)

    return beneficials_details

def get_people_details(BASE_URL, company_no):
    people_url = "{}/officers".format(company_no)
    people_response = make_request(BASE_URL.format(people_url), {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 200)
    people_details = []
    soup_people = BeautifulSoup(people_response.content, 'html.parser')

    appointments = soup_people.find("h2", {"id":"company-appointments"})
    if not appointments:
        return people_details
    if not appointments.find_next_sibling("div"):
        return people_details
    for each in appointments.find_next_sibling("div"):
        if 'appointment-' in str(each).lower():
            dummy = {'name':each.find("h2").text.strip().replace("'", ""), 'correspondence_address':each.find("dd").text.strip().replace("'", ""),
                    'role':'', 'date_of_birth':'', 'date_of_appointment':'', 'nationality':'', 'country_of_residence':'', 'occupation':'',
                     'date_of_resignation':'', 'place_registered':'', 'governing_law':'', 'legal_form':''}
            for items in each.find_all("dl"):
                if 'role' in str(items.find("dt")).lower():
                    dummy['role'] = items.find("dd").text.strip().replace("'", "")
                elif 'date of birth' in str(items.find("dt")).lower():
                    dummy['date_of_birth'] = items.find("dd").text.strip().replace("'", "")
                elif 'appointed on' in str(items.find("dt")).lower():
                    dummy['date_of_appointment'] = items.find("dd").text.strip().replace("'", "")
                elif 'governing law' in str(items.find("dt")).lower():
                    dummy['governing_law'] = items.find("dd").text.strip().replace("'", "")
                elif 'place registered' in str(items.find("dt")).lower():
                    dummy['place_registered'] = items.find("dd").text.strip().replace("'", "")
                elif 'resigned on' in str(items.find("dt")).lower():
                    dummy['date_of_resignation'] = items.find("dd").text.strip().replace("'", "")
                elif 'nationality' in str(items.find("dt")).lower():
                    dummy['nationality'] = items.find("dd").text.strip().replace("'", "")
                elif 'legal form' in str(items.find("dt")).lower():
                    dummy['legal_form'] = items.find("dd").text.strip().replace("'", "")
                elif 'country of residence' in str(items.find("dt")).lower():
                    dummy['country_of_residence'] = items.find("dd").text.strip().replace("'", "")
                elif 'occupation' in str(items.find("dt")).lower():
                    dummy['occupation'] = items.find("dd").text.strip().replace("'", "").replace("None","")
            
           
            if dummy["name"] is not None and dummy["name"] != "":
                meta_detail = {
                    "date_of_birth": dummy["date_of_birth"],
                    "residence_country": dummy["country_of_residence"],
                    "occupation": dummy["occupation"],
                    "law_goverened": dummy["governing_law"],
                    "legal_form": dummy["legal_form"],
                    "place_registered": dummy["place_registered"]
                }
                meta_detail = {key: value for key, value in meta_detail.items() if value}
                
                people_details.append({
                    "name": dummy["name"],
                    "address": dummy["correspondence_address"],
                    "designation": dummy["role"],
                    "appointment_date": format_date(dummy["date_of_appointment"]),
                    "termination_date": format_date(dummy["date_of_resignation"]),
                    "nationality": dummy["nationality"],
                    "meta_detail": meta_detail
                })

    return people_details

def get_filing_details(BASE_URL, company_no):
    filing_url = "{}/filing-history".format(company_no)
    filing_response = make_request(BASE_URL.format(filing_url), {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 200)
    keys_response = make_request("https://wck2.companieshouse.gov.uk/goWCK/help/en/stdwc/doccodes_ch.html", {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 60)
    
    keys_soup = BeautifulSoup(keys_response.content, 'html.parser')
    
    filing_details = []
    if filing_response is not None:
        soup_filing = BeautifulSoup(filing_response.content, 'html.parser')
    else:
        return filing_details

    if not soup_filing.find('table'):
        return filing_details
    if not soup_filing.find('table').find_all('tr')[1:]:
        return filing_details
    table = soup_filing.find('table')
    for row in table.find_all('tr')[1:]:
        column = row.find_all('td')
        date = column[0].text.strip().replace("'","")
        key = column[1].text.strip().replace("'","").replace("(","").replace(")","")
        title = column[2].find('strong').text.strip().replace("'","") if column[2].find('strong') else ""
        description = column[2].find('ul').text.strip().replace("'","").replace("\n", "").replace("  ", "") if column[2].find('ul') else ""
        source_url = "https://find-and-update.company-information.service.gov.uk/"+column[3].find("a")['href'] if column[3].find("a") else ""
        
        try:
            key_value = keys_soup.select_one("td:contains({})".format(key)).find_next().text.strip().replace("'","") if keys_soup.select_one("td:contains({})".format(key)) else ""
        except:
            key_value = ""

        filing_details.append({"date":format_date(date), "description":description, "filing_code":key, "filing_type": key_value, "file_url": source_url, "title":title})

    return filing_details

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

        BASE_URL = "https://find-and-update.company-information.service.gov.uk/company/{}"

        print("Loading CSV!")
        df = pd.read_csv("input/data.csv")
        df = df.rename(columns=lambda x: x.strip())
        company_numbers = df['CompanyNumber'].values
        print("CSV Loaded!")
        
        DATA = []
        for company_no in company_numbers:
            print(BASE_URL.format(company_no))
        
            additional_detail = []
            addresses_detail = []

            response = make_request(BASE_URL.format(company_no), {
                    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, 200)

            STATUS_CODE = response.status_code
            soup = BeautifulSoup(response.content, 'html.parser')

            company_name = soup.select_one("#content-container > div.company-header > p.heading-xlarge").string.strip().replace("'", "").replace('\"','"') if soup.select_one("#content-container > div.company-header > p.heading-xlarge") else ""
            company_reg_no = soup.select_one("#company-number > strong").string.strip().replace("'", "") if soup.select_one("#company-number > strong") else ""

            if company_name == "" and company_reg_no == "":
                continue

            general_address = soup.find('dt', string='Registered office address').find_next('dd').text.strip().replace("'", "") if soup.find('dt', string='Registered office address') else ""
            if general_address is not None and general_address !="":
                addresses_detail.append({"address": general_address, "type": "general_address"})

            company_status = soup.find('dt', string='Company status').find_next('dd').text.strip().replace("'", "") if soup.find('dt', string='Company status') else ""
            company_type = soup.find('dt', string='Company type').find_next('dd').text.strip().replace("'", "") if soup.find('dt', string='Company type') else ""
            incorporated_date = soup.find('dt', string='Incorporated on').find_next('dd').text.strip().replace("'", "") if soup.find('dt', string='Incorporated on') else ""
            dissolution_date = soup.find('dt', string='Dissolved on').find_next('dd').text.strip().replace("'", "") if soup.find('dt', string='Dissolved on') else ""
            
            overseas_entity_address = soup.find("dt", string="Overseas entity address").find_next().text.strip().replace("'", "") if soup.find("dt", string="Overseas entity address") else ""
            if overseas_entity_address != "" and overseas_entity_address is not None:
                addresses_detail.append({"address": overseas_entity_address, "type": "overseas_entity_address"})

            incorporation_country = soup.find("dt", string="Incorporated in").find_next().text.strip().replace("'", "") if soup.find("dt", string="Incorporated in") else ""
            legal_form = soup.find("dt", string="Legal form ").find_next().text.strip().replace("'", "") if soup.find("dt", string="Legal form ") else ""
            governing_law = soup.find("dt", string="Governing law").find_next().text.strip().replace("'", "") if soup.find("dt", string="Governing law") else ""
            incorporation_reg_no = soup.find("dt", string="Registration number").find_next().text.strip().replace("'", "") if soup.find("dt", string="Registration number") else ""
            parent_registry = soup.find("dt", string="Parent registry").find_next().text.strip().replace("'", "") if soup.find("dt", string="Parent registry") else ""

            if incorporation_country != "" and legal_form != "" and governing_law != "" and incorporation_reg_no != "" and parent_registry != "":
                incorporation_country_details = {'incorporation_country':incorporation_country, 'legal_form':legal_form, 'governing_law':governing_law,
                                        'registration_number':incorporation_reg_no, 'parent_registry':parent_registry}

                additional_detail.append({"type":"incorporation_country_details", "data":[incorporation_country_details]})

            previous_names_details = []
            if soup.find("h2", string="  Previous company names "):
                previous_name = soup.find("h2", string="  Previous company names ").find_next('table').find_all('tr')
                for ea in previous_name[1:]:
                    vals = [td.text.strip().replace("'", "") for td in ea.find_all('td')]
                    previous_names_details.append({"name": vals[0], "update_date": "", "meta_detail":{"period":vals[1].replace("\n", "").replace("  ", "") if vals[1] is not None else ""}})


            next_due_date, next_annual_statement_made_date, last_annual_statement_made_date = "", "", ""
            next_annual_statement_due_date, first_annual_statement_made_date = "", ""
            if soup.find("strong", string="Annual statement"):
                annual_statement = soup.find("strong", string="Annual statement").find_parent().find_next('p')
                if 'next' in str(annual_statement).lower():
                    if 'due' in str(annual_statement).lower():
                        next_annual_statement_made_date = annual_statement.find_all('strong')[0].text.strip().replace("'", "")
                        next_annual_statement_due_date = annual_statement.find_all('strong')[1].text.strip().replace("'", "")
                    else:
                        next_annual_statement_made_date = annual_statement.find_all('strong')[0].text.strip().replace("'", "")
                        next_annual_statement_due_date = ""
                elif 'last' in str(annual_statement).lower():
                    last_annual_statement_made_date = annual_statement.find('strong').text.strip().replace("'", "")
                elif 'first' in str(annual_statement).lower():
                    if 'due' in str(annual_statement).lower():
                        first_annual_statement_made_date = annual_statement.find_all('strong')[0].text.strip().replace("'", "")
                        next_due_date = annual_statement.find_all('strong')[1].text.strip().replace("'", "")
                    else:
                        first_annual_statement_made_date = annual_statement.find_all('strong')[0].text.strip().replace("'", "")
                        next_due_date = ""
                
                final_annual_statement = {"next_annual_statement_made_date":format_date(next_annual_statement_made_date), "next_annual_statement_due_date":format_date(next_annual_statement_due_date),
                                    "first_annual_statement_made_date":format_date(first_annual_statement_made_date), "next_due_date":format_date(next_due_date),
                                    "last_annual_statement_made_date":format_date(last_annual_statement_made_date)}
                
                additional_detail.append({"type":"annual_statement", "data":[final_annual_statement]})

            details = soup.select("div.govuk-tabs__panel div.column-half")
            account_details, confirmation_statement_details = [], []
            next_account_made_date = ""
            next_account_due_date = ""
            last_account_made_date = ""
            first_account_made_date = ""
            next_due_date = ""
            for item in details:
                dates = item.select("p")
                for date in dates:
                    if 'next' in str(date).lower():
                        if 'due' in str(date).lower():
                            next_account_made_date = date.find_all('strong')[0].text.strip().replace("'", "")
                            next_account_due_date = date.find_all('strong')[1].text.strip().replace("'", "")
                        else:
                            next_account_made_date = date.find_all('strong')[0].text.strip().replace("'", "")
                            next_account_due_date = ""
                    elif 'last' in str(date).lower():
                        last_account_made_date = date.find('strong').text.strip().replace("'", "")
                    elif 'first' in str(date).lower():
                        if 'due' in str(date).lower():
                            first_account_made_date = date.find_all('strong')[0].text.strip().replace("'", "")
                            next_due_date = date.find_all('strong')[1].text.strip().replace("'", "")
                        else:
                            first_account_made_date = date.find_all('strong')[0].text.strip().replace("'", "")
                            next_due_date = ""

                if item.find("h2"):
                    if 'account' in str(item.find("h2").string).lower(): 
                        account_details.append({'first_account_made_date':format_date(first_account_made_date), 'next_due_date':format_date(next_due_date), 
                                        'next_account_made_date':format_date(next_account_made_date), 'next_account_due_date':format_date(next_account_due_date), 
                                        'last_account_made_date':format_date(last_account_made_date)}) 
                    if 'confirmation statement' in str(item.find("h2").string).lower(): 
                        confirmation_statement_details.append({'first_account_made_date': format_date(first_account_made_date), 'next_due_date': format_date(next_due_date),
                                                    'next_confirmation_statement_made_date': format_date(next_account_made_date), 'next_confirmation_statement_due_date': format_date(next_account_due_date), 
                                                    'last_confirmation_statement_made_date': format_date(last_account_made_date)})
                        

            if account_details:
                additional_detail.append({"type":"account_details", "data":account_details})
            if confirmation_statement_details:
                additional_detail.append({"type":"statement_details", "data":confirmation_statement_details})

            sic = soup.find("h2",{"id":"sic-title"})
            sic_codes = []
            if sic:
                sic_ul = sic.find_next()
                for item in sic_ul.find_all('li'):
                    sic_codes.append({"code": item.text.strip().replace("'", "")})
                
                additional_detail.append({"type":"SIC_codes", "data":sic_codes})


            filling_details = get_filing_details(BASE_URL, company_no)
            people_details = get_people_details(BASE_URL, company_no)

            beneficial_owner_details = get_beneficial_owners(BASE_URL, company_no)
            additional_detail.append({"type":"beneficial_owners", "data":beneficial_owner_details})

            announcements_details = get_announcement_details(BASE_URL, company_no)

            record = [company_name, company_reg_no, company_status, dissolution_date, company_type, incorporated_date, previous_names_details,
                    filling_details, people_details, additional_detail, addresses_detail, announcements_details]
            
            DATA.append(record)
            record_for_db = prepare_data(record, category,
                                            country, entity_type, source_type, name, url, description)
                        
            insertion_data, lang = crawlers_functions.check_language(
                record_for_db, source_type, url, description, name)
    
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
            
            print("Stored record")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e, tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for United Kingdom
    '''
    name = 'Companies House United Kingdom'
    description = "Official data portal provided by the Companies House in the United Kingdom. The portal provides access to various datasets containing information about businesses and individuals registered with the Companies House. The datasets include basic company data, company accounts data, and company officer data."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'United Kingdom'
    category = 'Official Registry'
    url = "https://find-and-update.company-information.service.gov.uk/"

    ZIP_FILE_URL = "https://download.companieshouse.gov.uk/BasicCompanyDataAsOneFile-2023-12-04.zip"

    download_and_extract_zip(ZIP_FILE_URL, "input/")

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()