import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from CustomCrawler import CustomCrawler
import requests


meta_data = {
    'SOURCE' :'Ministry of Justice of Kyrgyzstan',
    'COUNTRY' : 'Kyrgyzstan',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://register.minjust.gov.kg/register/SearchAction.seam?firstResult=163275&logic=and&cid=3028892", 
                        "Source Description": "Official portal provided by the Ministry of Justice of Kyrgyzstan. The portal allows users to search the government database of registered businesses and legal entities in Kyrgyzstan."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://register.minjust.gov.kg/register/SearchAction.seam?firstResult=163275&logic=and&cid=3028892'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Kyrgyzstan Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv

Kyrgyzstan_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  Kyrgyzstan_crawler.get_requests_helper()
s = Kyrgyzstan_crawler.get_requests_session()

def contains_text(element, desired_text):
    return desired_text in element.get_text()

def get_value(soup, desired_text, colspan_start, colspan_end):
    desired_td = soup.find(lambda element: contains_text(element, desired_text), {'colspan': str(colspan_start)})
    
    if desired_td is None:
        return ""  # Return an empty string if desired_td is not found
    
    next_td = None
    current_sibling = desired_td.find_next_sibling('td')
    
    while current_sibling:
        if current_sibling.get('colspan') == str(colspan_end):
            next_td = current_sibling
            break
        current_sibling = current_sibling.find_next_sibling('td')
    
    return next_td.get_text().replace("\"","")if next_td is not None else ""

def extract_data(url):
    page = request_helper.make_request(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    desired_text = "Электронный адрес"
    desired_td = soup.find(lambda element: contains_text(element, desired_text), {'colspan': '4'})
    parent_tr = desired_td.find_parent('tr')
    previous_tr = parent_tr.find_previous('tr')
    email= previous_tr.text.strip()

    desired_text = "Код ОКПО"
    desired_td = soup.find(lambda element: contains_text(element, desired_text), {'colspan': '4'})
    parent_tr = desired_td.find_parent('tr')
    previous_tr = parent_tr.findNext('tr')
    okpo_code=previous_tr.text.strip()


    desired_text = "Код экономической деятельности"
    desired_td = soup.find(lambda element: contains_text(element, desired_text), {'colspan': '3'})
    parent_tr = desired_td.find_parent('tr')
    previous_tr = parent_tr.find_previous('tr')
    industry_code=previous_tr.text.strip()

    people_detail = []
    if get_value(soup, "Фамилия, имя, отчество", 3, 7) !="":      
        people_detail.append({
            "designation": 'head_of_organization',
            "name": get_value(soup, "Фамилия, имя, отчество", 3, 7),
        }),
    if get_value(soup, "Учредитель (участник)", 5, 3) !="":
        people_detail.append({
            "designation": 'founder',
            "name": get_value(soup, "Учредитель (участник)", 5, 3),
        })
    additional_detail = []    
    state_regsitration_information = {
    "type": "state_regsitration_information",
    "data":[
                {
            "state_registration_status": get_value(soup, " Государственная (учетная) регистрация или перерегистрация", 3, 7),
            "date": get_value(soup, "Дата приказа", 3, 7).replace(".","-"),
            "initial_registration_date": get_value(soup, "Дата первичной регистрации (в случае государственной перерегистрации)", 3, 7)
            }
        ]
    }
    if state_regsitration_information['data'][0] != {}:
        additional_detail.append(state_regsitration_information)
    founders_information = {
    "type": "founders_information",
    "data":[
        {
            "industries": get_value(soup, "Основной вид деятельности", 3, 7),
            "industry_code":industry_code,
            "founders(individual)": get_value(soup, "Количество учредителей (участников) - физических лиц", 3, 7),
            "founder(legal_entity)": get_value(soup, "Количество учредителей (участников) - юридических лиц", 3, 7),
            "total_founders": get_value(soup, "Общее количество учредителей (участников)", 3, 7),
        }

        ]       
    }
    if founders_information['data'][0] != {}:
        additional_detail.append(founders_information) 

    OBJ = {
        "name(state_language)": get_value(soup, "Полное наименование(на государственном языке)", 4, 5),
        "name": get_value(soup, "Полное наименование на официальном языке", 4, 5),
        "aliases(state_language)": get_value(soup, "Сокрашенное наименование(на государственном языке)", 4, 5),
        "aliases(official_language)": get_value(soup, "Сокрашенное наименование(на официальном языке)", 4, 5),
        "type": get_value(soup, "Организационно-правовая форма", 4, 5),
        "foreign_enterprise": get_value(soup, "Есть ли иностранное участие", 4, 5),
        "registration_number": get_value(soup, "Регистрационный номер", 4, 5),
        "okpo_code": okpo_code,
        "tax_number": get_value(soup, "ИНН", 4, 5),
        "addresses_detail": [
            {
                "type": "general_address",
                "address":(f"{get_value(soup, 'Область', 4, 5)} {get_value(soup, 'Район', 4, 5)} {get_value(soup, 'Город/село/поселок', 4, 5)} {get_value(soup, 'Микрорайон', 4, 5)} {get_value(soup, 'Улица (проспект, бульвар, переулок и т.п.)', 4, 5)} {get_value(soup, '№ квартиры (офиса, комнаты и т.п.)', 4, 5)} {get_value(soup, '№ дома', 4, 5)}")  
            },
        ],
        "additional_detail":additional_detail,
        "contacts_detail": [
            {
                "type": "telephone",
                "value": get_value(soup, "Телефон", 4, 5)
            },
            {
                "type":"fax",
                "value":get_value(soup, "Факс", 4, 5),

            },
            {
                "type":"email",
                "value":email,
            } 
        ],
        "method_of_creation": get_value(soup, "Способ создания", 3, 7),
        "ownership_form": get_value(soup, "Форма собственности", 3, 7),
        "people_detail": people_detail,
    }

    return OBJ


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0
total = start_num * 25
try:
    base_url = "https://register.minjust.gov.kg"
    for i in range(start_num, 6846):
        url = f"https://register.minjust.gov.kg/register/SearchAction.seam?firstResult={total}"
        print("page_number",i)
        response = request_helper.make_request(url)
        response.raise_for_status()  
        print(url)
        total += 25
        r=requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")

        table_rows = soup.select('tbody[id="searchActionForm:searchAction:tb"] tr')

        
        for row in table_rows:
            link = row.select_one("td:nth-of-type(8) a")['href']
            full_link = f"{base_url}{link}"
            OBJ = extract_data(full_link)
            OBJ =  Kyrgyzstan_crawler.prepare_data_object(OBJ)
            ENTITY_ID = Kyrgyzstan_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
            NAME = OBJ['name'].replace("%",'%%')
            BIRTH_INCORPORATION_DATE = ""
            ROW = Kyrgyzstan_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            Kyrgyzstan_crawler.insert_record(ROW)

    Kyrgyzstan_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Kyrgyzstan_crawler.db_log(log_data)
    
except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        log_data = {"status": "fail",
            "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
            "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

        Kyrgyzstan_crawler.db_log(log_data)






