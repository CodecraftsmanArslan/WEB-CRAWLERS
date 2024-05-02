"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import json
from CustomCrawler import CustomCrawler
from datetime import datetime

meta_data = {
    'SOURCE' :'Digitalna komora',
    'COUNTRY' : 'Croatia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://digitalnakomora.hr/e-gospodarske-informacije/poslovne-informacije/vodici", 
                        "Source Description": "The Digital Chamber, a communication platform for business entities, public administration and citizens, is a project of the Croatian Chamber of Commerce, co-financed by the European Fund for Regional Development from the Operational Program Competitiveness and Cohesion"},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://digitalnakomora.hr/e-gospodarske-informacije/poslovne-informacije/vodici'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Croatia_kyb_crawler"
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
requests_helper = _crawler.get_requests_helper()

body = {"email":"lahrasab@letresearch.com","password":"mKe4UPAD!3ZwaX6"}
json_data = json.dumps(body)

headers = {
    "Content-Type": "application/json"
}

response = requests_helper.make_request("https://cms.digitalnakomora.hr/hgk/user/login","POST", data=json_data, headers=headers, verify=False, timeout=60*60, max_retries=10)
cookies = response.cookies
cookie_set = ""
# Iterate over the cookies
for cookie in cookies:
    cookie_set += cookie.name+"="+cookie.value+";"


API_URL = 'https://newregister.bcci.bg/edipub/CombinedReports/SrcCombined'
HEADERS = {
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie":cookie_set,
        "Referer": "https://digitalnakomora.hr/pretraga/poslovni-subjekti",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Type": "application/json"
    }

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 1



def get_blocked_status(value):
    if value == 0:
        return "Not Blocked"
    if value == 1:
        return "Blocked"
    return value


def fill_null_fields(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if value is None:
                data[key] = ""
            elif isinstance(value, (dict, list)):
                fill_null_fields(value)
    elif isinstance(data, list):
        for item in data:
            fill_null_fields(item)

    return data

def convert_date(date_string):
    
    if date_string:
        date_string = date_string.rstrip('.')
        date = datetime.strptime(date_string, "%d.%m.%Y")
        formatted_date = date.strftime("%d-%m-%Y")
        return formatted_date
    return ""

def crawl():
    ROWS = []
    i = PAGE
    consecutive_empty_data_count = 0
    while True:
        print("page_number :", i)
        BODY={"searchInput":"_","sortByColumn":"PuniNaziv","sortOrder":1,"pageSize":100,"pageNumber":i}
        json_data = json.dumps(BODY)
        res = requests_helper.make_request("https://digitalnakomora.hr/HGKGospodarskaMrezaAPI/api/PoslovniSubjekt/GetFiltered","POST",data=json_data, headers=HEADERS, verify=False, timeout=60*60, max_retries=10)

        SATAUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        response = res.json()
        if response is None:
            continue

        if response is not None and 'data' in response and 'items' in response['data'] and len(response['data']['items']) == 0:
            consecutive_empty_data_count +=1
            i += 1
            time.sleep(60)
            if consecutive_empty_data_count >= 20:
                break
            continue
        consecutive_empty_data_count = 0
        i += 1

        data_items = response['data']['items']
        

        if len(data_items) > 0:

            for data in data_items:

                detail_api = f"https://digitalnakomora.hr/HGKClaniceAPI/api/PoslovniSubjekt/PoslovniSubjektInfo/{data['id']}"
                detail_res = requests_helper.make_request(detail_api,"GET", headers=HEADERS, verify=False, timeout=60*60, max_retries=10)
                
                details_response = fill_null_fields(detail_res.json()) 
                if ('data' in details_response and 'info' in details_response['data'] and 'kratkiNaziv' in details_response['data']['info']) or ('data' in details_response and 'info' in details_response['data'] and 'mbs' in details_response['data']['info']):
                    OBJ = {
                        "name": details_response['data']['info']["kratkiNaziv"].strip(),
                        "registration_number": str(details_response['data']['info']['mbs']),
                        "registration_date":"",
                        "type": details_response['data']['pravniStatus']["pravniOblik"].strip().replace("'", "''"),
                        "personal_identification_number": details_response['data']['info']['oib'],
                        "industries": details_response['data']['info']['djelatnost'].strip().replace("'", "''"),
                        "number_of_employees": details_response['data']['info']['brojZaposlenih'],
                        "incorporation_date": convert_date(details_response['data']['pravniStatus']['datumIMjestoOsnivanja']) ,
                        "block_status": get_blocked_status(details_response['data']['pravniStatus']['statusBlokade']).strip().replace("'", "''"),
                        "ownership_type": details_response['data']['pravniStatus']['oblikVlasnistva'].strip().replace("'", "''").replace("%", " percent"),
                        "hgk_raating": details_response['data']['pravniStatus']['HGKRejting'].strip().replace("'", "''"),
                        "hgk_score":details_response['data']['pravniStatus']["HGKScore"].strip().replace("'", "''"),
            
                        "addresses_detail": [
                            {
                                "address": details_response['data']['info']["adresaSjedista"].strip().replace("'", "''"),
                                "type": "general_address"
                            }
                        ] if details_response['data']['info']["adresaSjedista"] else [],

                        "people_detail" : [
                            {
                                "name": director["imePrezime"].strip().replace('"', '').replace("'", "''"),
                                "designation": director["funckijaOsobe"].strip().replace("'", "''")
                            } for item in details_response['data']['info']['ljudi']
                            for director in item['osobe']
                        ] if len(details_response['data']['info']['ljudi']) > 0 else [],

                        "contacts_detail": [
                            {
                                'type': "email",
                                'value': details_response['data']['kontakt']['emailSudreg'].strip().replace("'", "''")
                            } 
                        ] if details_response['data']['kontakt']['emailSudreg'] else []
                    }
                else:
                    continue
                OBJ = _crawler.prepare_data_object(OBJ) 
                ENTITY_ID = _crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
                NAME = OBJ['name']
                BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date') if OBJ.get('incorporation_date') else ''
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
