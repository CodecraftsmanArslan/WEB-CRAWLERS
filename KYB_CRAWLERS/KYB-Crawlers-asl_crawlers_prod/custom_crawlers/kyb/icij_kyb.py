import sys
from pathlib import Path

import pandas as pd
sys.path.append(str(Path(__file__).parent.parent.parent))
import json
from helpers.crawlers_helper_func import CrawlersFunctions
import shortuuid
from helpers.logger import Logger
from dotenv import load_dotenv
import psycopg2
import traceback
import os
from datetime import datetime

load_dotenv()

path = 'icij_csv/'
node_addresses = pd.read_csv(path+'nodes-addresses.csv').fillna('')
node_entities = pd.read_csv(path+'nodes-entities.csv').fillna('')
node_intermediaries = pd.read_csv(path+'nodes-intermediaries.csv').fillna('')
node_officers = pd.read_csv(path+'nodes-officers.csv').fillna('')
node_others = pd.read_csv(path+'nodes-others.csv').fillna('')
relationships = pd.read_csv(path+'relationships.csv').fillna('')


crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + \
    '/crawlers_metadata/downloads/excel_csv/'
FILENAME = ''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'


def dmy_en_month_to_number(date_string):
    # Try parsing the date string using different formats
    formats = ['%d-%b-%Y', '%b %d, %Y', '%Y-%m-%d']
    formatted_date = ''

    for fmt in formats:
        try:
            date = datetime.strptime(date_string, fmt)
            formatted_date = date.strftime('%d-%m-%Y')
            break
        except ValueError:
            pass

    return formatted_date

def clean_designation_value(string):
    substring = "of"
    last_index = string.rfind(substring)

    if last_index != -1:
        new_string = string[:last_index] + string[last_index+len(substring):]
    else:
        new_string = string

    return new_string.replace("'", "''").strip()

def get_countries(value):

    countries = list()
    split_countries = value.split(";")
    # Print the separated parts
    for country in split_countries:
        if country and 'Not identified' not in country and 'XXX' not in country:
            countries.append(country.replace("'", ""))

    countries_string =  ', '.join(countries)

    return countries_string


def prepare_data(entity_id, record, category, entity_type, type_, name_, url_, description_):
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
    data_for_db.append(shortuuid.uuid(str(entity_id)+url_+'custom_crawlers.kyb.icij_kyb'))  # entity_id
    data_for_db.append(record['name'].replace("'", ""))  # name
    data_for_db.append(json.dumps(
        [dmy_en_month_to_number(record['registration_date'])] if record['registration_date'] != '' else []))  # dob
    data_for_db.append(json.dumps([category]))  # category
    data_for_db.append(json.dumps([record['country_name']] if record['country_name'] != '' else [] ))  # country
    data_for_db.append(entity_type.title())  # entity_type
    data_for_db.append(json.dumps([]))  # img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'", "''"), "Name": name_}
    data_for_db.append(json.dumps(record))  # data
    data_for_db.append(json.dumps(source_details))  # source_details
    data_for_db.append(name_ + "-" + type_)  # source
    data_for_db.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_for_db.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    data_for_db.append('en')
    data_for_db.append('true')

    return data_for_db


