"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from time import sleep
import warnings
from CustomCrawler import CustomCrawler
warnings.filterwarnings("ignore")

meta_data = {
    'SOURCE' :'Unified State Register',
    'COUNTRY' : 'Belarus',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://egr.gov.by/egrn/index.jsp?language=en", 
                        "Source Description": "The Unified State Register is a centralized database that contains comprehensive information about legal entities (such as corporations, partnerships, associations, and foundations) and individual entrepreneurs registered in Belarus. The register serves as an official record of these entities and provides a range of information that is important for legal, administrative, and commercial purposes."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://egr.gov.by/egrn/index.jsp?language=en'
}
crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Belarus Unified State Register"
}
belarus_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = belarus_crawler.get_requests_helper()

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


def crawl():
    API_URL = f'https://egr.gov.by/egrmobile/api/search/checkStatusSubject?search=Н&searchTerm=1&placeSearch=all&size=10&page=0'
    HEADERS = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    api_response = request_helper.make_request(API_URL,verify=False, headers=HEADERS)
    STATUS_CODE = api_response.status_code
    DATA_SIZE = len(api_response.content)
    CONTENT_TYPE = api_response.headers['Content-Type'] if 'Content-Type' in api_response.headers else 'N/A'
    api_data = api_response.json()
    totalElements = api_data['totalElements']
    totalPages = api_data['totalPages']
    page_size = totalElements
    print('Total page size',page_size)
    API_URL_ = f'https://egr.gov.by/egrmobile/api/search/checkStatusSubject?search=Н&searchTerm=1&placeSearch=all&size={page_size}&page=0'
    response = request_helper.make_request(API_URL_,verify=False, headers=HEADERS)
    print(API_URL_)
    json_data = response.json()
    for content in json_data['content']:
        pan_number = content['pan']
        # pan_number = 500030779
        print(pan_number)
        DATA_API = f"https://egr.gov.by/egrmobile/api/v1/extracts/commonInfo?pan={pan_number}"
        data_response = request_helper.make_request(DATA_API,verify=False) 
        if data_response.status_code != 200:
            continue
        result = data_response.json() 
        
        ADDRESS_API = f'https://egr.gov.by/egrmobile/api/v1/extracts/placeLocation?pan={pan_number}'
        address_response  = request_helper.make_request(ADDRESS_API,verify=False)
        address = address_response.text
        INDUSTRIES_API = f'https://egr.gov.by/egrmobile/api/v1/extracts/mainActivity?pan={pan_number}'
        industries_response = request_helper.make_request(INDUSTRIES_API,verify=False)
        if industries_response == 200: 
            industries  =industries_response.json()
        else:
            industries= []
        try:
            industries = str(industries.get('code',""))+' '+industries.get('nameActivitysz',"")
        except:
            industries = ""
        
        DEBTS_INFORMATION_API = f'https://egr.gov.by/egrmobile/api/v1/extracts/licenses?pan={pan_number}'
        debts_response = request_helper.make_request(DEBTS_INFORMATION_API,verify=False)
        if debts_response is not None:
            debts_info  = debts_response.text
        else:
            debts_info = ""
        
        PERVIOUS_NAME_API = f"https://egr.gov.by/egrmobile/api/v1/extracts/nameHistory?pan={pan_number}"
        pervious_name_res = request_helper.make_request(PERVIOUS_NAME_API,verify=False)
        if pervious_name_res.status_code == 200:
            pervious_names = pervious_name_res.json()  
        else:
            pervious_names = []

        FILINGSDETAIL_API = f'https://egr.gov.by/egrmobile/api/v1/extracts/changes?pan={pan_number}'
        fillings_detail_res = request_helper.make_request(FILINGSDETAIL_API,verify=False)
        if fillings_detail_res == 200:
            fillings_details = fillings_detail_res.json()
        else:
            fillings_details = []
        
        fillings_details_ = []
        for detail in fillings_details:
            detail_dict = {
            "title":detail['mes'],
            "date":detail['date'],
            "meta_detail":{
                "decision":detail['number'] if detail['number'] != "None" else "" 
                }
            
            }
            fillings_details_.append(detail_dict)
        try:
            last_updated = result["dateLastEvent"].replace("T00:00:00.000+03:00","")
        except:
            last_updated = result.get("dateLastEvent","")
        
        OBJ = {
                "registration_number":result['unn'],	
                "status":result['state'],
                "registration_authority":result['nameOrgRegForDateCreateStatment'],
                "name":result['fullNameRus'],
                "aliases":result["fullNameBel"],
                "state_body":result["stateRegistration"],
                "registration_date":result["dateOfStateRegistration"].replace("T00:00:00.000+03:00",""),
                "last_updated":last_updated,
                "industries":industries,
                "debts_information":debts_info,
                "contacts_detail":[
                    {
                        "type":"phone_number",
                        "values":result['phone']
                    },
                    {
                        "type":"email",
                        "values":result['email']
                    }
                ],
                "addresses_detail":[
                    {
                        "type":"general_address",
                        "address":address
                    }
                ],
                "previous_names_detail":[
                    {
                        "name":pervious_name.get('name',""),
                        "update_date":pervious_name.get('finish',''),
                        "meta_detail":{
                            "effective_date":pervious_name.get('start',''),
                        }
                    }for pervious_name in pervious_names
                ],
                "additional_detail":[
                    {
                        "type":"exclusion_information",
                        "data":[
                            {
                                "date":result['dateDeсisionLiquidation'].replace("T00:00:00.000+03:00","") if result['dateDeсisionLiquidation'] == "Null" else "",
                                "decision":result['numberDeсisionLiquidation'],
                                "exclusion_authority":result['nameOrgRegForDateCreateStatment']
                            }
                        ]
                    },
                    {
                        "type":"liquidation_information",
                        "data":[
                            {
                                "date":result['dateDeсisionLiquidation'].replace("T00:00:00.000+03:00","") if result['dateDeсisionLiquidation'] == "Null" else "",
                                "decision_number":result['numberDeсisionLiquidation'],
                                "liquidation_authority":result['nameOrgRegForDateCreateStatment']
                            }
                        ]
                    }
                ],
                "fillings_detail":fillings_details_
            }
        
        OBJ =  belarus_crawler.prepare_data_object(OBJ)
        ENTITY_ID = belarus_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = belarus_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        
        belarus_crawler.insert_record(ROW)

    return STATUS_CODE,DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    belarus_crawler.end_crawler()
    
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    belarus_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    belarus_crawler.db_log(log_data)