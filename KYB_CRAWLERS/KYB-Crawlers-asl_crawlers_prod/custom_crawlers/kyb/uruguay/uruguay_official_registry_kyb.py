"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from langdetect import detect
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from deep_translator import GoogleTranslator
import csv
import time


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

def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        max_chunk_size = 5000  # Maximum chunk size for translation
        translated_chunks = []
        
        if len(record_) <= max_chunk_size:
            # If the record is within the limit, add it to the batch for translation
            translated_chunks.append(record_)
        else:
            # Split the record into smaller chunks and add them to the batch for translation
            chunks = [record_[i:i + max_chunk_size] for i in range(0, len(record_), max_chunk_size)]
            translated_chunks.extend(chunks)
        
        translated_batch = []  # Store the translated chunks
        
        # Translate each chunk individually
        for chunk in translated_chunks:
            translated_chunk = GoogleTranslator(source='auto', target='en').translate(chunk)
            translated_batch.append(translated_chunk)
        
        translated_record = ' '.join(translated_batch)
        return translated_record.replace("'", "''").replace('"', '')
    
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        time.sleep(2)
        return translated_record

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
    
    meta_detail['administrative_department'] = record[5].replace("'", "''")
    meta_detail["aliases"] = record[0].replace("'", "''")
    meta_detail["employer_registry_number"]=record[3]
    # meta_detail['description'] = record[-1].replace("'","''")
   
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":googleTranslator(record[0].replace("'","''")),
        "status": "",
        "incorporation_date":record[4],
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "tax_number":str(record[1]),
        "type": googleTranslator(record[2].replace("'","''")),
        "crawler_name": "crawlers.custom_crawlers.kyb.uruguay.uruguay_official_registry_kyb",
        "country_name": "Uruguay",
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
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f'{record[1]}-{record[4]}-uruguay_official_registry_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
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
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        nav_sublist_div = soup.find("ul", class_="Page-navSublist")
        # Find all anchor tags (links) on the page
        links = nav_sublist_div.find_all('a')
        # Iterate over the links and visit each page
        for link in links:
            href = link.get('href')
            link_ = "https://catalogodatos.gub.uy/" + href

            # Send a GET request to the link URL
            response_ = requests.get(link_)
            soup_ = BeautifulSoup(response_.content, 'html.parser')
            a_tags = soup_.find_all("a", class_="Button Button--primary resource-url-analytics resource-type-None")

            for a_tag in a_tags:
                href = a_tag.get("href")
                print("Href:", href)

                # Send a GET request to the CSV file URL
                csv_response = requests.get(href)
                csv_data = csv_response.content.decode('latin-1').splitlines()
                csv_data[0] = csv_data[0].replace(" ", "")
                csv_reader = csv.DictReader(csv_data)
                bussiness_name = ""
                GUY = ""
                RUT = ""
                incorporation_date = ""
                employer_registry_Number = ""
                DATA=[]
                for record in csv_reader:
                    
                    if "RazonSocial" in record:
                        bussiness_name = record["RazonSocial"]
                    elif "RazónSocial" in record:
                        bussiness_name = record["RazónSocial"]
                    elif "Nombredelasociedad" in record:
                        bussiness_name = record["Nombredelasociedad"]
                    elif "RazÃ³nSocial" in record:
                        bussiness_name = record["RazÃ³nSocial"]
                    elif "RAZ?NSOCIAL" in record:
                        bussiness_name = record["RAZ?NSOCIAL"]
                    elif "RAZONSOCIAL" in record:
                        bussiness_name = record["RAZONSOCIAL"]
                    elif "RAZÓNSOCIAL" in record:
                        bussiness_name = record["RAZÓNSOCIAL"]

                    
                    if "Tipo" in record:
                        GUY = record["Tipo"]
                    elif "TIPO" in record:
                        GUY = record["TIPO"]
                    elif "Nombredelproceso" in record:
                        GUY = record["Nombredelproceso"]
                    elif "Tiposocietario" in record:
                        GUY = record["Tiposocietario"]
                    elif "Guy" in record:
                        GUY = record["Guy"]

                
                    if "RUT" in record:
                        RUT = record["RUT"]
                    elif "Número de RUT" in record:
                        RUT = record["NúmerodeRUT"]

                    
                    if "NúmerodeBPS" in record:
                        employer_registry_Number = record["NúmerodeBPS"]

                
                    if "Fechadecreación" in record:
                        incorporation_date = record["Fechadecreación"]

                    administrative_department = record.get("Departamento", record.get("Oficina", ""))

                    DATA.append([bussiness_name, RUT, GUY,employer_registry_Number,incorporation_date,administrative_department])
               
                
                for record_ in DATA:
                   
                    
                    
                    record_for_db = prepare_data(record_, category,country, entity_type, source_type, name, url, description)
                    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                    UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                    
                    print("stored in database\n")
                    crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Russia
    '''
    name = 'AGESIC (Agency for the Development of Electronic Government and Information and Knowledge Society)'
    description = "This is the data catalog of the Uruguayan government's AGESIC (Agency for the Development of Electronic Government and Information and Knowledge Society). Specifically, it is a dataset on the creation of companies via the 'Empresa en el día' (Company in a Day) initiative."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Uruguay'
    category = 'Official Registry'
    url = "https://catalogodatos.gub.uy/dataset/agesic-creacion-de-empresas-a-traves-de-empresa-en-el-dia/resource/70f1d128-f184-452b-8a0c-e3f53b19ee36"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
