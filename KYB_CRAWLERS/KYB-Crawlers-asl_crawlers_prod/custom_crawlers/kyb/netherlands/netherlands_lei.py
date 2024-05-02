"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'Kamer van Koophandel (Chamber of Commerce)',
    'COUNTRY': 'Netherlands',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.kvk.nl/lei/zoeken/",
                      "Source Description": "The Kamer van Koophandel is the Chamber of Commerce in the Netherlands. The KVK's main statutory tasks are to operate the official national Business Register and provide businesses with information and advice."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.kvk.nl/lei/zoeken/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Netherlands LEI Official Registry" 
}

netherlands_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = netherlands_crawler.get_requests_helper()

query_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".lower()
query_list = list(query_list)

headers = {
  'Host': 'web-api.kvk.nl',
  'Origin': 'https://www.kvk.nl',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
  'api-version': '2.0'
}

start_number = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 0
end_number = 99999999

def crawl():
    for i in range(start_number, end_number):
        query = str(i).zfill(8)
        data_url = f"https://web-api.kvk.nl/lei-opgave/search?q={query}&page=1&size=15"
        while True:
            data_response = request_helper.make_request(url=data_url, method="GET", headers=headers)
            if not data_response:
                print("No data response. Retrying...")
                time.sleep(10)
                continue
            if data_response.status_code == 200:
                data = data_response.json()
                break
            else:
                print(f"Error: {data_response.status_code}")
                time.sleep(10)
        
        all_companies = data.get("results", "")
        if all_companies:
            print(f"Scraping data for {query}")
            for company in all_companies:
                name_ = company.get("legalName", "") if company.get("legalName", "") else ""
                chamber_number = company.get("registrationAuthorityEntityId", "") if company.get("registrationAuthorityEntityId", "") else ""
                address_first_line = company.get("legalAddress", "").get("firstAddressLine", "") if company.get("legalAddress", "").get("firstAddressLine", "") else ""
                address_postal_code = company.get("legalAddress", "").get("postalCode", "") if company.get("legalAddress", "").get("postalCode", "") else ""
                address_city = company.get("legalAddress", "").get("city", "") if company.get("legalAddress", "").get("city", "") else ""
                complete_address = address_first_line + " " + address_postal_code + " " + address_city
                registration_number = company.get("legalEntityIdentifier", "") if company.get("legalEntityIdentifier", "") else ""
                lei_reg_status = company.get("status", "") if company.get("status", "") else ""
                registration_date = company.get("initialRegistrationDate", "") 
                if registration_date:
                    registration_date = registration_date.split("T")[0]
                else:
                    registration_date = ""

                next_renewal_date = company.get("nextRenewalDate", "") 
                if next_renewal_date:
                    next_renewal_date = next_renewal_date.split("T")[0]
                else:
                    next_renewal_date = ""

                last_edited_date = company.get("lastPublicUpdateDate", "") 
                if last_edited_date:
                    last_edited_date = last_edited_date.split("T")[0]
                else:
                    last_edited_date = ""

                type_ = company.get("legalForm", "") if company.get("legalForm", "") else ""
                status_ = company.get("legalEntityStatus", "") if company.get("legalEntityStatus", "") else ""

                OBJ = {
                        "name": name_,
                        "chamber_of_commerce_number": chamber_number,
                        "addresses_detail": [
                            {
                                "type": "general_address",
                                "address": complete_address
                            }
                        ],
                        "registration_number": registration_number,
                        "lei_status": lei_reg_status,
                        "registration_date": registration_date,
                        "next_renewal_date": next_renewal_date,
                        "last_edited_date": last_edited_date,
                        "type": type_,
                        "status": status_
                    }         
                OBJ = netherlands_crawler.prepare_data_object(OBJ)
                ENTITY_ID = netherlands_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
                ROW = netherlands_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                netherlands_crawler.insert_record(ROW)                       
        else:
            print(f"No data for: {query}")
            continue
try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    netherlands_crawler.db_log(log_data)
    netherlands_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    netherlands_crawler.db_log(log_data)