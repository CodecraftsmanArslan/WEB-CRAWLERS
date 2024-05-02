"""Set System Path"""
import shutil
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import re, time
import pandas as pd
import shortuuid
import requests, json,os
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
# from deep_translator import GoogleTranslator

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
# FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/excel_csv/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'
def split_values(value,delimiter1,delimiter2,columns):
    """this function splits details occuring in a string into a useful info dict.
    e.g CAMENEV OLESEA [Lichidator], STAVINSCHI OLGA [Administrator], there is an information of persons name and his role, the delimiter1 is ], here which splits person details and the delimiter2 is [ which splits person name and his role. columns contains ['name', 'role'] and after that trim the string and remove other symbols

    Args:
        value (Str): Value to split
        delimiter1 (Str): this delimiter splits persons details
        delimiter2 (Str): this delimiter splits values in persons details
        columns (Str): columns in order of splitted values

    Returns:
        list
    """
    value = str(value)
    data  = []
    if value != '' and value != 'nan':
        data = [*data,*[{columns[0]:re.sub(r'[^\w\s,]|_', '', x[0]).strip(),columns[1]: re.sub(r'[^\w\s,]|_', '', x[1]).strip() if len(x) > 1 else ""} for x in [y.split(delimiter2) for y in value.split(delimiter1)]]]
    return data

def find_and_update_codes(values, df_to_search, type):
    """This function finds the codes in other sheets and replaces them with their values in the current sheet.

    Args:
        values (str): String containing codes to search in other sheets.
        df_to_search (DataFrame): Sheet to search for codes.
        type (str): Name of key to hold the value.

    Returns:
        list: List of dictionaries containing corresponding values.
    """
    search_result_list = str(values).split(',')
    corresponding_value = []
    
    for index, val in enumerate(search_result_list):
        if val != '' and val != 'nan':
            try:
                found = df_to_search.loc[df_to_search['ID'] == int(val.strip())].values
            except:
                found = df_to_search.loc[df_to_search['ID'] == int(float(val.strip()))].values
            code = found[0][0] if len(found) > 0 else ""
            name = found[0][1] if len(found) > 0 else ""
            corresponding_value.append({'code':str(code) , 'name': name.replace("'", "''").replace("NONE","").replace("None","").replace("none","").replace("NULL","").strip()})
    
    return corresponding_value

def find_and_update_country_codes(values, df_to_search, type):
    """This function finds the codes in other sheets and replaces them with their values in the current sheet

    Args:
        values (str): String containing codes to search in other sheets
        df_to_search (dataframe): Sheet to search for codes
        type (str): Name of key to hold the value

    Returns:
        list
    """
    name = str(values)

    search_result_list = str(values).split('(')
    corresponding_value = []
    if len(search_result_list) >= 2:
        country_val = search_result_list[1].replace(")", "").strip()
        try:
            found = df_to_search.loc[df_to_search['COD'] == country_val.strip()].values
        except:
            found = df_to_search.loc[df_to_search['COD'] == country_val.strip()].values
        corresponding_value.append({"country": found[0][1] if len(found) > 0 else "", "name": name.replace("'", "''").replace("NONE","").replace("None","").replace("none","").replace("NULL","").strip()})
    return corresponding_value
 
