"""Import required library"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from random import randint
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE': "Canada''s Business Registries",
    'COUNTRY': 'Canada',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://beta.canadasbusinessregistries.ca/search",
                      "Source Description": "We can search for a business by name or number (either Business Number or Registry ID) through this registry. The results will show the legal name, status, location, province or territory where the business is registered, and a direct link to the official registry source for more details."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://beta.canadasbusinessregistries.ca/search'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Canada Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv

canada_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = canada_crawler.get_requests_helper()

start_number = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 1000000
end_number = 999000000

payload={}

headers = {
  'authority': 'searchapi.mrasservice.ca',
  'Origin': 'https://beta.canadasbusinessregistries.ca',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

def province_full(name):
     prov_name = name.replace("BC", "British Columbia").replace("ON", "Ontario").replace("AB", "Alberta").replace("SK", "Saskatchewan").replace("MB", "Manitoba").replace("QC", "Québec").replace("NS", "Nova Scotia").replace("NB", "New Brunswick").replace("NL", "Newfoundland and Labrador").replace("NT", "Northwest Territories").replace("NU", "Nunavut").replace("PE", "Prince Edward Island").replace("YT", "Yukon")
     return prov_name

def get_proxy_list():
    response = request_helper.make_request("https://proxy.webshare.io/api/v2/proxy/list/download/dclobvygwpkwhkglwkfazlkbouwzulwdvcfabqpf/US/any/username/direct/-/")
    data = response.text
    lines = data.strip().split('\n')
    proxy_list = [line.replace('\r', '') for line in lines]
    return proxy_list

def make_request(url, method="GET", headers={}, timeout=10, max_retries=3, retry_interval=60, json=None, data=None):
    try:
        response = requests.request(method, url, headers=headers, timeout=timeout, json=json)
        if response.status_code == 200:
            return response
        else: raise Exception("Too Many Requests") 
    except Exception as e:
        for attempt in range(max_retries + 1):
            print(f"Request failed")
            print(f"Retrying with proxy (attempt {attempt + 1}/{max_retries + 1})...")
            
            proxy_list = get_proxy_list()
            for proxy in proxy_list:
                if len(proxy.split(':')) == 4:
                    host, port, username, password = proxy.split(':')
                    proxies = {
                        'http': f'http://{username}:{password}@{host}:{port}',
                        'https': f'http://{username}:{password}@{host}:{port}',
                    }
                    try:
                        response = requests.request(method, url, headers=headers, timeout=timeout, json=json, proxies=proxies)
                        if response.status_code == 200:
                            return response
                    except Exception as e:
                        print(f"Request with proxy failed: {e}")
            if attempt < max_retries:
                print(f"Waiting for retry in {retry_interval} seconds...")
                time.sleep(retry_interval)
    return None

def crawl():
    for i in range(start_number, end_number):
        company_id = str(i).zfill(9)
        while True:
            response = make_request(f"https://searchapi.mrasservice.ca/Search/api/v1/search?fq=keyword:%7B{company_id}%7D&lang=en&queryaction=fieldquery", headers=headers, data=payload)
            if not response:
                print("No Initial Response")
                time.sleep(10)
                continue
            if response.status_code == 200:
                company_data = response.json()
                STATUS_CODE = response.status_code
                DATA_SIZE = len(response.content)
                CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
                break
            else:
                print(f"Initial Error Code: {response.status_code}")
                time.sleep(10)

        def get_data(hierarchy, variable):
            the_data = company_details[hierarchy].get(variable, "") if company_details[hierarchy].get(variable, "") else ""
            return the_data
    
        all_prov_details = []
        addresses_detail = []

        company_details = company_data.get("docs", "") if company_data.get("docs", "") else ""
        if len(company_details) > 0:
            print(f"Scraping Reg No: {company_id}...")
            if company_details[0]["hierarchy"] == "parent":
                company_name = get_data(0, "Company_Name")
                registration_number = get_data(0, "BN")
                registry_id = get_data(0, "Juri_ID")
                address_city = get_data(0, "City")
                address_prov = get_data(0, "Reg_office_province")
                complete_address = address_city + ", " + address_prov
                if complete_address:
                    address_dict = {
                        "type": "registered_office",
                        "address": complete_address
                    }
                    addresses_detail.append(address_dict)
                status_ = get_data(0, "Status_State")
                status_date = get_data(0, "Status_Date")
                type_ = get_data(0, "Entity_Type")
                registration_date = get_data(0, "Date_Incorporated")

            if len(company_details) > 1:
                for i in range(1, len(company_details)):
                    if company_details[i]["hierarchy"] == "child":
                        province = get_data(i, "Jurisdiction")
                        business_name = get_data(i, "Company_Name")
                        if company_name == business_name:
                            business_name = ""
                        prov_registry_id = get_data(i, "Juri_ID")
                        prov_registration_date = get_data(i, "Date_Incorporated")
                        prov_reg_dict = {
                            "name": province_full(province),
                            "aliases": business_name,
                            "prov_registry_id": prov_registry_id,
                            "prov_reg_date": prov_registration_date
                        }
                        all_prov_details.append(prov_reg_dict)

            OBJ = {
                "name": company_name,
                "registration_number": registration_number,
                "registry_id": registry_id,
                "addresses_detail": addresses_detail,
                "status": status_,
                "status_date": status_date,
                "type": type_,
                "registration_date": registration_date,
                "additional_detail": [
                    {
                        "type": "provincial_registration_info",
                        "data": all_prov_details
                    }
                ]
            }

            print(OBJ)

            OBJ = canada_crawler.prepare_data_object(OBJ)
            ENTITY_ID = canada_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
            ROW = canada_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
            canada_crawler.insert_record(ROW) 

            time.sleep(randint(1,2))

        else:
            print(f"No data found for: {company_id}!")

    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE 

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    canada_crawler.db_log(log_data)
    canada_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}
    canada_crawler.db_log(log_data)