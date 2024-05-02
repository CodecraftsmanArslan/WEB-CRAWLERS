"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import json, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Directory of Trade and Industry',
    'COUNTRY' : 'Monaco',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://teleservice.gouv.mc/rci/recherche?value=+__&pageSize=15", 
                        "Source Description": "The Directory of Trade and Industry in Monaco is a government agency responsible for the regulation, promotion, and development of trade and industry in the Principality of Monaco. It serves as a central authority for businesses operating within Monaco's borders, providing support, information, and resources to entrepreneurs, investors, and local businesses."},
    'URL' : 'https://teleservice.gouv.mc/rci/recherche?value=+__&pageSize=15',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED':False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Monaco Official Registry"
}

ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

monaco_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = monaco_crawler.get_requests_helper()
flag = True
arguments = sys.argv
PAGE_NUM = int(arguments[1]) if len(arguments)>1 else 1
def crawl():  
            for page in range(PAGE_NUM, 1369):
                print("Page Number:",page)
                API_URL="https://teleservice.gouv.mc/rci/recherche/page?value=%20_&size=15&page={}&_=1691063933187".format(page)
                res = request_helper.make_request(API_URL, verify=False)
                COOKIES = ''
                COOK = res.cookies.get_dict()
                for key in COOK:
                        COOKIES += f'{key}={COOK[key]};'
                payload = {
                "value": "__",
                "size": 15,
                "page": page,
                "_": 1691063933187
                }
                headers={
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Cookie": COOKIES,
                    "Host": "teleservice.gouv.mc",
                    "Referer": "https://teleservice.gouv.mc/rci/recherche?value=+_&pageSize=15",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"
                    }
                response = request_helper.make_request(API_URL, method="GET", params=payload, headers=headers)
                data_dict = json.loads(response.text)
                # Access the "data" array
                data_array = data_dict.get('data', [])
                numero_rci_lists = [item['numeroRci'] for item in data_array]
                for data in data_array:
                    DATA_URL="https://teleservice.gouv.mc/rci/extrait/{}?lang=en".format(data['numeroRci'])
                    response = request_helper.make_request(DATA_URL)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    p_elements = soup.find_all('p', class_=['mb-2', 'mb-0'])
                    data_dict = {}
                    for p_element in p_elements:
                        key = p_element.find('strong').text.strip()
                        value = p_element.contents[-1]
                        data_dict[key] = value
                    first_name_elements = soup.find_all('p')
                    for first_name_element in first_name_elements:
                          p_text = first_name_element.get_text() 
                          if "First Name:" in p_text:
                                first_name = p_text.split(':')[-1].strip()
                                data_dict['first_name'] = first_name
                    state_elements=soup.find_all('div', class_='badge-success')
                    if len(state_elements) >= 2:
                        second_state_element = state_elements[1]
                        state_text = second_state_element.find('span').text
                        data_dict['state'] = state_text
                    NAME = data_dict.get('Company name:', '')
                    reg_number = data_dict.get('RCI Number:', '')
                    type = data_dict.get('Legal form:', '')
                    state = data_dict.get('state', '')
                    industries = data_dict.get('Activity:', '').replace("%","%%")
                    # Additional_detail; type:Establishment_information
                    type_of_establishment =data_dict.get('Type of establishment:', '')
                    sign_of_establishment =data_dict.get('Sign of the establishment:', '')
                    activity_of_establishment =data_dict.get('Activity of the establishment:', '')
                    address =data_dict.get('Address:', '').replace(";",",")
                    establishment_number=data_dict.get('Statistical Identification Number (SIN*) of the main establishment:', '')
                    # people_detail
                    name_ =data_dict.get('Name:', '')
                    designation =data_dict.get('Function:', '')
                    first_name =data_dict.get('first_name', '')    
                    DATA = {
                        "name": NAME,
                        "type": type,
                        "status":data['etat'],
                        "industries": industries,
                        "registration_number": reg_number,
                        "addresses_detail":[
                            {
                                "type":"general_address",
                                "address": address

                            }
                        ],
                        "additional_detail": [
                            {
                                "type": "establishment_information",
                                "data": [
                                      {
                                    "establishment_type": type_of_establishment,
                                    "establishment_sign": sign_of_establishment,
                                    "establishment_number": establishment_number,
                                    "activity": activity_of_establishment
                                      }
                                ]
                            }
                        ],
                        "people_detail": [
                            {
                                "name": name_ + ' ' + first_name,
                                "designation": designation
                            }
                        ]
                    }
                    ENTITY_ID =monaco_crawler.generate_entity_id(reg_number=reg_number)
                    BIRTH_INCORPORATION_DATE = ''
                    DATA =monaco_crawler.prepare_data_object(DATA)
                    ROW =monaco_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                    monaco_crawler.insert_record(ROW)          
            return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
    log_data = {
            "status": 'success',
            "error": "",
            "url": meta_data['URL'],
            "source_type": meta_data['SOURCE_TYPE'],
            "data_size": DATA_SIZE,
            "content_type": CONTENT_TYPE,
            "status_code": STATUS_CODE,
            "trace_back": "",
            "crawler": "HTML"
        }
    monaco_crawler.db_log(log_data)
    monaco_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    monaco_crawler.db_log(log_data)
   