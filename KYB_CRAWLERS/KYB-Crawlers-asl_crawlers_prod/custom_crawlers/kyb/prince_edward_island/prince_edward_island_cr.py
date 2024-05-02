"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Corporate Registry of Prince Edward Island, Canada',
    'COUNTRY' : 'Prince Edward Island',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch", 
                        "Source Description": "Corporate Services is responsible for the registration of corporations and business names in PEI. Businesses of all types can reserve names, register, and manage their registry account information."},
    'URL' : 'https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Prince Edward Island Corporate Registry Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

prince_edward_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  prince_edward_crawler.get_requests_helper()
arguments = sys.argv
business_number = int(arguments[1]) if len(arguments)>1 else 0000
end_business_number = 999999
try:
    for number in range(business_number,end_business_number):
        print("Bussiness Number=", number)
        corporate_url = 'https://wdf.princeedwardisland.ca/api/workflow'

        payload = {"appName":"BusinessAPI","featureName":"BusinessAPI",
                    "metaVars":{"service_id":'null',"save_location":'null'},
                    "queryVars":{"service":"BusinessAPI","activity":"BusinessView","id":f"{number}"},
                    "queryName":"BusinessView"}

        corporate_reg_response = request_helper.make_request(corporate_url, method="POST",json=payload)
        STATUS_CODE = corporate_reg_response.status_code
        DATA_SIZE = len(corporate_reg_response.content)
        CONTENT_TYPE = corporate_reg_response.headers['Content-Type'] if 'Content-Type' in corporate_reg_response.headers else 'N/A'
        if corporate_reg_response.status_code == 500:
            print("No data found")
            continue
        original_data = corporate_reg_response.json()
        print(original_data['data']['data']['keyValuePairs'])

        people_detail = []
        try:
            pattern = r"([A-Za-z]+ [A-Za-z]+) - ([A-Za-z, ]+)"
            Shareholders_matches = re.findall(pattern, original_data['data']['data']['keyValuePairs']['Directors and Shareholders'])
            for match_ in Shareholders_matches:
                offices_ = {"name": match_[0], "designation": match_[1]} 
                people_detail.append(offices_)

        except Exception as e:
            print(e)
            people_detail = []
            if original_data['data']['data']['keyValuePairs'].get('Owner',"") !="":
                Owner= {
                    "name":original_data['data']['data']['keyValuePairs'].get('Owner',""),
                    "designation":"owner"
                }
                people_detail.append(Owner)

            if original_data['data']['data']['keyValuePairs'].get('Former Owner',"") !="":
                agent= {
                    "name":original_data['data']['data']['keyValuePairs'].get('Former Owner',""),
                    "designation":"former_owner"
                }
                people_detail.append(agent)


        OBJ = {
            "name":original_data['data']['data']['keyValuePairs'].get('Entity Name',""),
            "aliases":original_data['data']['data']['keyValuePairs'].get('Entity Secondary Name').replace("\n"," ").strip() if "Entity Secondary Name" not in original_data['data']['data']['keyValuePairs'] else original_data['data']['data']['keyValuePairs'].get("Trade Names","").replace("\n"," ").replace(" ","").strip(),
            "registration_number":original_data['data']['data']['keyValuePairs'].get('Registration Number',""),
            "business_number":original_data['data']['data']['keyValuePairs'].get('Business Number',""),
            "nature":original_data['data']['data']['keyValuePairs'].get('Nature of Business',""),
            "type":original_data['data']['data']['keyValuePairs'].get('Business Type',""),
            "registration_date":original_data['data']['data']['keyValuePairs'].get('Registration Date',""),
            "status":original_data['data']['data']['keyValuePairs'].get('Status',""),
            "renewal_date":original_data['data']['data']['keyValuePairs'].get('Renewal Date',""),
            "gazette_date":original_data['data']['data']['keyValuePairs'].get('Gazette Date',""),
            "corporation_type":original_data['data']['data']['keyValuePairs'].get('Corporation Type',""),
            "object_type":"corporate_registry",
            "end_date":original_data['data']['data']['keyValuePairs'].get('End Date',""),
            "expiry_date":original_data['data']['data']['keyValuePairs'].get('Expiry Date',""),
            "amalgamated_name":original_data['data']['data']['keyValuePairs'].get('Amalgamated Name',""),
            "jurisdiction":original_data['data']['data']['keyValuePairs'].get('Home Jurisdiction',""),
            "addresses_detail":[
                {
                    "type":"general_address",
                    "address":original_data['data']['data']['keyValuePairs'].get("Address","").replace("\n","").replace("&nbsp;"," ").replace("   "," ").strip()
                }
            ],
            "people_detail":people_detail,
            "previous_names_detail":original_data['data']['data']['keyValuePairs'].get("Former Name(s)","")

        }

        OBJ =  prince_edward_crawler.prepare_data_object(OBJ)
        param = OBJ.get("name", "") + OBJ.get("status", "")
        ENTITY_ID = prince_edward_crawler.generate_entity_id(OBJ['registration_number'], param)
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date","")
        ROW = prince_edward_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        prince_edward_crawler.insert_record(ROW)

    prince_edward_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    prince_edward_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    prince_edward_crawler.db_log(log_data)
