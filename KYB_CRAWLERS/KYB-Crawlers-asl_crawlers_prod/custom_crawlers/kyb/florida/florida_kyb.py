"""Set System Path"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import pandas as pd
import shortuuid,time
import warnings
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
warnings.filterwarnings('ignore')
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
import os
import stat
import paramiko

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

STATE_NAME = json.load(open('state_names.json'))

def download_directory(sftp, remote_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    for item in sftp.listdir_attr(remote_dir):
        remote_path = remote_dir + '/' + item.filename
        local_path = os.path.join(local_dir, item.filename)
        files_to_skip = ["README.TXT", "99-README.TXT", "WELCOME.TXT"]
        if stat.S_ISDIR(item.st_mode):
            if item.filename not in ["Events", "Filings", "Prior to 2011"]:
                download_directory(sftp, remote_path, local_path)
        else:
            if item.filename not in files_to_skip and not os.path.exists(local_path):
                sftp.get(remote_path, local_path)

def download_complete_data():
    sftp_host = 'sftp.floridados.gov'
    sftp_port = 22
    sftp_user = 'Public'
    sftp_password = 'PubAccess1845!'
    remote_directory = '/Public/doc/cor'
    local_directory = 'inputs'

    transport = paramiko.Transport((sftp_host, sftp_port))
    transport.connect(username=sftp_user, password=sftp_password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print('Downloading started')
    download_directory(sftp, remote_directory, local_directory)
    print('File downloaded successfully.')
   

def get_code_value(code, dict):

    if code !='':
        if code in dict:
            return dict[f'{code}']
        else:
            return ''
    return code


def get_status_value(value):
    if value == 'A':
        return 'active'
    if value == 'I':
        return 'inactive'
    return value

def get_type_value(value):
    if value == 'DOMP':
        return 'Domestic Profit'
    if value == 'DOMNP':
        return 'Domestic Non-Profit'
    if value == 'FORP':
        return 'Foreign Profit'
    if value == 'FORNP':
        return 'Foreign Non-Profit'
    if value == 'DOMLP':
        return 'Domestic Limited Partnership'
    if value == 'FORLP':
        return 'Foreign Limited Partnership'
    if value == 'FLAL':
        return 'Florida Limited Liability Co.'
    if value == 'FORL':
        return 'Foreign Limited Liability Co.'
    if value == 'NPREG':
        return 'Non-Profit, Registration'
    if value == 'TRUST':
        return 'Declaration of Trust'
    if value == 'AGENT':
        return 'Designation of Registered Agent'
    return value

def get_agent_type(value):
    if value == 'C':
        return 'Corporation'
    if value == 'P':
        return 'Person'
    return value

def get_designation(value):
    if value == 'P':
        return 'President'
    if value == 'T':
        return 'Treasurer'
    if value == 'C':
        return 'Chairman'
    if value == 'V':
        return 'Vice President'
    if value == 'S':
        return 'Secretary'
    if value == 'D':
        return 'Director'
    if value == 'MGR':
        return 'Manager'    
    return value

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
    meta_detail['file_date'] = record['file_date']
    meta_detail['fei_number'] = record['fei_number']
    meta_detail['last_transaction_date'] = record['last_transaction_date']

    addresses_detail = [
        {
            'type': 'general_address',
            'address': (f"{record['address_1']} {record['address_2']} {record['city']} {record['state']} {record['zip']} {record['country']}").replace("'", "''").replace("NULL", "").replace("  ", "")
        } if record['address_1'] else '',

        {
            'type': 'postal_address',
            'address': (f"{record['mail_address_1']} {record['mail_address_2']} {record['mail_city']} {record['mail_state']} {record['mail_zip']} {record['mail_country']}").replace("'", "''").replace("NULL", "").replace("  ", "")
        } if record['mail_address_1'] else ''
    ]

    fillings_detail = [
        {
            'date': record['report_date_1']
        } if record['report_date_1'] else '',
        {
            'date': record['report_date_2']
        } if  record['report_date_2'] else '',
        {
            'date': record['report_date_3']
        } if record['report_date_3'] else '',
    ]

    people_detail = [
        {
            'name': record['registered_agent_name'].replace("NULL", "").replace("  ", ""),
            'designation': 'registered_agent',
            'address': record['registered_agent_address'] + ' ' + record['registered_agent_city'] + ' ' + record['registered_agent_state'] + ' ' + record['registered_agent_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['registered_agent_type']),
            }
        } if record['registered_agent_name'] and record['registered_agent_name'] is not None  else '',
        {
            'name': record['officer_1_name'].replace("NULL", "").replace("  ", ""),
            'designation':  get_designation(record['officer_1_title']),
            'address': record['officer_1_address'] + ' ' + record['officer_1_city'] + ' ' + record['officer_1_state'] + ' ' + record['officer_1_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['officer_1_type']),
            }
        } if record['officer_1_name'] and record['officer_1_name'] is not None else '',
        {
            'name': record['officer_2_name'].replace("NULL", "").replace("  ", ""),
            'designation': get_designation(record['officer_2_title']),
            'address': record['officer_2_address'] + ' ' + record['officer_2_city'] + ' ' + record['officer_2_state'] + ' ' + record['officer_2_zip'],
            'meta_detail': {
                'entity_type': get_agent_type(record['officer_2_type']),
            }
        } if record['officer_2_name'] and record['officer_2_name'] is not None else '',
        {
            'name': record['officer_3_name'].replace("NULL", "").replace("  ", ""),
            'designation': get_designation(record['officer_3_title']),
            'address': record['officer_3_address'] + ' ' + record['officer_3_city'] + ' ' + record['officer_3_state'] + ' ' + record['officer_3_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['officer_3_type']),
            }
        } if record['officer_3_name'] and record['officer_3_name'] is not None else '',
        {
            'name': record['officer_4_name'].replace("NULL", "").replace("  ", ""),
            'designation': get_designation(record['officer_4_title']),
            'address': record['officer_4_address'] + ' ' + record['officer_4_city'] + ' ' + record['officer_4_state'] + ' ' + record['officer_4_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['officer_4_type']),
            }
        } if record['officer_4_name'] and record['officer_4_name'] is not None else '',
        {
            'name': record['officer_5_name'].replace("NULL", "").replace("  ", ""),
            'designation': get_designation(record['officer_5_title']),
            'address': record['officer_5_address'] + ' ' + record['officer_5_city'] + ' ' + record['officer_5_state'] + ' ' + record['officer_5_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['officer_5_type']),
            }
        } if record['officer_5_name'] and record['officer_5_name'] is not None else '',
        {
            'name': record['officer_6_name'].replace("NULL", "").replace("  ", ""),
            'designation': get_designation(record['officer_6_title']),
            'address': record['officer_6_address'] + ' ' + record['officer_6_city'] + ' ' + record['officer_6_state'] + ' ' + record['officer_6_zip'],
            'meta_detail':{
                'entity_type': get_agent_type(record['officer_6_type']),
            }
        } if record['officer_6_name'] and record['officer_6_name'] is not None else '',
    ]

    addresses_detail = [a for a in addresses_detail if a]
    fillings_detail = [d for d in fillings_detail if d]
    people_detail = [p for p in people_detail if p]

    data_obj = {
        "name": record['name'].replace("'","''"),
        "status": get_status_value(record['status']),
        "registration_number": str(record['registration_number']).replace("'","''"),
        "registration_date": "",
        "dissolution_date": "",
        "type": get_type_value(record['filing_type']),
        "jurisdiction": get_code_value(record['state_country'], STATE_NAME),
        "jurisdiction_code": record['state_country'],
        "crawler_name": "custom_crawlers.kyb.florida_kyb",
        "country_name": "Florida",
        "company_fetched_data_status": "",
        'addresses_detail':addresses_detail,
        "meta_detail": meta_detail,
        'fillings_detail': fillings_detail,
        'people_detail': people_detail,
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
    data_for_db.append(shortuuid.uuid(str(record['registration_number'])+"florida_kyb")) # entity_id
    data_for_db.append(record['name'].replace("'", "")) #name
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

def get_data_from_lines(lines,source_type, entity_type, country, category, url, name, description):
    for line in lines:
        line = line.replace('\u0000', '')
        data = dict()                
        data['registration_number'] = line[0:12]
        data['name'] = line[12:204].strip().replace("'", "''")
        data['status'] = line[204:205].strip().replace("'", "''")
        data['filing_type'] = line[205:220].strip().replace("'", "''")
        data['address_1'] = line[220:262].strip().replace("'", "''")
        data['address_2'] = line[262:304].strip().replace("'", "''")
        data['city'] = line[304:332].strip().replace("'", "''")
        data['state'] = line[332:334].strip().replace("'", "''")
        data['zip'] = line[334:344].strip().replace("'", "''")
        data['country'] = line[344:346].strip().replace("'", "''")
        data['mail_address_1'] = line[346:388].strip().replace("'", "''")
        data['mail_address_2'] = line[388:430].strip().replace("'", "''")
        data['mail_city'] = line[430:458].strip().replace("'", "''")
        data['mail_state'] = line[458:460].strip().replace("'", "''")
        data['mail_zip'] = line[460:470].strip().replace("'", "''")
        data['mail_country'] = line[470:472].strip().replace("'", "''")
        data['file_date'] = line[472:480].strip().replace("'", "''")
        data['fei_number'] = line[480:494].strip().replace("'", "''")
        data['more_than_six_officers_flag'] = line[494:495].strip().replace("'", "''")
        data['last_transaction_date'] = line[495:503].strip().replace("'", "''")
        data['state_country'] = line[503:505].strip().replace("'", "''")
        data['report_year_1'] = line[505:509].strip().replace("'", "''")
        data['filler_1'] = line[509:510].strip().replace("'", "''")
        data['report_date_1'] = line[510:518].strip().replace("'", "''")
        data['report_year_2'] = line[518:522].strip().replace("'", "''")
        data['filler_2'] = line[522:523].strip().replace("'", "''")
        data['report_date_2'] =line[523:531].strip().replace("'", "''")
        data['report_year_3'] = line[531:535].strip().replace("'", "''")
        data['filler_3'] = line[535:536].strip().replace("'", "''")
        data['report_date_3'] = line[536:544].strip().replace("'", "''")
        data['registered_agent_name'] = line[544:586].strip().replace("'", "''").replace('  ', ' ')
        data['registered_agent_type'] = line[586:587].strip().replace("'", "''")
        data['registered_agent_address'] = line[587:629].strip().replace("'", "''")
        data['registered_agent_city'] = line[629:657].strip().replace("'", "''")
        data['registered_agent_state'] = line[657:659].strip().replace("'", "''")
        data['registered_agent_zip'] = line[659:668].strip().replace("'", "''")
        data['officer_1_title'] = line[668:672].strip().replace("'", "''")
        data['officer_1_type'] = line[672:673].strip().replace("'", "''")
        data['officer_1_name'] = line[673:715].strip().replace("'", "''").replace('  ', ' ')
        data['officer_1_address'] = line[715:757].strip().replace("'", "''")
        data['officer_1_city'] = line[757:785].strip().replace("'", "''")
        data['officer_1_state'] = line[785:787].strip().replace("'", "''")
        data['officer_1_zip'] = line[787:796].strip().replace("'", "''")
        data['officer_2_title'] = line[796:800].strip().replace("'", "''")
        data['officer_2_type'] = line[800:801].strip().replace("'", "''")
        data['officer_2_name'] = line[801:843].strip().replace("'", "''").replace('  ', ' ')
        data['officer_2_address'] = line[843:885].strip().replace("'", "''")
        data['officer_2_city'] = line[885:913].strip().replace("'", "''")
        data['officer_2_state'] = line[913:915].strip().replace("'", "''")
        data['officer_2_zip'] = line[915:924].strip().replace("'", "''")
        data['officer_3_title'] = line[924:928].strip().replace("'", "''")
        data['officer_3_type'] = line[928:929].strip().replace("'", "''")
        data['officer_3_name'] = line[929:971].strip().replace("'", "''").replace('  ', ' ')
        data['officer_3_address'] = line[971:1013].strip().replace("'", "''")
        data['officer_3_city'] = line[1013:1041].strip().replace("'", "''")
        data['officer_3_state'] = line[1041:1043].strip().replace("'", "''")
        data['officer_3_zip'] = line[1043:1052].strip().replace("'", "''")
        data['officer_4_title'] = line[1052:1056].strip().replace("'", "''")
        data['officer_4_type'] = line[1056:1057].strip().replace("'", "''")
        data['officer_4_name'] = line[1057:1099].strip().replace("'", "''").replace('  ', ' ')
        data['officer_4_address'] = line[1099:1141].strip().replace("'", "''")
        data['officer_4_city'] = line[1141:1169].strip().replace("'", "''")
        data['officer_4_state'] = line[1169:1171].strip().replace("'", "''")
        data['officer_4_zip'] = line[1171:1180].strip().replace("'", "''")
        data['officer_5_title'] = line[1180:1184].strip().replace("'", "''")
        data['officer_5_type'] = line[1184:1185].strip().replace("'", "''")
        data['officer_5_name'] = line[1185:1227].strip().replace("'", "''").replace('  ', ' ')
        data['officer_5_address'] = line[1227:1269].strip().replace("'", "''")
        data['officer_5_city'] = line[1269:1297].strip().replace("'", "''")
        data['officer_5_state'] = line[1297:1299].strip().replace("'", "''")
        data['officer_5_zip'] = line[1299:1308].strip().replace("'", "''")
        data['officer_6_title'] = line[1308:1312].strip().replace("'", "''")
        data['officer_6_type'] = line[1312:1313].strip().replace("'", "''")
        data['officer_6_name'] = line[1313:1355].strip().replace("'", "''").replace('  ', ' ')
        data['officer_6_address'] = line[1355:1397].strip().replace("'", "''")
        data['officer_6_city'] = line[1397:1425].strip().replace("'", "''")
        data['officer_6_state'] = line[1425:1427].strip().replace("'", "''")
        data['officer_6_zip'] = line[1427:1436].strip().replace("'", "''")

        record_for_db = prepare_data(data, category,
                                        country, entity_type, source_type, name, url, description)
                    
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
       

        print("Stored record\n")
        if record_for_db[1].replace(' ', '') != '':
            crawlers_functions.db_connection(query)

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
        number_of_records = 0
        
        for txt_file in os.listdir('inputs/'):

            if txt_file.endswith('.txt'):
                with open('inputs/'+txt_file, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
                    if len(lines) > 0:
                        number_of_records += len(lines)
                        get_data_from_lines(lines,source_type, entity_type, country, category, url, name, description)
            else:
                if not txt_file.endswith('.DS_Store'):
                    print('text_file', txt_file)
                    for sub_file in os.listdir('inputs/'+txt_file):
                        if sub_file.endswith('.txt'):
                            with open('inputs/'+txt_file+'/'+sub_file, 'r', encoding='utf-8', errors='ignore') as file:
                                lines = file.readlines()     
                                if len(lines) > 0:
                                    number_of_records += len(lines)
                                    get_data_from_lines(lines, source_type, entity_type, country, category, url, name, description)
                    
        return number_of_records, "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")       

if __name__ == '__main__':
    '''
    Description: CSV Crawler for Florida
    '''
    name = 'Florida Division of Corporations'
    description = "Official website of Florida Division of Corporations. This dataset provides access to corporate data files for businesses registered with the Florida Division of Corporations. "
    entity_type = 'Company/Organization'
    source_type = 'TXT'
    countries = 'Florida'
    category = 'Official Registry'
    url = "https://sftp.floridados.gov/"
    download_complete_data()
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
