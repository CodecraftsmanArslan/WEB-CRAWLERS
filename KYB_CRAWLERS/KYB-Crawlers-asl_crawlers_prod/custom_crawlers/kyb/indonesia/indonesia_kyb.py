"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid, time, csv
from bs4 import BeautifulSoup
import pandas as pd
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
from deep_translator import GoogleTranslator

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
'''DRIVER CONFIGURATION'''

def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        max_chunk_size = 5000  # Maximum chunk size for translation
        translated_chunks = []
        
        if len(record_) <= max_chunk_size:
            # If the record is within the limit, translate it as a whole
            translated_record = GoogleTranslator(source='auto', target='en').translate(record_)
            translated_chunks.append(translated_record)
        else:
            # Split the record into smaller chunks and translate them individually
            chunks = [record_[i:i + max_chunk_size] for i in range(0, len(record_), max_chunk_size)]
            for chunk in chunks:
                translated_chunk = GoogleTranslator(source='auto', target='en').translate(chunk)
                translated_chunks.append(translated_chunk)
        
        translated_record = ' '.join(translated_chunks)
        return translated_record.replace("'", "''").replace('"', '')
    
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        time.sleep(1)
        return record_
    
def download_file(url, file_no):
    if not os.path.exists("input"):
        os.makedirs("input")

    response = requests.get(url)

    if response.status_code == 200:
        file_path = os.path.join("input/", "file_{}.csv".format(file_no))
        with open(file_path, 'wb') as file:
            file.write(response.content)

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, data_obj):
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{url_}-indonesia_kyb')) # entity_id
    data_for_db.append(googleTranslator(record[0].replace("'", ""))) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(data_obj)) # data
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


