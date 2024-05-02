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
    data_for_db.append(shortuuid.uuid(record['name']+page_link_+'custom_crawlers.bangladesh.chittagong_stock_exchange_cse')) # entity_id
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

        select_body = page_soup.find(
            'div', {'id': 'top_content_1'})
    
        pages = select_body.find_all("a")

        for page in pages:

            if '#' in page.get('href'):
                continue

            page_link = page.get("href")
            response = requests.get(page_link)
            STATUS_CODE  = response.status_code
            DATA_SIZE   = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            response = requests.get(page_link)

            page_data = BeautifulSoup(
                response.content, 'html.parser')

            company_name = page_data.find("div", class_="com_title")
            company_name = company_name.text.strip()

            pattern = re.compile("Trading Code:")
            trading_code_element = page_data.find("b", string=pattern) 
            trading_code = trading_code_element.find_next_sibling('b').text.strip()
            

            scrip_code_element = page_data.find("b", string="Scrip Code: ")
            scrip_code = scrip_code_element.find_next_sibling('b').text.strip()

            contact_information = page_data.find("strong", string="Contact Information")
            people_table = contact_information.findNext('table')
            people_rows = people_table.find('tr')
            cells = people_rows.find('td')
            table_data = cells.find('table')
            table_rows = table_data.find_all('tr')
            peoples = list()
            for row in table_rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:

                    people = dict()
                    people['designation'] = cells[0].text.strip().replace("'", "")
                    people['name'] = cells[1].text.strip().replace("'", "")
                    people['phone_number'] = cells[2].text.strip().replace("'", "")
                    people['email_address'] = cells[3].text.strip().replace("'", "")

                    peoples.append(people)

            address_element = page_data.find("b", string="Office Address ")
            address = address_element.parent.find('br').next_sibling.strip()


            factory_address_element = page_data.find("b", string=" Factory Address")
            factory_address = factory_address_element.parent.find('br').next_sibling.strip()

            phone_element = page_data.find("strong", string="Phone :")
            phone = phone_element.find_next_sibling('font').text.strip()

            fax_element = page_data.find("strong", string="Fax :")
            fax = fax_element.find_next_sibling('font').text.strip()

            email_element = page_data.find("strong", string="Email :")
            email = email_element.find_next_sibling('font').text.strip()

            website_element = page_data.find("strong", string="Website :")
            web = website_element.find_next_sibling('font').text.strip()

            authorized_capital_element = page_data.find("td", string="Authorized Capital in BDT* (mn) ")
            capital_element = authorized_capital_element.findNextSibling('td').text.strip() if authorized_capital_element is not None else ''
            
            paid_up_capital_element = page_data.find("td", string="Paid-up Capital in BDT* (mn)")
            paid_up_capital = paid_up_capital_element.findNextSibling('td').text.strip() if paid_up_capital_element is not None else ''

            sector_element = page_data.find("td", string="Sector")
            sector = sector_element.findNextSibling('td').text.strip()
        
            listing_element = page_data.find("td", string="Listing Year  ")
            listing_year = listing_element.findNextSibling('td').text.strip() if listing_element is not None else '' 

            week_range_element = page_data.find("td", string="52 Week's Range")
            week_range = week_range_element.findNextSibling('td').text.strip() if week_range_element is not None else '' 

            debut_trade_element = page_data.find("td", string="Debut Trade Date")
            debut_trade = debut_trade_element.findNextSibling('td').text.strip() if debut_trade_element is not None else '' 
            
            financial_statement_element = page_data.find("strong", string="Quarterly Financial Statement")
            financial_statement = financial_statement_element.find_next('td').text.strip() if financial_statement_element is not None else '' 

            data = dict()

            data['name'] = company_name.replace(
                "'", "''").strip()
            data['status'] = ''
            data['registration_number'] = ''
            data['registration_date'] = ''
            data['dissolution_date'] = ''
            data['type'] = ''
            data['crawler_name'] = 'custom_crawlers.bangladesh.chittagong_stock_exchange_cse'
            data['country_name'] = country
            data['company_fetched_data_status'] = ''


            meta_details = dict()

            if scrip_code:
                meta_details['scrip_code'] = scrip_code.replace("'","''")
            if trading_code:
                meta_details['trading_code'] = trading_code.replace("'","''")
            if week_range:
                meta_details['52_week_range'] = week_range.replace("'", "''")
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
            if debut_trade:
                meta_details['debut_trade'] = debut_trade.replace("'","''")
            
            addresses = list()

            if address:
                address_obj = dict()
                address_obj['type'] = 'address'
                address_obj['address'] = address.replace("'", "''")
                address_obj['description'] = ''
                address_obj['meta_detail'] = []
                addresses.append(address_obj)

            if factory_address and factory_address not in 'N/A':
                factory_obj = dict()
                factory_obj['type'] = 'factory_address'
                factory_obj['address'] = factory_address.replace("'", "''")
                factory_obj['description'] = ''
                factory_obj['meta_detail'] = []
                addresses.append(factory_obj)

            fillings_detail_list = list()
            if financial_statement:
                fillings_detail = dict()
                fillings_detail['Financial Statements'] = financial_statement.replace("'", "")
                fillings_detail_list.append(fillings_detail)

            data['addresses_detail'] = addresses
            data['fillings_detail'] = fillings_detail_list
            data['meta_detail'] = meta_details
            data['people_detail'] = peoples

            record_for_db = prepare_data(data, category,
                                            country, entity_type, source_type, name, url, description, page_link)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
           
            print("stored records")
           
            crawlers_functions.db_connection(query)

        return len(pages), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Bangladesh stock market
    '''
    name = 'Chittagong Stock Exchange (CSE)'
    description = "The Chittagong Stock Exchange (CSE) is one of the two stock exchanges in Bangladesh, alongside the Dhaka Stock Exchange. It is located in Chittagong, the second-largest city of the country. The CSE plays a vital role in facilitating securities trading and capital market activities."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Bangladesh'
    category = 'Stock Market'
    url = 'https://www.cse.com.bd/company/listedcompanies'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
