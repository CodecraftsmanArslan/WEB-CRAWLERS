"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import warnings,json
from CustomCrawler import CustomCrawler
warnings.filterwarnings('ignore')

meta_data = {
    'SOURCE' :'Chamber of Commerce & Industry St. Eustatius & Saba business register',
    'COUNTRY' : 'St. Eustatius & Saba',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://registry.statiasabachamber.com/search", 
                        "Source Description": "The Chamber of Commerce on St. Eustatius & Saba is responsible for registering businesses, maintaining the business registry, providing information and support to entrepreneurs, and promoting economic development on the island. It serves as a vital institution for businesses and entrepreneurs in Bonaire, ensuring proper documentation and compliance with legal requirements for companies operating on the island."},
    'SOURCE_TYPE': 'HTML',
    'URL' : ' https://registry.statiasabachamber.com/search'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "St. Eustatius & Saba Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


Eustatius_Saba_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  Eustatius_Saba_crawler.get_requests_helper()
session =  Eustatius_Saba_crawler.get_requests_session()
try:
    LOGING_API = 'https://regsaasapi.regsys.ie/api/authorization/login/user'
    login_headers = {
        "Content-Type":"application/json",
        "Expires":"0",
        "Origin":"https://registry.statiasabachamber.com",
        "Pragma":"no-cache",
        "Referer":"https://registry.statiasabachamber.com/",
    }
    login_payload = '{"password":"ds12345678","username":"raza"}'

    login_response = request_helper.make_request(LOGING_API, method='POST', headers=login_headers,data=login_payload)
    login_data = login_response.json()
    
    authToken = login_data['data']['authToken']
    
    SEARCH_API = 'https://regsaasapi.regsys.ie/api/entity/search'

    headers = {
        "Expires":"0",
        "Origin":"https://registry.statiasabachamber.com",
        "Pragma":"no-cache",
        "Referer":"https://registry.statiasabachamber.com/",
        "Content-Type":'application/json; charset=utf-8',
        "Authorization":"Bearer " +authToken,
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    alphabet_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    payload = '{"bef63d7c-b1c6-40d8-b07c-09d86e53c21f":"","registeredNameSearchType":4,"registeredName":"","registeredNumber":"","registeredDateFrom":"","registeredDateTo":"","allowEmptySearchCriteriaInd":true}'
    for alphabet in alphabet_list:
        payload = json.loads(payload)
        payload['registeredName'] = alphabet
        payload = json.dumps(payload)
        
        search_response = request_helper.make_request(SEARCH_API, method='POST', headers=headers,data=payload)
        STATUS_CODE = search_response.status_code
        DATA_SIZE = len(search_response.content)
        CONTENT_TYPE = search_response.headers['Content-Type'] if 'Content-Type' in search_response.headers else 'N/A'
        
        search_data = search_response.json()
        for data in search_data['data']:
            entity_id = data['entityId']
            DATA_API = f'https://regsaasapi.regsys.ie/api/entity/{entity_id}'
            print(DATA_API)
            data_repsone = request_helper.make_request(DATA_API, headers=headers)
            all_data = data_repsone.json()
            data_ = all_data['data']
            FILLLING_API = f"https://regsaasapi.regsys.ie/api/enquiry/products/documents/{entity_id}"
            # FILLLING_API = "https://regsaasapi.regsys.ie/api/enquiry/products/documents/16858"
            filling_response  =request_helper.make_request(FILLLING_API, headers=headers)
            filling_data = filling_response.json()
            if len(filling_data) == 0:
                fillings_details =[]
            else:
                fillings_details =[]
                for filling_detail in filling_data['data']:
                    filing_dict = {
                        "title":filling_detail['docReferenceName'] if filling_detail['docReferenceName'] is not None else "",
                        "filing_code":filling_detail['submissionRefNum'] if filling_detail['submissionRefNum'] is not None else "",
                        "meta_detail":{
                            "submission_date":filling_detail['submissionRegisteredDate'].split("T")[0] if filling_detail['submissionRegisteredDate'] is not None else ""
                        },
                        "date":filling_detail['submissionEffectiveDate'].split("T")[0] if filling_detail['submissionEffectiveDate'] is not None else ""
                    }
                    fillings_details.append(filing_dict)
                
            OBJ = {
                "name":data_['entityRegName'],
                "registration_number":data_['entityRegNumber'],
                "type":data_['entityTypeDesc'],
                "registration_date":data_["entityRegDate"].split("T")[0] if data_['entityRegDate'] is not None else "",
                "status":data_['entityStatusDesc'],
                "trade_name":data_['entityRegName'],
                "fillings_detail":fillings_details,
            }

            OBJ =  Eustatius_Saba_crawler.prepare_data_object(OBJ)
            ENTITY_ID = Eustatius_Saba_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = Eustatius_Saba_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            Eustatius_Saba_crawler.insert_record(ROW)
        
    Eustatius_Saba_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Eustatius_Saba_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    Eustatius_Saba_crawler.db_log(log_data) 