def get_records(source_type, entity_type, country, category, url, name, description, file_no, data_schema):
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
        
        download_file(SOURCE_URL, file_no)

        response = requests.get(SOURCE_URL)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        DATA = []

        if SOURCE_URL == "https://data.demakkab.go.id/dataset/a3b71fbc-21df-4f6e-aba7-0251b2b19297/resource/5f6dd746-e206-4eff-9299-679c2fec938f/download/perusahaan.xlsx":
            df = pd.read_excel(url)
            headers = df.iloc[0]
            df.columns = headers
            df = df.iloc[1:]
            csv_data = df.to_csv(index=False)
            csv_reader = csv.DictReader(csv_data.splitlines())

            data_obj = data_schema[SOURCE_URL]

            for row in csv_reader:
                data_obj["name"] = row.get('NAMA PERUSAHAAN')

                DATA.append(data_obj)
                record = [googleTranslator(row.get('NAMA PERUSAHAAN'))]
                record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description, data_obj)
                                        
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                            
                if record_for_db[1] != "":
                    print("Stored record.")
                    crawlers_functions.db_connection(query)

        elif SOURCE_URL == "https://data.jakarta.go.id/dataset/0be09038-2624-44cb-a800-ee4097c26770/resource/b794609e-3a6b-4298-bae3-4d734bea6879/download/Data-Perusahaan-Armada-Bus.csv":
            df = pd.read_csv(url)
            csv_data = df.to_csv(index=False)
            csv_reader = csv.DictReader(csv_data.splitlines())

            data_obj = data_schema[SOURCE_URL]

            for row in csv_reader:
                data_obj["name"] = row.get('perusahaan')
                data_obj["meta_detail"]["terminal"] = googleTranslator(row.get("terminal"))
                data_obj["meta_detail"]["locality"] = googleTranslator(row.get("jurusan"))

                DATA.append(data_obj)
                record = [googleTranslator(row.get('perusahaan'))]
                record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description, data_obj)
                                        
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                            
                if record_for_db[1] != "":
                    print("Stored record.")
                    crawlers_functions.db_connection(query)

        elif SOURCE_URL == "https://katalog.data.go.id/datastore/dump/7070deed-44e9-4ccb-814b-256033399219?bom=True":
            df = pd.read_csv(url)
            csv_data = df.to_csv(index=False)
            csv_reader = csv.DictReader(csv_data.splitlines())

            data_obj = data_schema[SOURCE_URL]

            for row in csv_reader:
                data_obj["name"] = row.get('nama_perusahaan')
                data_obj["status"] = googleTranslator(row.get('status_lkpm'))
                data_obj["type"] = googleTranslator(row.get('tipe'))
                
                data_obj["meta_detail"]["country"] = row.get('Negara')
                data_obj["meta_detail"]["license_number"] = row.get('no_izin')
                data_obj["meta_detail"]["year"] = row.get('tahun')
                data_obj["meta_detail"]["approval_date"] = row.get('tanggal_disetujui')
                data_obj["meta_detail"]["total_investment_(US$)"] = row.get('total_investasi_$')
                data_obj["meta_detail"]["total_investment_(million Rupiah)"] = row.get('total_investasi_juta')
                data_obj["meta_detail"]["LKPM_value_(US$ thousand)"] = row.get('Nilai LKPM US$.Ribu')
                data_obj["meta_detail"]["LKPM_value_(million Rupiah)"] = row.get('Nilai LKPM Rp.Juta')
                data_obj["meta_detail"]["net_value_(US$ thousand)"] = row.get('Nilai Net US$ ribu')
                data_obj["meta_detail"]["net_value_(US$ Million)"] = row.get('Nilai Net US$ Juta')
                data_obj["meta_detail"]["net_value_(Rupiah Million)"] = row.get('Nilai Net Rp. Juta')
                data_obj["meta_detail"]["net_value_(Rupiah Billion)"] = row.get('nilai_net_miliar')
                
                data_obj["contacts_detail"][0]["value"] = row.get('no_telpon_perusahaan')
                
                data_obj["addresses_detail"][0]["address"] = googleTranslator(row.get('alamat_perusahaan'))
                
                data_obj["addresses_detail"][1]["meta_detail"]["project_location"] = googleTranslator(row.get('Lokasi_proyek'))
                data_obj["addresses_detail"][1]["meta_detail"]["province"] = googleTranslator(row.get('Provinsi'))
                data_obj["addresses_detail"][1]["meta_detail"]["district"] = googleTranslator(row.get('Kabupaten_kota'))
                data_obj["addresses_detail"][1]["meta_detail"]["region"] = googleTranslator(row.get('Wilayah'))
                
                data_obj["additional_detail"][0]["data"][0]["industry_type"] = googleTranslator(row.get('Bidang_usaha'))
                data_obj["additional_detail"][0]["data"][0]["KBLI_code"] = googleTranslator(row.get('Nama KBLI'))
                data_obj["additional_detail"][0]["data"][0]["sector"] = googleTranslator(row.get('Sektor'))
                data_obj["additional_detail"][0]["data"][0]["primary_sector"] = googleTranslator(row.get('Sektor Utama'))
                data_obj["additional_detail"][1]["data"][0]["overseas_employees"] = row.get('Tki')
                data_obj["additional_detail"][1]["data"][0]["foreign_employees"] = row.get('Tki')

                DATA.append(data_obj)
                record = [googleTranslator(row.get('nama_perusahaan'))]
                record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description, data_obj)
                                        
                query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                        WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
                            
                if record_for_db[1] != "":
                    print("Stored record.")
                    crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Indonesia
    '''
    countries = "Indonesia"
    entity_type = "Company/Organization"
    category = "Official Registry"    
    name = "One Data Indonesia"
    description = "One Data Indonesia Portal is Indonesia's official open data portal managed by the Central level Indonesia One Data Secretariat, Ministry of National Development Planning / Bappenas."
    source_type = "CSV"

    file_no = 1
    URLS = [
        "https://data.demakkab.go.id/dataset/a3b71fbc-21df-4f6e-aba7-0251b2b19297/resource/5f6dd746-e206-4eff-9299-679c2fec938f/download/perusahaan.xlsx",
        "https://data.jakarta.go.id/dataset/0be09038-2624-44cb-a800-ee4097c26770/resource/b794609e-3a6b-4298-bae3-4d734bea6879/download/Data-Perusahaan-Armada-Bus.csv",
        "https://katalog.data.go.id/datastore/dump/7070deed-44e9-4ccb-814b-256033399219?bom=True"
    ]

    with open("schema.json") as f:
        json_schema = f.read()
    json_schema = json.loads(json_schema)
    data_schema = json_schema['Indonesia']

    for url in URLS: 
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description, file_no, data_schema)
        file_no+=1
        
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