def get_listed_object(record, countries):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
    @param record
    @return dict
    '''
    # preparing summary dictionary object
    meta_detail = dict()
    meta_detail['territorial_id_number'] = str(record["Codul unităţii administrativ-teritoriale (CUATM)"]).replace("'","")
    meta_detail['aliases'] = record["Denumirea completă"].replace("'","").replace("NONE","").replace("None","").replace("none","").replace("NULL","").strip()
    address = dict()
    address['type'] = "general_address"
    address['address'] = str(record["Adresa"]).replace("'","").replace("NONE","").replace("None","").replace("none","").replace("NULL","").strip()
    address['description'] = ""
    liquidation_date =str(record["Data lichidării"])

    people_detail = []
    founder_data =record.get("Lista fondatorilor (cu indicarea cotei părţi în capitalul social %)")
    print(founder_data)
    if founder_data is not None and isinstance(founder_data, str):
        founder_list = founder_data.split("),")
        print(founder_list)
        for founder in founder_list:
            founder = str(founder)
            try:
                cpname, percentage = founder.split('(')
            except ValueError:
                cpname = founder
                percentage = ""
    else:
        # Handle the case where the data is missing or not a string
        cpname = ""
        percentage = ""


    # founder_list = record["Lista fondatorilor (cu indicarea cotei părţi în capitalul social %)"].split("),")
    # print(founder_list)
    # for founder in founder_list:
    #     founder = str(founder)
    #     try:
    #         cpname, percentage = founder.split('(')
    #     except ValueError:
    #         cpname = founder
    #         percentage = ""
        
        meta_detail_ = {}
        if percentage != "":
            meta_detail_["percentage"] = percentage.replace(")","")
        person = {
            "name": cpname.replace("'","").strip(),
            "meta_detail": meta_detail_,
            "designation": "shareholder"
        }  
        people_detail.append(person)
    
    leaders = record["Lista conducătorilor (cu indicarea rolurilor)"].split(", ")
    for leader in leaders:
        leader_parts = leader.split("[")
        leader_name = leader_parts[0].strip()
        if len(leader_parts) >= 2:
            designation = leader_parts[1].replace("]", "").strip()
        else:
            designation = "" 
        # designation = leader_parts[1].replace("]", "").strip()
        dict_leader = {
            "designation": str(designation).replace("'",""),
            "name": str(leader_name).replace("'","").replace("NONE","").replace("None","").replace("none","").replace("NULL","").strip()
        }
        people_detail.append(dict_leader)
        
    
# create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["Denumirea completă"].replace("'","").replace('\"',''),
        "status": "",
        "registration_number": str(record["IDNO/ Cod fiscal"]).split(".")[0],
        "registration_date": str(record["Data înregistrării"]),
        "dissolution_date": liquidation_date if liquidation_date != 'NaT' else "",
        "type": record["Forma org./jurid."].replace("'",""),
        "crawler_name": "crawlers.custom_crawlers.kyb.republic_moldova.republic_moldova_kyb",
        "country_name": countries,
        "company_fetched_data_status": "",
        "people_detail":people_detail,
        "addresses_detail": [address],
        "additional_detail":[
            {"type":"licensed_activity_information", "data":find_and_update_codes(record["Genuri de activitate licentiate"],license_sheet,'licensed_activity_type')},
            {"type":"unlicensed_activity_information", "data":find_and_update_codes(record["Genuri de activitate nelicentiate"],non_license_sheet,'unlicensed_activity_type')},
            {"type":"beneficial_owner", "data":find_and_update_country_codes(record["Lista beneficiarilor efectivi (Nume, Prenume, Ţara de reşedinţă)"],country_sheet, "beneficial_owner")}
        ],
        
        "meta_detail": meta_detail
    }
    # Remove empty entries in additional_detail
    data_obj["additional_detail"] = [item for item in data_obj["additional_detail"] if item["data"]]

    if any("Lichidator" in person.get("designation", "") for person in data_obj.get("people_detail", [])):
        data_obj["status"] = "liquidator appointed"
    else:
        data_obj["status"] = ""

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
    data_for_db.append(shortuuid.uuid(f'{str(record["IDNO/ Cod fiscal"])}{record["Codul unităţii administrativ-teritoriale (CUATM)"]}{"republic_moldova_kyb"}')) # entity_id
    data_for_db.append(record["Denumirea completă"].replace("'", "")) #name
    data_for_db.append(json.dumps([str(record["Data înregistrării"]).replace(' 00:00:00','')])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'",""), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record, country))) # data
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
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME, license_sheet,non_license_sheet, country_sheet
        FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts/'
        SOURCE_URL = url
        FILENAME = 'Moldova.xlsx'
        response = requests.get(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        
        with open(f'{FILE_PATH}{FILENAME}', 'wb') as f:
            f.write(response.content) 
        
        file_path = os.path.join(f'{FILE_PATH}{FILENAME}')
        print(file_path)
        df = pd.read_excel(file_path,skiprows=1, sheet_name="Company")
        non_license_sheet = pd.read_excel(file_path,sheet_name="Clasificare nelicenţiate")
        license_sheet = pd.read_excel(file_path,sheet_name="Clasificare licenţiate")
        country_sheet = pd.read_excel(file_path,sheet_name='Clasificare ţara')
        df.fillna("", inplace=True)
        non_license_sheet.fillna("", inplace=True)
        license_sheet.fillna("", inplace=True)
        country_sheet.fillna("", inplace=True)
        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                            country, entity_type, source_type, name, url, description)
                        
    
            query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Stored record\n")
            if record_for_db[1].replace(' ', '') != '':
                crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","")


if __name__ == '__main__':
    '''
    Description: XLSX Crawler for Republic of Moldova
    '''
    name = 'The Government of the Republic of Moldova'
    description = "This dataset is provded by the Moldovan government. The dataset contains information from the business and companies register of the Republic of Moldova, which includes information about legal entities registered in the country. The information available in this dataset includes the legal name of each entity, its registration number, the date it was registered, its legal address, and other details about its legal status, such as whether it is active or inactive. "
    entity_type = 'Company/Organization'
    source_type = 'XLSX'
    countries = 'Republic of Moldova'
    category =  'Official Registry'
    url = "https://date.gov.md/ro/system/files/resources/2023-06/2023.06.19%20Company.xlsx"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
