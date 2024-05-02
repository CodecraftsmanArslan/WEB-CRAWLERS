"""Set System Path"""
import re
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


def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, page_link_):
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
    data_for_db.append(shortuuid.uuid(record['name']+page_link_+'custom_crawlers.bangladesh.stock_market_dse')) # entity_id
    data_for_db.append(record['name'].replace("'", "")) #name
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url
        
        page_response = requests.get(url)

        page_soup = BeautifulSoup(
            page_response.content, 'html.parser')

        select_body = page_soup.find_all(
            'div', {'class': 'BodyContent'})

        pages = list()
        for body_content_div in select_body:
   
            pages += body_content_div.find_all("a")

        for page in pages:

            if 'href' not in page.attrs:
                continue
            href = page.get("href")

            page_link = 'https://www.dsebd.org/'+ href

            response = requests.get(page_link)
            STATUS_CODE  = response.status_code
            DATA_SIZE   = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            response = requests.get(page_link)

            page_data = BeautifulSoup(
                response.content, 'html.parser')

            company_name = page_data.find("h2", class_="BodyHead topBodyHead")
            company_name = company_name.text.strip().split(':')[-1]

            pattern = re.compile("Trading Code:")
            trading_code_element = page_data.find("strong", string=pattern) 
            trading_code = trading_code_element.parent.text.split(':')[1].strip()

            scrip_code_element = page_data.find("strong", string="Scrip Code:")
            scrip_code = scrip_code_element.parent.text.split(':')[1].strip()

            weeks_moving_range_element = page_data.find("th", string="52 Weeks' Moving Range")
            weeks_moving_range = weeks_moving_range_element.findNextSibling('td').text.strip()

            market_capitalization_element = page_data.find("th", string="Market Capitalization (mn)")
            market_capitalization = market_capitalization_element.findNextSibling('td').text.strip()

            authorized_capital_element = page_data.find("th", string="Authorized Capital (mn)")
            capital_element = authorized_capital_element.findNextSibling('td').text.strip() if authorized_capital_element is not None else ''

            sector_element = page_data.find("th", string="Sector")
            sector = sector_element.findNextSibling('td').text.strip()
            
            paid_up_capital_element = page_data.find("th", string="Paid-up Capital (mn)")
            paid_up_capital = paid_up_capital_element.findNextSibling('td').text.strip() if paid_up_capital_element is not None else ''

            listing_element = page_data.find("td", string="Listing Year")
            listing_year = listing_element.findNextSibling('td').text.strip() if listing_element is not None else '' 


            head_office_element = page_data.find("td", string="Head Office") 
            head_office = head_office_element.findNextSibling('td').text.strip() if head_office_element is not None else ''

            single_address_elemet = page_data.find("td", string="Address") 
            single_address = single_address_elemet.findNextSibling('td').text.strip() if single_address_elemet is not None else ''

            factory_element = page_data.find("td", string="Factory")
            factory = factory_element.findNextSibling('td').text.strip() if factory_element is not None else ''

            phone_element = page_data.find("td", string="Contact Phone") if page_data.find("td", string="Contact Phone") is not None else page_data.find("td", string="Telephone No.")
            phone = phone_element.findNextSibling('td').text.strip()

    
            fax_element = page_data.find("td", string="Fax")
            fax = fax_element.findNextSibling('td').text.strip() if fax_element is not None else ''

            email_element = page_data.find("td", string="E-mail")
            email = email_element.findNextSibling('td').text.strip()

            web_element = page_data.find("td", string="Web Address") if  page_data.find("td", string="Web Address") is not None else  page_data.find("td", string="Website")
            web = web_element.findNextSibling('td').text.strip() if web_element is not None else ''

            data = dict()

            data['name'] = company_name.replace(
                "'", "''").strip() if company_name is not None else ''
            data['status'] = ''
            data['registration_number'] = ''
            data['registration_date'] = ''
            data['dissolution_date'] = ''
            data['type'] = ''
            data['crawler_name'] = 'custom_crawlers.bangladesh.stock_market_dsc'
            data['country_name'] = country
            data['company_fetched_data_status'] = ''


            meta_details = dict()

            if scrip_code:
                meta_details['scrip_code'] = scrip_code.replace("'","''")
            if trading_code:
                meta_details['trading_code'] = trading_code.replace("'","''")
            if weeks_moving_range:
                meta_details['52_week_range'] = weeks_moving_range.replace("'", "''")
            if market_capitalization:
                meta_details['market_capitalization_(mn)'] = market_capitalization.replace("'", "''")
            if capital_element:
                meta_details['authorized_capital_(mn)'] = capital_element.replace("'", "''")
            if sector:
                meta_details['industry_type'] = sector.replace("'","''")
            if paid_up_capital:
                meta_details['paid_up_capital_(mn)'] = paid_up_capital.replace("'", "''")
            if listing_year:
                meta_details['listing_date'] = listing_year
            if phone:
                meta_details['phone_number'] = phone.replace("'","''")
            if fax:
                meta_details['fax_number'] = fax.replace("'","''")
            if email:
                meta_details['email_address'] = email.replace("'","''")
            if web:
                meta_details['internet_address'] = web.replace("'","''")
            

            addresses = list()

            if head_office and head_office not in 'N/A':
                address_obj = dict()
                address_obj['type'] = 'head_office_address'
                address_obj['address'] = head_office.replace("'", "''")
                address_obj['description'] = ''
                address_obj['meta_detail'] = []
                addresses.append(address_obj)

            if factory and factory not in 'N/A':
                factory_obj = dict()
                factory_obj['type'] = 'factory_address'
                factory_obj['address'] = factory.replace("'", "''")
                factory_obj['description'] = ''
                factory_obj['meta_detail'] = []
                addresses.append(factory_obj)

            if single_address and single_address not in 'Head Office':
                single_address_obj = dict()
                single_address_obj['type'] = 'address'
                single_address_obj['address'] = single_address.replace("'", "''")
                single_address_obj['description'] = ''
                single_address_obj['meta_detail'] = []
                addresses.append(single_address_obj)


            people_name_element = page_data.find("td", string="Company Secretary Name")
            people_name = people_name_element.findNextSibling('td').text.strip() if people_name_element is not None else ''

            cell_no_element = page_data.find("td", string="Cell No.")
            cell_no = cell_no_element.findNextSibling('td').text.strip() if cell_no_element is not None else ''

            phone_no_element = page_data.find("td", string="Telephone No.")
            phone_no = phone_no_element.findNextSibling('td').text.strip() if phone_no_element is not None else ''

            p_email_element = page_data.find_all("td", string="E-mail") if len(page_data.find_all("td", string="E-mail")) > 1 else None


            p_email = p_email_element[1].findNextSibling('td').text.strip() if p_email_element is not None else '' 

            people = list()
            if people_name:
                people_object = dict()
                people_object['type'] = 'people_detail'

                people_data = dict()
                people_data['secretary_name'] = people_name.replace("'","''")
                people_data['cell_number'] = cell_no.replace("'","''")
                people_data['phone_number'] = phone_no.replace("'","''")
                people_data['email_address'] = p_email.replace("'","''")
                people_object['data'] = people_data
                people.append(people_object)
                


            data['additional_detail'] = []
            data['addresses_detail'] = addresses
            data['fillings_detail'] = []
            data['meta_detail'] = meta_details
            data['people_detail'] = people
            

            record_for_db = prepare_data(data, category,
                                            country, entity_type, source_type, name, url, description, page_link)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
           
            print("stored records")
           
            crawlers_functions.db_connection(query)

        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Bangladesh stock market
    '''
    name = 'Dhaka Stock Exchange (DSE)'
    description = "The Dhaka Stock Exchange (DSE) is the main stock exchange in Bangladesh. It plays a crucial role in the country's capital market, facilitating the trading of securities and serving as a platform for companies to raise capital."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Bangladesh'
    category = 'Stock Market'
    url = 'https://www.dsebd.org/company_listing.php'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
