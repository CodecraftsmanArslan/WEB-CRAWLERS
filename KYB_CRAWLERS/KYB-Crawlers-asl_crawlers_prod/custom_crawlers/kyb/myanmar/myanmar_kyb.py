"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import camelot
import pandas as pd
import shortuuid,time
import requests, json, os, csv
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from bs4 import BeautifulSoup

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def update_csv():
    counter = 0
    urls = []
    while True:
        url = f"https://www.dica.gov.mm/en/topic/details-daily-registered-companies?page={counter}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            td_elements = soup.find_all('td', {'class': 'views-field-title'})
            if len(td_elements) == 0:
                break
            for td in td_elements:
                a_element = td.find('a')
                if a_element:
                    href = a_element.get('href')
                    urls.append(href)
        counter += 1

    with open('kyb/myanmar/urls.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for url in urls:
            writer.writerow([url])

    print("CSV File Updated.")


def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    @param record
    @return dict
    '''
    
    # preparing meta_detail dictionary object
    meta_detail = dict()   
    
    # create data object dictionary containing all above dictionaries
    try:
        registration_number = record['Registration Number']
    except:
        registration_number = record['Registration \nNumber']
    
    try:
        compnay_name = record['Company Name']
    except:
        compnay_name = record['Unnamed: 1']
    try:
        approve = record['Approve Time']
    except:
        approve = record['Approve \nTime']
    
    data_obj = {
        "name": compnay_name.replace("'","''"),
        "status": "",
        "registration_number": registration_number,
        "registration_date": approve,
        "dissolution_date": "",
        "type": record['Company Type'].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.myanmar.myanmar_kyb",
        "country_name": "Myanmar",
        "company_fetched_data_status": "",
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
    try:
        registration_number = record['Registration Number']
    except:
        registration_number = record['Registration \nNumber']
    try:
        sr = record['Sr']
    except:
        sr = record['Unnamed: 2']
    try:
        compnay_name = record['Company Name']
    except:
        compnay_name = record['Unnamed: 1']
    
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(str(registration_number)+'myanmar_kyb')) # entity_id
    data_for_db.append(compnay_name.replace("'", "")) #name
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
        FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts/'
        SOURCE_URL = url
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        FILENAME = 'myanmar/'+url.split('/')[-1]
        
        with open(f'{FILE_PATH}{FILENAME}', 'wb') as f:
            f.write(response.content)

        file_path = os.path.join(f'{FILE_PATH}{FILENAME}')
        
        tables = camelot.read_pdf(file_path, pages= 'all', split_text=True, flag_size=True)
        os.remove(file_path)
        
        current_table_df = tables[0].df
        all_tables_df = current_table_df

        # 2. loop through each page to append all tables into one all tables dataframe (all_tables_df)
        for table in tables:
            # convert current table into df
            current_table_df = table.df
            all_tables_df = pd.concat(
                [all_tables_df, current_table_df], ignore_index=True)

        # 3. check if the columns of pd has all integers then remove the columns
        # And replace it with first row as column/header
        is_all_integers_in_col = all(str(x).isdigit for x in list(all_tables_df.columns.values))
        if is_all_integers_in_col:
            # grab the first row for the header
            new_header = all_tables_df.iloc[0]
            # take the data less the header row
            all_tables_df = all_tables_df[1:]
            all_tables_df.columns = new_header
            
        all_tables_df = all_tables_df.loc[all_tables_df['Sr'] != 'Sr']
        all_tables_df.replace('\n', '', regex=True, inplace=True)
        df = all_tables_df
        
        if 'Registration \nNumber' in df.columns:
            df.rename(columns={'Registration \nNumber': 'Registration Number'}, inplace=True)

        elif 'Registration \n Number' in df.columns:
            df.rename(columns={'Registration \n Number': 'Registration Number'}, inplace=True)
        
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
           
            print("Stored record\n")
            if record_for_db[1] != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: PDF Crawler for Myanmar
    '''
    name = 'Directorate of Investment and Company Administration (DICA) in Myanmar'
    description = "Official website of the Directorate of Investment and Company Administration (DICA) in Myanmar. The website serves as a valuable resource for investors and businesses looking to understand the regulatory landscape in Myanmar and take advantage of investment opportunities in the country. It includes information on the laws and procedures related to investment and company registration in Myanmar, as well as resources and tools to help businesses navigate these processes."
    entity_type = 'Company/Organization'
    source_type = 'PDF'
    countries = 'Myanmar'
    category = 'Official Registry'
    update_csv()
    urls_list = pd.read_csv('.//kyb/myanmar/urls.csv')
    for url in urls_list.iterrows():
        url = url[1][0]
       
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
