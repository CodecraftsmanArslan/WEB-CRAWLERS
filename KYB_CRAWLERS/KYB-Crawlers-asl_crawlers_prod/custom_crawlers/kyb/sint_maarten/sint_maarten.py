"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'St. Maarten Chamber of Commerce & Industry (COCI)',
    'COUNTRY' : 'Sint Maarten',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.chamberofcommerce.sx/services/business-registry/", 
                        "Source Description": "The St. Maarten Chamber of Commerce & Industry (COCI) is the official chamber of commerce for the Dutch Caribbean island of St. Maarten. It is responsible for the registration, administration, and promotion of businesses on the island. The COCI provides various services to businesses, including issuing business licenses, maintaining the commercial register, providing business information and support, and representing the interests of the business community."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.chamberofcommerce.sx/services/business-registry/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "St. Maarten Chamber of Commerce & Industry (COCI)"
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
s =  _crawler.get_requests_session()

API_URL = 'https://www.chamberofcommerce.sx/search-company.php'
HEADERS = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.chamberofcommerce.sx',
            'Origin': 'https://www.chamberofcommerce.sx',
            'Referer': 'https://www.chamberofcommerce.sx/services/business-registry/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            }

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 10001

def crawl():
    ROWS = []
    i = PAGE
    consecutive_empty_data_count = 0
    while True:
        print(i)
        body = f'companyName=&registryNumber={i}'
        res = s.post(API_URL,data=body,headers=HEADERS)
        SATAUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        data = res.json()
        if len(data) == 0 or data[0] == 0:
            consecutive_empty_data_count +=1
            i += 1
            if consecutive_empty_data_count >= 399:
                break
            continue
        consecutive_empty_data_count = 0
        data = data[0]
        i += 1
        
        if "dissolution_date" in data and data["dateOfDiscontinuation"] is not None:
            status= 'Discontinued'
        else:
            status = "Active" 
        for direct in data["directors"]:
            if direct["directorTitle"] == "Liquidator":
                status = "Discontinued after liquidator appointed"
        
        OBJ = {
                    "name": data["companyName"],
                    "registration_number": str(data["cociRegistrationNumber"]),
                    "registration_date":"",
                    "status":status,
                    "type": data["legalForm"],
                    "incorporation_date":data["incorporationDate"],
                    "industries": str(data["businessActivities"]).replace("[","").replace("]",""),
                    "dissolution_date": data["dateOfDiscontinuation"],
                    'aliases': ', '.join(data['tradeNames']),
                    "addresses_detail": [
                        {
                            "meta_detail":{},
                            "description":"",
                            "address": data["companyAddress"],
                            "type": "general_address"
                        }
                    ],
                    "people_detail": [
                        {
                            "name": director["directorName"],
                            "designation": director["directorTitle"]
                        } for director in data['directors']
                    ]
                }
        OBJ =  _crawler.prepare_data_object(OBJ)
        ENTITY_ID = _crawler.generate_entity_id(OBJ['registration_number'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = OBJ["incorporation_date"]
        ROW = _crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        ROWS.append(ROW)
        if len(ROWS) == 5:
            _crawler.insert_many_records(ROWS)
            ROWS.clear()
    _crawler.insert_many_records(ROWS)

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
