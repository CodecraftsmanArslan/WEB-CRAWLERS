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

def get_listed_object(record, entity_type, category_, countries):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    3) Get FATF countries profiles descriptions from database and store them.
    
    @param record
    @param countries
    @param category_
    @param entity_type
    @return dict
    '''
    # preparing report details dictionary object
    report_details = dict()
    report_details['Name'] = [record[0].replace("'","''")]  
    report_details['Entity Type'] = [entity_type] 
    report_details['Category'] = [category_]  
    report_details['Country'] = [countries]  
    
    # preparing summary dictionary object
    summary = dict()  
    summary['Name'] = [record[0]]  
    summary['District'] = [record[1].replace("'","''")] 
    summary['Mobile'] = [record[2]]
    summary['Sector'] = [record[3]]
    summary['Sub Sector'] = [record[4]]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "Report Details": report_details,
        "Summary": summary
    }


    fatf_file_df = crawlers_functions.get_fatf()
    fatf_descriptions = []
    for index ,row in fatf_file_df.iterrows():
        if row['country_name'] == countries:
            fatf_descriptions.append(row['descriptions'])
    
    data_obj["FATF Profile"] = fatf_descriptions
    
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
    data_for_db.append(shortuuid.uuid(record[0]+url_)) # entity_id
    data_for_db.append(record[0].title().replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.upper()])) #category
    data_for_db.append(json.dumps([country.upper()])) #country
    data_for_db.append(entity_type.upper()) #entity_type
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
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        # Set the base URL and the range of page numbers to scrape
        page_range = range(53, 353)
        page_url = 'https://iade.gov.tl/enterprises/page/'
        # Create an empty list to store the scraped data
        data = []
        # Loop through the page range and scrape each page
        for page_number in page_range:
            # Construct the URL for the current page
            url_ = page_url + str(page_number) + "/?lang=en"
            print("Page:", page_number)
            # Send a GET request to the URL and parse the response using BeautifulSoup
            response = requests.get(url_)
            soup = BeautifulSoup(response.content, "html.parser")
            # Find the table element that contains the data
            table = soup.find("table", {"class": "table"})
            # Find all the rows in the table
            rows = table.find_all("tr")
            # Loop through the rows and extract the data
            for row in rows[1:]:
                cells = row.find_all("td")
                Title = cells[0].text.strip()
                District = cells[1].text.strip()
                Mobile = cells[2].text.strip()
                Sector = cells[3].text.strip()
                Sub_Sector = cells[4].text.strip()
                # Append the data to the list
                data.append([Title, District, Mobile, Sector, Sub_Sector])

            for record_ in data:
                record_for_db = prepare_data(record_, category,
                                                country, entity_type, source_type, name, url, description)
                            
                insertion_data, lang = crawlers_functions.check_language(
                    record_for_db, source_type, url, description, name)
        
                if lang == 'en':
                    crawlers_functions.language_handler(insertion_data, 'reports')
                    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
                else:
                    query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                        *insertion_data)
                
                if insertion_data[1].replace(' ', '') != '':
                    crawlers_functions.db_connection(query)

        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for East Timor
    '''
    name = 'Enterprise Directory of Timor-Leste'
    description = "Official website of Enterprise Directory of Timor-Leste, which is a small island nation located in Southeast Asia. The directory is maintained by the Investment and Export Promotion Agency of Timor-Leste (IADE), which is a government agency responsible for promoting investments and exports in the country. The directory includes a list of registered companies and businesses operating in Timor-Leste, as well as their contact information and business profile. "
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'East Timor'
    category = 'Company/SIE'
    url = 'https://iade.gov.tl/enterprise-directory/?lang=en'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