def get_records(source_type, entity_type, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        print('length of data', len(node_entities))
        for entity in node_entities.values:
            if entity[1] == "" and entity[2] == "":
                continue     
            
            print(entity[0])
            officer_list = list()
            additional_detail = list()
            addresses = list()
            my_object = dict()

            my_object['name'] = entity[1].replace(
                "'", "''") if entity[1] is not None else ''
            my_object['status'] = entity[13].replace(
                "'", "''") if entity[13] is not None else ''
            my_object['registration_number'] = ''
            my_object['registration_date'] = ''
            my_object['inactive_date'] = entity[10] if entity[10] is not None else ''
            my_object['incorporation_date'] = entity[9] if entity[9] is not None else ''
            my_object['dissolution_date'] = entity[11] if entity[11] is not None else ''
            my_object['jurisdiction_code'] = entity[4].replace(
                "'", "''") if entity[4] != 'XXX' and entity[4] is not None else ''
            my_object['jurisdiction'] = entity[5].replace(
                "'", "''") if entity[5] is not None else ''
            my_object['type'] = entity[6].replace(
                "'", "''") if entity[6] is not None else ''
            my_object['crawler_name'] = 'custom_crawlers.kyb.icij_kyb'
            my_object['country_name'] = get_countries(
                entity[17]) if entity[17] is not None else ''
            my_object['company_fetched_data_status'] = ''
            
            if my_object['name'] == "":
                my_object['name'] = entity[2].replace("'", "''")

            meta_details = dict()
            meta_details['original_name'] = entity[2].replace(
                "'", "''") if entity[2] is not None else ''
            meta_details['dorm_date'] = entity[12] if entity[12] is not None else ''
            meta_details['service_provider'] = entity[14].replace(
                "'", "''") if entity[14] is not None else ''
            meta_details['ibcRUC'] = entity[15] if entity[15] is not None else ''
            meta_details['country_codes'] = get_countries(
                entity[16]) if entity[16] is not None else ''
            meta_details['valid_until'] = entity[19].replace(
                "'", "''") if entity[19] is not None else ''
            meta_details['description'] = entity[20].replace(
                "'", "''") if entity[20] is not None else ''

            if entity[7] != '':
                primary_address = dict()
                primary_address['type'] = 'general_address'
                primary_address['address'] = entity[7].replace(
                "'", "''")
                addresses.append(primary_address)

            entity_relation_at = relationships[relationships['node_id_end'] == entity[0]].values
            if (len(entity_relation_at) > 0):
                for relation in entity_relation_at:
                    if relation[2] == 'officer_of':
                        officer = node_officers[node_officers['node_id'] == relation[0]].values
                        if len(officer) > 0:
                            officer = officer[0]

                            officer_data = dict()
                            officer_data['name'] = officer[1].replace(
                                "'", "''") if officer[1] is not None else ''
                            officer_data['designation'] = clean_designation_value(relation[3]) if relation[3] is not None else ''
                            officer_data['appointment_date'] = relation[5] if relation[5] is not None else ''
                            officer_data['termination_date'] = relation[6] if relation[6] is not None else ''
                            officer_data['meta_detail'] = {
                                'countries': get_countries(
                                    officer[2]) if officer[2] is not None else '',
                                'country_codes': get_countries(officer[3]) if officer[3] is not None else '',
                                'valid_until': officer[5].replace(
                                    "'", "''") if officer[5] is not None else '',
                                'description': officer[6].replace(
                                    "'", "''") if officer[6] is not None else ''
                            }

                            officers_relations = relationships[relationships['node_id_start'] == officer[0]].values

                            if len(officers_relations) > 0:
                                for officer_relation in officers_relations:
                                    if officer_relation[2] == 'registered_address':
                                        officer_addresses = node_addresses[node_addresses['node_id'] == officer_relation[1]].values
                                        if  len(officer_addresses) > 0:
                                            officer_addresses = officer_addresses[0]
                                            officer_data['address'] = officer_addresses[1].replace("'", "''") if officer_addresses[1] is not None else officer_addresses[2].replace("'", "''")
                                        else:
                                            officer_data['address'] = ''
                                    else:
                                        officer_data['address'] = ''
                            else:
                                officer_data['address'] = ''

                            
                            officer_data['postal_address'] = ''

                            officer_list.append(officer_data)
                        
                    if relation[2] == 'intermediary_of' or relation[2] == 'officer_of':

                        intermediary = node_intermediaries[node_intermediaries['node_id'] == relation[0]].values

                        if len(intermediary) > 0:
                            intermediary = intermediary[0]
                            intermediary_obj = dict()
                            intermediary_obj['type'] = 'intermediary'
                            intermediary_data = dict()

                            intermediary_data['name'] = intermediary[1].replace(
                                "'", "''") if intermediary[1] is not None else ''
                            intermediary_data['status'] = intermediary[2].replace(
                                "'", "''") if intermediary[2] is not None else ''
                            intermediary_data['address'] = intermediary[4].replace(
                                "'", "''") if intermediary[4] is not None else ''
                            intermediary_data['countries'] = get_countries(
                                intermediary[5]) if intermediary[5] is not None else ''
                            intermediary_data['country_codes'] = get_countries(intermediary[6]) if intermediary[6] is not None else ''
                            intermediary_data['valid_until'] = intermediary[8].replace(
                                "'", "''") if intermediary[8] is not None else ''
                            intermediary_data['description'] = intermediary[9].replace(
                                "'", "''") if intermediary[9] is not None else ''

                            intermediary_obj['data'] = [intermediary_data]

                            additional_detail.append(intermediary_obj)

                    if relation[2] == 'connected_to':
                        other_node = node_others[node_others['node_id'] == relation[0]].values

                        if  len(other_node) > 0:
                            other_node = other_node[0]
                            
                            other_link_data = dict()
                            other_link_data['type'] = 'linked_company'

                            other_node_obj = dict()
                            other_node_obj['name'] = other_node[1].replace(
                                "'", "''") if other_node[1] is not None else ''

                            other_node_obj['type'] = other_node[2].replace(
                                "'", "''") if other_node[2] is not None else ''
                            other_node_obj['incorporation_date'] = other_node[3] if other_node[3] is not None else ''
                            other_node_obj['struck_off_date'] = other_node[4] if other_node[4] is not None else ''
                            other_node_obj['closed_date'] = other_node[5] if other_node[5] is not None else ''

                            other_node_obj['jurisdiction'] = other_node[6] if other_node[6] is not None else ''
                            other_node_obj['jurisdiction_description'] = other_node[7].replace(
                                "'", "''") if other_node[7] is not None else ''
                            other_node_obj['countries'] = get_countries(
                                other_node[8]) if other_node[8] is not None else ''
                            other_node_obj['country_code'] = get_countries(other_node[9]) if other_node[9] is not None else ''
                            other_node_obj['valid_until'] = other_node[11].replace(
                                "'", "''") if other_node[11] is not None else ''
                            other_node_obj['description'] = other_node[12].replace(
                                "'", "''") if other_node[12] is not None else ''

                            if other_node_obj['jurisdiction'] == 'XXX':
                                other_node_obj['jurisdiction'] = ''

                            other_link_data['data'] = [other_node_obj]
                            additional_detail.append(other_link_data)                  

            entity_relation_at_start = relationships[relationships['node_id_start'] == entity[0]].values

            if (len(entity_relation_at_start) > 0):
                for relation in entity_relation_at_start:

                    if relation[2] == 'registered_address':
                        address = node_addresses[node_addresses['node_id'] == relation[1]].values

                        if  len(address) > 0:
                            address_obj = dict()
                            address = address[0]

                            address_obj['type'] = 'general_address'
                            address_obj['address'] = address[1].strip().replace(
                                "'", "''") if address[1] is not None else address[2].strip().replace(
                                "'", "''")

                            address_obj['description'] = address[7].replace(
                                "'", "''") if address[7] is not None else ''

                            address_obj['meta_detail'] = {
                                'country' : get_countries(
                                address[3]) if address[3] is not None else '',
                                'country_code' : get_countries(address[4]) if address[4] is not None else '',
                                'valid_until' : address[6].replace(
                                "'", "''") if address[6] is not None else ''
                            }
                            addresses.append(address_obj)
    
            
            previous_names_detail = [
                {
                    'name': entity[3].replace("'", "''") if entity[3] is not None else ''
                } if entity[3] else ''
            ]
            previous_names_detail = [p for p in previous_names_detail if p]

            my_object['additional_detail'] = additional_detail
            my_object['addresses_detail'] = addresses
            my_object['meta_detail'] = meta_details
            my_object['people_detail'] = officer_list
            my_object['previous_names_detail'] = previous_names_detail

            record_for_db = prepare_data(
                entity[0], my_object, category, entity_type, source_type, name, url, description)

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Stored record.")
            if record_for_db[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(node_entities), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e, tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'", "''")


if __name__ == '__main__':
    '''
    Description: Crawler for Oregon for ICIJ Data
    '''
    name = 'The International Consortium of Investigative Journalists (ICIJ)'
    description = "The International Consortium of Investigative Journalists (ICIJ) is a global network of more than 200 investigative journalists in over 70 countries who collaborate on in-depth investigative stories. The ICIJ is the publisher of the Offshore Leaks Database, which contains information about offshore companies and trusts, as well as their owners and intermediaries, as revealed in leaked documents. The aim of the database is to provide greater transparency around offshore financial operations and to expose potential wrongdoing or financial improprieties."
    entity_type = 'Company/ Persons/ Organisations'
    source_type = 'CSV'
    category = 'Offshore'
    url = 'https://offshoreleaks.icij.org/pages/database'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(
        source_type, entity_type, category, url, name, description)
    
    print("Crawler Completed!")

    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path": file_path, "trace_back": trace_back,  "crawler": "HTML"})
    logger.log()
