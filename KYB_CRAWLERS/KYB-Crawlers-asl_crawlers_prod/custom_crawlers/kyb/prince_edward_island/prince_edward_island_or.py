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
    'CRAWLER_NAME': 'Prince Edward Island Original Registry Official Registry'
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
        corporate__url = 'https://wdf.princeedwardisland.ca/api/workflow'

        payload = {"appName":"LegacyBusiness","featureName":"LegacyBusiness",
                "metaVars":{"service_id":'null',"save_location":'null'},
                "queryVars":{"service":"LegacyBusiness","activity":"LegacyBusinessView",
                "business_number":f"{number}","business_type":"9"},
                "queryName":"LegacyBusinessView"}

        registry_original_response = request_helper.make_request(corporate__url, method="POST",json=payload)
        if registry_original_response.status_code == 500:
            print("No data found")
            continue
        original_data = registry_original_response.json()
        people_detail = []
        try:
            pattern = r"([A-Za-z]+ [A-Za-z]+) - ([A-Za-z, ]+)"
            matches = re.findall(pattern, original_data['data']['data']['keyValuePairs']['Officer(s)'])
            for match in matches:
                offices = {"name": match[0], "designation": match[1]} 
                people_detail.append(offices)

            # Extract names and designations
            Director_pattern = r"([A-Za-z]+ [A-Za-z]+)\n"
            names = re.findall(Director_pattern, original_data['data']['data']['keyValuePairs']['Director(s)'])
            designations = ["director"] * len(names)
            for name, designation in zip(names, designations):
                people_detail.append({"name": name, "designation": designation})

            Shareholders_name = re.findall(Director_pattern, original_data['data']['data']['keyValuePairs']['Shareholder(s)'])
            shareholders_designations = ["shareholders"] * len(Shareholders_name)
            for Shareholders_name, shareholders_designations in zip(Shareholders_name, shareholders_designations):
                people_detail.append({"name": Shareholders_name, "designation": shareholders_designations})
        except:
            people_detail = []
        if original_data['data']['data']['keyValuePairs'].get('Chief Agent',"") !="":
            agent= {
                "name":original_data['data']['data']['keyValuePairs'].get('Chief Agent',"").split("\n")[0].strip(),
                "address":"".join(original_data['data']['data']['keyValuePairs'].get('Chief Agent',"").split("\n")[1:]).replace("\n"," ").strip(),
                "designation":"cheif_agent"
            }
            people_detail.append(agent)


        OBJ = {
            "name":original_data['data']['data']['keyValuePairs'].get('Entity Name',""),
            "registration_number":original_data['data']['data']['keyValuePairs'].get('Registration Number',""),
            "type":original_data['data']['data']['keyValuePairs'].get('Business Type',""),
            "registration_date":original_data['data']['data']['keyValuePairs'].get('Registration Date',""),
            "status":original_data['data']['data']['keyValuePairs'].get('Status',""),
            "object_type":"original_registry",
            "end_date":original_data['data']['data']['keyValuePairs'].get('Expiry Date',""),
            "jurisdiction":original_data['data']['data']['keyValuePairs'].get('Jurisdiction of Incorporation',""),
            "amalgamated_name":original_data['data']['data']['keyValuePairs'].get('Amalgamated Name',""),
            "industries":original_data['data']['data']['keyValuePairs'].get('Business In',"").replace("n/a",""),
            "category":original_data['data']['data']['keyValuePairs'].get("Business Out","").replace("n/a",""),
            "last_return_date":original_data['data']['data']['keyValuePairs'].get("Last Return Date",""),
            "addresses_detail":[
                {
                    "type":"general_address",
                    "address":original_data['data']['data']['keyValuePairs'].get("Address","").replace("\n"," ")
                }
            ],
            "people_detail":people_detail

        }
        OBJ =  prince_edward_crawler.prepare_data_object(OBJ)
        param = OBJ.get("name", "") + OBJ.get("object_type", "")
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
