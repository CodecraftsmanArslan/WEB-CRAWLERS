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

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def googleTranslator(record_):
    """Description: This method is used to translate any language to english. It take name as input and return the translated name
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'","''").replace('\"',"")
        
    except:
        return record_

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

    industry_details = dict()
    industry_details['type'] = 'industry_details'
    industry_details['data'] = record[4]

    capital_details = dict()
    capital_details['type'] = 'capital_details'
    capital_details['data'] = record[10]

    shareholder_details = dict()
    shareholder_details['type'] = 'shareholder_details'
    shareholder_details['data'] = record[13]

    peoples_details = dict()
    peoples_details['type'] = 'peoples_details'
    peoples_details['data'] = record[14]

    investment_details = dict()
    investment_details['type'] = 'investment_details'
    investment_details['data'] = record[15]

    contact_details = dict()
    contact_details['type'] = 'contact_details'
    contact_details['data'] = record[16]

    news_announcement = dict()
    news_announcement['type'] = 'news_announcement'
    news_announcement['data'] = record[17]

    market_circulars = dict()
    market_circulars['type'] = 'market_circulars'
    market_circulars['data'] = record[18]

    major_shareholders = dict()
    major_shareholders['type'] = 'major_shareholders'
    major_shareholders['data'] = record[19]

    meta_details = dict()
    meta_details['director_official'] = googleTranslator(record[1].replace("'","''"))
    meta_details['industry_type'] = googleTranslator(record[2].replace("'","''"))
    meta_details["account_inspector"] = googleTranslator(record[11].replace("'","''"))
    meta_details["securities_number"] = googleTranslator(record[12].replace("'","''"))
    meta_details["sector"] = googleTranslator(record[3].replace("'","''"))
    meta_details["isin_code"] = googleTranslator(record[5].replace("'","''"))
    meta_details["incorporation_date"] = record[7].replace("'","''")
    meta_details["authorized_capital"] = googleTranslator(record[8].replace("'","''"))
    meta_details["paid_capital"] = googleTranslator(record[9].replace("'","''"))
    meta_details["registration_date"] = record[6].replace("'","''")
    meta_details['aliases'] = record[0].replace("'","''")

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": googleTranslator(record[0].replace("'","''")),
        "industry_details": [industry_details],
        "capital_details": [capital_details],
        "shareholder_details": [shareholder_details],
        "people_detail": [peoples_details],
        "investment_details": [investment_details],
        "additional_detail": [contact_details],
        "news_announcement": [news_announcement],
        "market_circulars": [market_circulars],
        "meta_details": meta_details,
        "major_shareholders": [major_shareholders],
        "status": "",
        "registration_number": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.syria.stock_market",
        "country_name": "Syria",
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}{url_}{record[5]}')) # entity_id
    data_for_db.append(googleTranslator(record[0].replace("'", ""))) #name
    data_for_db.append(json.dumps([record[7].replace("'","''")])) #dob
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
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the first table with the class 'mytable'
        table = soup.find_all('table', {'class': 'table table-striped table-bordered detail-view company-info-table'})
        # Extract all rows of the table
        rows = table[0].find_all('tr')
        # Extract the rows of the detail
        name_ = rows[0].find('td').text.strip()
        director_official = rows[1].find('td').text.strip()
        industry_type = rows[2].find('td').text.strip()
        sector = rows[4].find('td').text.strip()
        industry_details = [{ "industry_type": googleTranslator(industry_type), "sector": googleTranslator(sector)}]
        isin_code = rows[3].find('td').text.strip()
        registration_date = rows[5].find('td').text.strip()
        incorporation_date = rows[6].find('td').text.strip()
        authorized_capital = rows[7].find('td').text.strip()
        paid_capital =  rows[8].find('td').text.strip()
        capital_details = [{"authorized_capital": googleTranslator(authorized_capital), "paid_capital": googleTranslator(paid_capital)}]
        account_inspector = googleTranslator(rows[9].find('td').text.strip())
        securities_number = rows[10].find('td').text.strip()

        rows = table[1].find_all('tr')
        # Contact Details
        address_ = rows[0].find('td').text.strip()
        pobox_number_ = rows[1].find('td').text.strip()
        phone_number_ = rows[2].find('td').text.strip()
        fax_number_ = rows[3].find('td').text.strip()
        e_mail_ = rows[4].find('td').text.strip()
        website_ = rows[5].find('td').text.replace("'","''").strip()

        contact_details = [{
            "address": googleTranslator(address_),
            "pobox_number": pobox_number_,
            "phone_number": phone_number_,
            "fax_number": fax_number_,
            "e_mail": e_mail_,
            "website": website_
        }]

        table = soup.find('table', {'class': 'table table-striped table-bordered detail-view board-of-directors'})
        shareholder_details = []

        # Find all rows in the table
        rows = table.find_all('tr')

        # Define custom keys
        custom_keys = ['name', 'category', 'share_holder%']  # Customize the keys based on your requirements

        # Iterate over each row starting from the second row
        for row in rows[1:]:
            # Find all td and th elements in the row
            cells = row.find_all('td')
            
            shareholder_detail = {}
            # Assign custom keys to the cells
            for i in range(len(cells)):
                cell = cells[i]
                key = custom_keys[i] if i < len(custom_keys) else f'Key {i+1}'
                value = googleTranslator(cell.text.strip())
                # print(f'{key}: {value}')
                shareholder_detail[key]= value
            shareholder_details.append(shareholder_detail)

        # Find all tables with the specific class
        tables = soup.find_all('table', class_='table table-striped table-bordered detail-view board-of-directors')

        # Check if the second table exists
        if tables[1] in tables:
            second_table = tables[1]
            # Create an empty dictionary to store the table data
            peoples_details = []

            # Find all rows in the table
            rows = second_table.find_all('tr')

            # Define custom keys
            custom_keys = ['designation', 'name', 'corporate_member_representatives']  # Customize the keys based on your requirements

            # Iterate over each row starting from the second row
            for row in rows[1:]:
                # Find all td and th elements in the row
                cells = row.find_all(['td', 'th'])
                
                peoples_detail = {}
                # Assign custom keys to the cells
                for i in range(len(cells)):
                    cell = cells[i]
                    key = custom_keys[i] if i < len(custom_keys) else f'Key {i+1}'
                    value = googleTranslator(cell.text.strip())
                    peoples_detail[key] = value
                peoples_details.append(peoples_detail)
        else:
            print("No second table with the specified class found.")


        # Check if the second table exists
        investment_details = []
        if len(tables) > 2:
            investment_table = tables[2]
            # Create an empty dictionary to store the table data

            # Find all rows in the table
            rows = investment_table.find_all('tr')

            # Define custom keys
            custom_keys = ['name', 'number_of_shares_owned', 'percentage_ownership']  # Customize the keys based on your requirements

            # Iterate over each row starting from the second row
            for row in rows[1:]:
                # Find all td and th elements in the row
                cells = row.find_all(['td', 'th'])
                
                investment_detail = {}
                # Assign custom keys to the cells
                for i in range(len(cells)):
                    cell = cells[i]
                    key = custom_keys[i] if i < len(custom_keys) else f'Key {i+1}'
                    value = googleTranslator(cell.text.strip())
                    # print(f'{key}: {value}')
                    investment_detail[key] = value
                investment_details.append(investment_detail)

        # Find all div elements with the class "issuer-company-view-announcements"
        issuer_divs = soup.find_all('div', class_='issuer-company-view-announcements')

        # Check if the second div exists
        if len(issuer_divs) >= 2:
            news_announcement = []
            second_issuer_div = issuer_divs[1]   
            news_divs = second_issuer_div.find_all('div', class_='news-med')
            # Iterate over each div
            for div in news_divs:
                # Create a dictionary to store data for each iteration
                data = {}
                
                # Find elements within the div
                description_ = div.find('h3', class_='news-title')
                published_date = div.find('p', class_='date')
                source_url = div.find('a', href=True)
                
                # Store the data in the dictionary
                data['description'] = googleTranslator(description_.text.strip() if description_ else "")
                data['published_date'] = published_date.text.strip() if published_date else ""
                data['source_url'] = 'http://www.dse.sy' + source_url['href'] if source_url else None
                # Add the data dictionary to the list
                news_announcement.append(data)
        
         # Check if the second div exists
        if len(issuer_divs) >= 3:
            market_circulars = []
            second_issuer_div = issuer_divs[0]   
            news_divs = second_issuer_div.find_all('div', class_='news-med')
            # Iterate over each div
            for div in news_divs:
                # Create a dictionary to store data for each iteration
                data = {}
                
                # Find elements within the div
                description_ = div.find('h3', class_='news-title')
                published_date = div.find('p', class_='date')
                source_url = div.find('a', href=True)
                
                # Store the data in the dictionary
                data['description'] = googleTranslator(description_.text.strip() if description_ else "")
                data['published_date'] = published_date.text.strip() if published_date else ""
                data['source_url'] = 'http://www.dse.sy' + source_url['href'] if source_url else None
                # Add the data dictionary to the list
                market_circulars.append(data)

                
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
        # Get the page source after the button clicks
        html_content = driver.page_source
        # Close the Selenium WebDriver
        driver.quit()
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the table by ID
        table = soup.find('table', {'id': 'directors_ownership_report'})

        # Find all rows in the table
        rows = table.find_all('tr')

        # Define custom keys
        custom_keys = ['name', 'nationality', 'number_of_seats', 'property', 'percentage_ownership']  # Customize the keys based on your requirements
        major_shareholders = []
        # Iterate over each row starting from the second row
        for row in rows[1:]:
            data ={}
            tds = row.find_all('td')
            data['name'] = googleTranslator(tds[1].text.strip())
            data['nationality'] = googleTranslator(tds[2].text.strip())
            data['number_of_seats'] = tds[4].text.strip()
            data['property'] = tds[5].text.strip()
            data['percentage_ownership'] = tds[6].text.strip()
            major_shareholders.append(data)


        DATA = []
        DATA.append([
            name_,
            director_official,
            industry_type,
            sector,
            industry_details,
            isin_code,
            registration_date,
            incorporation_date,
            authorized_capital,
            paid_capital,
            capital_details,
            account_inspector,
            securities_number,
            shareholder_details,
            peoples_details,
            investment_details,
            contact_details,
            news_announcement,
            market_circulars,
            major_shareholders
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
    Description: API Crawler for Syria
    '''
    name = 'Damascus Securities Exchange (DSE)'
    description = "This is the website of the Damascus Securities Exchange (DSE) in Syria. It provides information on the issuer companies listed on the exchange."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Syria'
    category = 'Stock Market'
    urls = pd.read_csv(".//kyb/syria/input/output.csv")
    for url in urls.iterrows():
        url = url[1][0]
        print(url)
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
