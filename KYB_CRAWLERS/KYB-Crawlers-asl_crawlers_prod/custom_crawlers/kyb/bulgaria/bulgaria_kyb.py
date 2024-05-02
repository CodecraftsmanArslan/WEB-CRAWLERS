"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from lxml import etree

meta_data = {
    'SOURCE' :'Bulgarian Chamber of Commerce and Industry',
    'COUNTRY' : 'Bulgaria',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://newregister.bcci.bg/edipub/CombinedReports", 
                        "Source Description": "Bulgarian Chamber of Commerce and Industry has kept a Unified Trade Register of Bulgarian companies, associations, and representation offices of foreign entities. Its main priorities and functions are aimed at serving the society and businesses by providing reliable information about the current status of the registered legal entities."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://newregister.bcci.bg/edipub/CombinedReports'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bulgarian Chamber of Commerce and Industry"
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
s =  _crawler.get_requests_session()

response = s.get("https://newregister.bcci.bg/edipub/CombinedReports")
cookie = response.headers.get('Set-Cookie')
split = cookie.split(',')
session_id = split[0].split(';')[0]
request_verification_token = split[-1].split(';')[0]

filing_soup = BeautifulSoup(response.text, "html.parser")
input_tag = filing_soup.find("input", attrs={"name": "__RequestVerificationToken"})
token = input_tag["value"]

API_URL = 'https://newregister.bcci.bg/edipub/CombinedReports/SrcCombined'
HEADERS = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": f"{session_id};{request_verification_token}",
        "Referer": "https://newregister.bcci.bg/edipub/CombinedReports",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 1


def get_checkbox(i):
    body = f"__RequestVerificationToken={token}&CompanyName=+&EIK=&BusinessActivity=&RegistrationAreaId=-1&BusinessAddressAreaId=-1&CountryForeignParticipationId=-1&Counter=0&Page={i}"
    response = s.post("https://newregister.bcci.bg/edipub/CombinedReports/SrcCombined",data=body,headers=HEADERS)
    soup2 = BeautifulSoup(response.content, 'html.parser')
    get_checkBoxs = soup2.find_all('input', {'class': 'customer'})
    all_checkbox = []
    for checkBox in get_checkBoxs:
        checkBox = checkBox.get('name')
        all_checkbox.append(checkBox)
    return all_checkbox

def crawl():
    url = "https://newregister.bcci.bg/edipub/CombinedReports/Generate"
    for i in range(PAGE,5644):
        # print("page_number :", i)
        # i = PAGE
        print("page number",i)
        arr = [False] * 10
        all_checkboxs = get_checkbox(i)
        for index in range(len(all_checkboxs)):
            arr[index] = True  # Set the current checkbox to True
            payload = f'__RequestVerificationToken={token}&CompanyName=+&EIK=&BusinessActivity=&RegistrationAreaId=-1&BusinessAddressAreaId=-1&CountryForeignParticipationId=-1&Counter=1&Page={i}'
            for j, value in enumerate(arr):
                payload += f'&{all_checkboxs[j]}={str(value).lower()}&Generate='
            
            arr[index] = False 
            res = s.post(url,data=payload,headers=HEADERS)
            SATAUS_CODE = res.status_code
            DATA_SIZE = len(res.content)
            CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A' 
            soup = BeautifulSoup(res.content, 'lxml')
            report = soup.find(id = 'report')
            item = {}
            try:
                entity_number = soup.find('b', string='Номер на субект: ').next_sibling.strip()
                item['entity_num'] = entity_number.split("/")[0]
                item['entity_date'] = entity_number.split("/")[1].replace(".","-")
            except:
                item['entity_num'], item['entity_date'] = "", ""
            entity_tag = soup.find('b', string='Номер на субект: ') if soup.find('b', string='Номер на субект: ') else ""
            try:
                item['company_name'] = entity_tag.find_next('br').next_sibling.strip()
            except:
                item['company_name'] = ""
            try:
                item['type'] = entity_tag.find_next('br').find_next('b').text.strip()
            except:
                item['type'] = ""
            try:
                item['registration_num'] = report.find('b', string='Регистриран по ДДС').next_sibling.strip() 
            except:
                item['registration_num'] = ""
            try:
                item['tex_num'] = report.find('b', string='ЕИК/Булстат: ').next_sibling.strip()
            except:
                item['tex_num'] = ""
            try:
                item['industries'] = report.find('b',string='Сфера дейност:').next_sibling.strip()
            except:
                item['industries'] = ""
            try:
                item['ownership_type'] = report.find('b', string='Вид на собствеността: ').next_sibling.strip()
            except:
                item['ownership_type'] = ""
            try:
                address_tag = report.find('b', string='Адресни данни по седалище: ')
                br_tags = address_tag.find_all_next('br')
                iteration_count = 0
                address_parts = []
                for br_tag in br_tags:
                    if br_tag.next_sibling:
                        extracted_text = br_tag.next_sibling.strip()
                        address_parts.append(extracted_text)
                        iteration_count += 1
                        if iteration_count >= 3:
                            break
                item['address'] = " ".join(address_parts)
            except:
                item['address'] = ""

            try:
                activaty_tag = report.find('b', string = 'Дейности за бизнес контакти:')
                activaty = activaty_tag.find_next('br').next_sibling.strip()
                code = activaty.split('-')[0].strip()
                name = activaty.split('-')[-1].strip()
            except:
                code ,name = "",""
            item['activaty_code'] = code
            item['activaty_name'] = name
            try:
                person_detail_tag = report.find('b',string = 'Упълномощени представители и обем на пълномощията:')
                person_detail = person_detail_tag.find_next('br').next_sibling.strip()
                person_name = person_detail.split(',')[0].strip()
                designation = person_detail.split(',')[1].strip()
                item['nationality'] = person_detail_tag.find_next('br').find_next('br').next_sibling.strip()
                item['person_name'] = person_name
                item['designation'] = designation
            except:
                item['nationality'] = ""
                item['person_name'] = ""
                item['designation'] = ""

            try:
                address_tag = report.find('b', string='Адресни данни по седалище: ')
                item['phone_num'] = address_tag.find_next('br').find_next('br').find_next('br').find_next('br').next_sibling.split(':')[-1].strip()
            except:
                item['phone_num'] = ""
            try:
                item['fax_num'] = address_tag.find_next('br').find_next('br').find_next('br').find_next('br').find_next('br').next_sibling.split(':')[-1].strip()
            except:
                item['fax_num'] = ""
            try:
                item['email'] = address_tag.find_next('br').find_next('br').find_next('br').find_next('br').find_next('br').find_next('br').find_next('a').text.strip()
            except:
                item['email'] = ""
            try:
                item['mangement_leve'] = report.find('b',string= 'Степен на управление:').next_sibling.strip()
            except:
                item['mangement_leve'] = ""
            
            additional_detail = []
            if item.get('activaty_code', '') != "":
                employee_info = {
                    "type": "activities_information",
                    "data":[
                            {
                                "activity_code":item.get('activaty_code', ''),
                                "activity_name":item.get('activaty_name', '')
                            }
                        ]
                    }
                additional_detail.append(employee_info)

            OBJ = {
                    "entity_number":item.get('entity_num',''),
                    "registration_date":item.get('entity_date',''),
                    "name":item.get('company_name','').replace('\"','').replace("\" ",""),
                    "type":item.get('type',''),
                    "registration_number":item.get('registration_num',''),
                    "tax_number":item.get('tex_num',''),
                    "addresses_detail":[
                        {
                            "type":"general_address",
                            "address":item.get('address','')
                        }
                    ],
                    "contacts_detail": [
                        {
                            "type":'phone_number',
                            "value":item.get('phone_num','')
                        },
                        {
                            "type":'email',
                            "value":item.get('email','')
                        },
                        {
                            "type":'fax_number',
                            "value":item.get('fax_num','')
                        },
                    ],
                    "industries":item.get('industries',''),
                    "ownership_type":item.get('ownership_type',''),
                    "representation_note":item.get('representation_note',''),
                    "jurisdiction":item.get('jurisdiction', ''),
                    "management_level":item.get('mangement_leve',''),
                    "people_detail":[
                        {
                            "name":item.get('person_name',''),
                            "designation":item.get('designation',''),
                            "nationality":item.get('nationality','')
                        }
                    ],
                    "additional_detail":additional_detail
                }
            print(OBJ)
            OBJ = _crawler.prepare_data_object(OBJ)
            ENTITY_ID = _crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = _crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            _crawler.insert_record(ROW)
                
    
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