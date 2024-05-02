"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
import camelot
from datetime import datetime
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
import pandas as pd

"""Crawler Meta Data Details"""
meta_data = {
    'SOURCE' :'Central Bank Of The U.A.E',
    'COUNTRY' : 'United Arab Emirates',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.centralbank.ae/media/q1inypqm/insurance-list-oct-2023.pdf", 
                        "Source Description": 'The Central Bank of the United Arab Emirates is the state institution responsible for managing the currency, monetary policy, banking and insurance regulation in the United Arab Emirates'},
    'URL' : 'https://www.centralbank.ae/media/q1inypqm/insurance-list-oct-2023.pdf',
    'SOURCE_TYPE' : 'HTML'
}

"""Crawler Configuration"""
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'United Arab Emirates Official Registry Source Two'
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://www.centralbank.ae/media/q1inypqm/insurance-list-oct-2023.pdf'

uae_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = uae_crawler.get_requests_helper()

def main_function():
    """
    Main function to process data from a PDF file.

    This function performs the following tasks:
    1. Makes a request to a specified BASE_URL.
    2. Extracts information such as status code, data size, and content type from the HTTP response.
    3. Uses Camelot to read tables from the PDF.
    4. Combines all tables into a single DataFrame.
    5. Removes unnecessary columns and sets the first row as the header.
    6. Processes the DataFrame to create data objects and inserts records into a database.

    Returns:
    - STATUS_CODE: HTTP status code from the request.
    - DATA_SIZE: (int)
    - CONTENT_TYPE: (str)
    """
    response = request_helper.make_request(BASE_URL)
    STATUS_CODE = response.status_code
    DATA_SIZE = len(response.content)
    CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
    
    tables = camelot.read_pdf(BASE_URL, pages= 'all', split_text=True, flag_size=True)
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

    all_tables_df = all_tables_df.loc[all_tables_df['Registration No.'] != 'Registration No.']
    all_tables_df.replace('\n', '', regex=True, inplace=True)
    df = all_tables_df

    for df_data in df.iterrows(): 
        OBJ ={
            "registration_number":df_data[1]['Registration No.'],
            "name":df_data[1]['Company Name'],
            "type":df_data[1]['Entity Type'],
            "category":df_data[1]['Company Structure']
        }
        OBJ =  uae_crawler.prepare_data_object(OBJ)
        ENTITY_ID = uae_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = uae_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        uae_crawler.insert_record(ROW)
    
    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = main_function()
    
    log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    uae_crawler.db_log(log_data)
    uae_crawler.end_crawler()
    
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    uae_crawler.db_log(log_data)