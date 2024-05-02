"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import json
from operator import le
from CustomCrawler import CustomCrawler
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from requests.adapters import Retry

meta_data = {
    'SOURCE' :'Registro Nacional de Contratistas (RNC)',
    'COUNTRY' : 'Venezuela',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://rncenlinea.snc.gob.ve/reportes/consulta_publica?p=1", 
                        "Source Description": "The Registro Nacional de Contratistas (RNC) in Venezuela is an organization responsible for maintaining an updated and centralized registry of companies and individuals who wish to participate in public procurement processes in the country."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://rncenlinea.snc.gob.ve/reportes/consulta_publica?p=1'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Venezuela_kyb_crawler"
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
s =  _crawler.get_requests_session()


"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 3000



def crawl():

    ROWS = []
    consecutive_empty_data_count = 0
    i = PAGE
    while True:
        
        print("record_number :", i)
        api_url = f"https://rncenlinea.snc.gob.ve/planilla/index/{i}"

        retry = Retry(total=5, backoff_factor=0.5)
        s.mount("http://", requests.adapters.HTTPAdapter(max_retries=retry))
        s.mount("https://", requests.adapters.HTTPAdapter(max_retries=retry))
       
        response = s.get(api_url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")

        if "The page you were looking for doesn't exist (404)" in response.text:
            consecutive_empty_data_count +=1
            print("The page you were looking for doesn't exist")
            i += 1
            if consecutive_empty_data_count >= 10000:
                break
            continue

        consecutive_empty_data_count = 0
        pattern = re.compile("Número de RIF.:")
        registration_number_element = soup.find(string=pattern) 
        registration_number = registration_number_element.find_next('td').text.strip() if registration_number_element else ''

        pattern = re.compile("Nombre y Apellido o Razón Social:")
        name_element = soup.find(string=pattern) 
        name = name_element.find_next('td').text.strip().replace("'", "''").replace("%", "%%") if name_element else ''

        pattern = re.compile("Tipo de Persona:")
        type_of_person_element = soup.find(string=pattern) 
        type_of_person = type_of_person_element.find_next('td').text.strip() if type_of_person_element else ''

        pattern = re.compile("Denominación Comercial:")
        type_element = soup.find(string=pattern) 
        type = type_element.find_next('td').text.strip() if type_element else ''

        pattern = re.compile("Siglas:")
        aliases_element = soup.find(string=pattern) 
        aliases = aliases_element.find_next('td').text.strip().replace("'", "''").replace("%", "%%")  if aliases_element else ''

        activities_info_tr = soup.find_all('tr', class_='fondoP_4')
        
        additional_detail = list()

        if len(activities_info_tr) > 0:
            activity_data = list()
            for row in activities_info_tr:
                cells = row.find_all('td')
                if len(cells) > 3:
                    activities_info = dict()
                    activities_info['activity_name'] = cells[1].text.strip()
                    activities_info['experience'] = cells[2].text.strip()
                    activities_info['major_activity'] = cells[3].text.strip()
                    activities_info['activity_type'] = cells[4].text.strip()
                    activity_data.append(activities_info)
            
            if len(activity_data) > 0:
                all_activities = dict()
                all_activities['type'] = "activities_information"
                all_activities['data'] = activity_data
                additional_detail.append(all_activities)
        
        
        pattern = re.compile("Observaciones del Contratista")
        observations_el = soup.find(string=pattern)

        if observations_el:
            observation_table = observations_el.findParent("table")
            table_rows = observation_table.find_all("tr") if observation_table else []
            if len(table_rows) > 2:
                observation_data = list()
                for row in table_rows[2:]:
                    cells = row.find_all("td")
                    if len(cells) > 1:
                        observation_info = dict()
                        observation_info['date'] = cells[0].text.strip()
                        observation_info['observation_type'] = cells[1].text.strip()
                        observation_info['description'] = cells[2].text.strip().replace("'", "''").replace("%", "%%")
                        observation_data.append(observation_info)

                if len(observation_data) > 0:
                    all_observations = dict()
                    all_observations['type'] = "contractor_observations_information"
                    all_observations['data'] = observation_data
                    additional_detail.append(all_observations)

        OBJ = {
            "name": name,
            "registration_number": registration_number,
            "type": type,
            "type_of_person":type_of_person,
            'aliases': aliases,
            
        }
        OBJ['additional_detail'] = additional_detail
    
        OBJ = _crawler.prepare_data_object(OBJ)
        ENTITY_ID = _crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = _crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        _crawler.insert_record(ROW)

        i += 1

    return SATAUS_CODE,DATA_SIZE, CONTENT_TYPE
   
try:
    SATAUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    _crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":"",  "crawler":"HTML"}
    _crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    _crawler.db_log(log_data)
