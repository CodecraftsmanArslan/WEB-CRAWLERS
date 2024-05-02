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
import wget
import shutil
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
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


import pandas as pd

def qualification_code(code):
    file_path = "brazil/mapping/Qualification_codes.csv"
    df_codes = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1')
    matching_values = df_codes.loc[df_codes['A'] == code, 'B'].tolist()
    return matching_values[0] if matching_values else ""

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
   
    # preparing meta_detail dictionary object
    meta_detail = dict()  
    meta_detail["member_code"]=str(record[1])
    meta_detail["cpf_or_cnpj_of_the_member_number"]=str(record[3]).replace("***", "").replace("**", "")
    # meta_detail["qualification_code"]=str(record[4])
    meta_detail["foreign_member_of_the_country_code"]=str(record[6])
    # meta_detail["legal_authority"]=str(record[8])
    # meta_detail["legal_authority_qualification_code"]=str(record[9])

    additional_detail  = [
            {
            "type": "qualification_information",
            "data":[
                {
                    "name": qualification_code(record[4]),
                    "qualification_code": str(record[4])
                }
            ]
            },
              {
            "type": "legal_authority_information",
            "data":[
                {
                    "legal_authority": str(record[8]),
                    "legal_authority_qualification_code": str(record[9])
                }
            ]
            }
    ]
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record[2].replace("'","''"),
        "tax_number":str(record[7]).replace("***", "").replace("**", ""),
        "status": "",
        "registration_number": str(record[0]),
        "registration_date": str(datetime.datetime.fromtimestamp(int(float(record[5]))/1000)),
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.brazil.brazil_kyb2",
        "country_name": "Brazil",
        "company_fetched_data_status": "",
        "additional_detail":additional_detail,
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
    crawler_name = 'brazil_kyb2'
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{crawler_name}')) # entity_id
    data_for_db.append(record[2].replace("'", "")) #name
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
        SOURCE_URL = url
        # response = requests.get(SOURCE_URL, stream=True, headers={
        #     'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        # STATUS_CODE = response.status_code
        # DATA_SIZE = len(response.content)
        # CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        FILE_PATH = os.path.join(os.getcwd(), '../../crawlers_metadata/downloads/custom_scripts')
        print(FILE_PATH)
       
        
        
        if os.path.exists(f'{FILE_PATH}/brazil2'):
            shutil.rmtree(f'{FILE_PATH}/brazil2')

        os.mkdir(f'{FILE_PATH}/brazil2')

        wget.download(url,f'{FILE_PATH}/brazil2/brazil2.zip')

        with zipfile.ZipFile(f'{FILE_PATH}/brazil2/brazil2.zip', 'r') as zip_ref:
            zip_ref.extractall(f'{FILE_PATH}/brazil2')

        filenames = os.listdir(f'{FILE_PATH}/brazil2')
        print("filenames",filenames)
       
        csv_files = [ filename for filename in filenames if filename.endswith( 'CSV' ) ]
        
        df = pd.read_csv(f'{FILE_PATH}/brazil2/{csv_files[0]}'.format(FILE_PATH), low_memory=False,sep=';', header=None,encoding= 'unicode_escape')
        print("Zip",df)
        df.fillna("",inplace=True)
        print(len(df),"DF")
        print(df.columns)
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
            insertion_data, lang = crawlers_functions.check_language(
                record_for_db, source_type, url, description, name)
    
            if lang == 'en':
                crawlers_functions.language_handler(insertion_data, 'reports')
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                    WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)
            else:
                query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}'""".format(
                    *insertion_data)

            print("Stored record\n",insertion_data)
            if insertion_data[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: ZIP Crawler for Brazil
    '''
    name = 'Federal Revenue of Brazil (RFB) - National Register of Legal Entities (CNPJ)'
    description = "This link provides a dataset related to the Cadastro Nacional da Pessoa Jurídica (CNPJ), which is the Brazilian national registry of legal entities . The dataset contains information about companies registered with the CNPJ, including their name, address, tax identification number, and other details."
    entity_type = 'Company/Organization'
    source_type = 'ZIP'
    countries = 'Brazil'
    category = 'Official Registry'
    url_list = ['https://dadosabertos.rfb.gov.br/CNPJ/Socios0.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios1.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios2.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios3.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios4.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios5.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios6.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios7.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios8.zip',
                'https://dadosabertos.rfb.gov.br/CNPJ/Socios9.zip',]
                
    for url in url_list:

        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()
