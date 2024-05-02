"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
import requests,os

meta_data = {
    'SOURCE' :'Bonaire Chamber business register',
    'COUNTRY' : 'Bonaire',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://registry.bonairechamber.com/search", 
                        "Source Description": "The Chamber of Commerce on Bonaire is responsible for registering businesses, maintaining the business registry, providing information and support to entrepreneurs, and promoting economic development on the island. It serves as a vital institution for businesses and entrepreneurs in Bonaire, ensuring proper documentation and compliance with legal requirements for companies operating on the islando"},
    'URL' : 'https://registry.bonairechamber.com/search',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bonaire Official Registry"
}

ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

bonaire_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  bonaire_crawler.get_requests_helper()

def crawl():  
    
        # organization_detail
        LOGIN_URL = "https://regsaasapi.regsys.ie/api/authorization/login/user"
        headers={
            'content-type':'application/json',
            'expires':'0',
            'origin':'https://registry.bonairechamber.com',
            'pragma':'no-cache',
            'referer':'https://registry.bonairechamber.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }
        BODY='{"username":"Test1","password":"Ds@12345"}'
        session = request_helper.create_requests_session()
        res = session.post(LOGIN_URL, headers=headers, data=BODY)
        tokenization=res.json()
        token=tokenization['data']['authToken']
        API_URL="https://regsaasapi.regsys.ie/api/entity/search"
       
        headers = {
            'Accept': '*/*',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'expires':'0',
            'origin':'https://registry.bonairechamber.com',
            'pragma':'no-cache',
            'referer':'https://registry.bonairechamber.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

        }
        arguments = sys.argv
        start_number = int(arguments[1]) if len(arguments)>1 else 1
        
        for number in range(start_number, 16000):
            print("registeredNumber",number,'\n')
            if number >= 14900: # In the sourece the end records in 1406 so we can break this loop 14900 If any number are availbe in soure we can store it into DB.   
                break
            payload = {
                "registeredNameSearchType": 4,
                "registeredName": "",
                "registeredNumber": number,
                "registeredDateFrom": "",
                "registeredDateTo": "",
                "allowEmptySearchCriteriaInd": True
            }
            res_ = requests.post(API_URL, headers=headers, json=payload)
            STATUS_CODE = res.status_code
            DATA_SIZE=len(res.content)
            response_data=res_.json()['data']
            CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
            if response_data:
                for entity in response_data:
                    entity_id = entity['entityId']
                    API_URL1=f'https://regsaasapi.regsys.ie/api/entity/{entity_id}'
                    headers_1 = {
                        'Accept': '*/*',
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                    'expires':'0',
                    'origin':'https://registry.bonairechamber.com',
                    'pragma':'no-cache',
                    'referer':'https://registry.bonairechamber.com/',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

                    }
                    FILING_API=f'https://regsaasapi.regsys.ie/api/enquiry/products/documents/{entity_id}'
                    res_1= requests.get(API_URL1, headers=headers_1)
                    res_2= requests.get(FILING_API, headers=headers_1)
                    
                    response_data=res_1.json()['data']
                    filing_response_data=res_2.json()['data']
                    
                    NAME = response_data['entityRegName']
                    reg_number = response_data['entityRegNumber']
                    type = response_data['entityTypeDesc']
                    reg_date = response_data['entityRegDate'].split('T')[0]
                    status = response_data['entityStatusDesc']
                    trades = response_data['entityNames']
                    trade_names = []
                    if trades:
                        for trade in trades:
                            trade_name = trade['name']
                            trade_names.append(trade_name)
                    trade_names_formatted = ', '.join(trade_names)
                    filings_details=[]
                    if filing_response_data:
                        for filing_detail in filing_response_data:
                            title = filing_detail['docReferenceName']
                            filing_code=filing_detail['submissionRefNum']
                            submission_date=filing_detail['submissionRegisteredDate'].split('T')[0] if filing_detail['submissionRegisteredDate'] is not None and "T" in filing_detail['submissionRegisteredDate'] else ""
                            try:
                                date = filing_detail['submissionEffectiveDate'].split('T')[0]
                            except:
                                date = ""
                            filing_details = {
                                'title': title,
                                'filing_code': filing_code,
                                'date': date,
                                'meta_detail': {
                                    'submission_date': submission_date,
                                    }
                            }
                            filings_details.append(filing_details)
                         
                    DATA = {
                    "name":NAME,
                    "type":type,
                    "status":status,
                    "registration_number":reg_number,
                    "registration_date":reg_date,
                    "trade_name":trade_names_formatted,
                    "fillings_detail":filings_details
                    }
                    
                    ENTITY_ID = bonaire_crawler.generate_entity_id(reg_number=reg_number, company_name=NAME)
                    BIRTH_INCORPORATION_DATE = ''
                    DATA = bonaire_crawler.prepare_data_object(DATA)
                    ROW = bonaire_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                    bonaire_crawler.insert_record(ROW)          
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
    bonaire_crawler.db_log(log_data)
    bonaire_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    bonaire_crawler.db_log(log_data)
   
