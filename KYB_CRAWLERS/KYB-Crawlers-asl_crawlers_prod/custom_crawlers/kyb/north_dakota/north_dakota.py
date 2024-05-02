"""Set System Path"""
import sys, os, traceback
from CustomCrawler import CustomCrawler
from dotenv import load_dotenv
load_dotenv()

ENV =  {
            'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')   
        }

meta_data = {
    'SOURCE' :'North Dakota Secretary of State',
    'COUNTRY' : 'North Dakota',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://firststop.sos.nd.gov/search/business", 
                        "Source Description": "The North Dakota Secretary of State serves as the official state government office responsible for a variety of administrative and regulatory functions in North Dakota, USA. The office oversees business registrations, elections, notary services, and other official matters."},
    'URL' : 'https://firststop.sos.nd.gov/search/business',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': True,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'North Dakota'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

north_dakota_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  north_dakota_crawler.get_requests_helper()

# default 0000000015 to 0000274165
start = 15
end = 274165

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = sys.argv[1]
    if len(sys.argv)>2:
        end = sys.argv[2] 
try:
    for i in range(int(start), int(end) + 1):
        formatted_number = str(i).zfill(10)
        print(i)
        url = 'https://firststop.sos.nd.gov/api/Records/businesssearch'
        data = {
            "SEARCH_VALUE":formatted_number,
            "STARTS_WITH_YN":False,
            "ACTIVE_ONLY_YN":False
        }
        headers = {
            "authorization" : "undefined",
            "referer" : "https://firststop.sos.nd.gov/search/business"
        }
        response = request_helper.make_request(url, method="POST", json=data)
        try:
            json_data = response.json()
        except AttributeError:
            continue
        STATUS_CODE = response.status_code
        if 'rows' in json_data:
            for row in json_data['rows'].values():
                additional_detail = []
                addresses_detail = []
                people_detail = []
                fillings_detail = []

                id = row['ID']
                NAME = row['TITLE'][0].replace("%", "%%") if row['TITLE'][0] is not None else ""
                registration_number = row['RECORD_NUM']
                url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{id}/false"
                response = request_helper.make_request(url, headers=headers)
                try:
                    json_data = response.json()
                except AttributeError:
                    continue
                values = {}
                for item in json_data['DRAWER_DETAIL_LIST']:
                    label = item['LABEL']
                    value = item['VALUE']
                    values[label] = value

                filing_type = values.get('Filing Type').replace('%', '%%').replace("'", "").replace("  ", "") if values.get('Filing Type') is not None else ""
                status = values.get('Status').replace('%', '%%').replace("'", "").replace("  ", "") if values.get('Status') is not None else ""

                if values.get('Standing - AR') is not None:
                    additional_detail.append({
                        "type": "standing_information",
                        "data":[{
                            "standing_ar": values.get('Standing - AR').replace('%', '%%').replace("'", "") if values.get('Standing - AR') is not None else "",
                            "standing_ra": values.get('Standing - RA').replace('%', '%%').replace("'", "") if values.get('Standing - RA') is not None else "",
                            "standing_other": values.get('Standing - Other').replace('%', '%%').replace("'", "") if values.get('Standing - Other') is not None else ""
                        }]
                    })

                formed_in = values.get('Formed In').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Formed In') is not None else ""
                term_of_duration = values.get('Term of Duration').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Term of Duration') is not None else ""
                initial_filing_date = values.get('Initial Filing Date').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Initial Filing Date') is not None else ""

                if values.get('Principal Address') is not None and values.get('Principal Address') != "":
                    addresses_detail.append({
                        "type": "general_address",
                        "address": values.get('Principal Address').replace('\n', ' ').replace("%", "%%").replace("'", "").replace("  ", "")
                    })

                if values.get('Mailing Address') is not None and values.get('Mailing Address') != "":
                    addresses_detail.append({
                        "type": "postal_address",
                        "address": values.get('Mailing Address').replace('\n', ' ').replace("%", "%%").replace("'", "").replace("  ", "")
                    })

                ar_due_date = values.get('AR Due Date').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('AR Due Date') is not None else ""
                industries = values.get('Nature of Business').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Nature of Business') is not None else ""
                expiration_date = values.get('Expiration Date').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Expiration Date') is not None else ""

                registered_agent = values.get('Registered Agent').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Registered Agent') is not None else ""
                if registered_agent is not None and registered_agent != "":
                    registered_agent = registered_agent.replace("%", "%%")
                    people_detail.append({
                        "name": registered_agent.split('\n')[0] if registered_agent is not None else "",
                        "address": ', '.join(registered_agent.split('\n')[1:]) if registered_agent is not None else "",
                        "designation": "registered_agent"
                    })

                commercial_registered_agent = values.get('Commercial Registered Agent').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Commercial Registered Agent') is not None else ""
                if commercial_registered_agent is not None and commercial_registered_agent != "":
                    commercial_registered_agent = commercial_registered_agent.replace("%", "%%")
                    people_detail.append({
                        "name": commercial_registered_agent.split('\n')[0] if commercial_registered_agent is not None else "",
                        "address": ', '.join(commercial_registered_agent.split('\n')[1:]) if commercial_registered_agent is not None else "",
                        "designation": "commercial_registered_agent"
                    })

                if values.get('Owner Name') is not None:
                    people_detail.append({
                        "name": values.get('Owner Name'),
                        "address": values.get('Owner Address').replace('\n', ' ').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Owner Address') is not None else "",
                        "designation": "owner"
                    })
                
                url = f"https://firststop.sos.nd.gov/api/History/business/{registration_number}"
                response = request_helper.make_request(url, headers=headers)
                try:
                    json_data = response.json()
                except AttributeError:
                    pass
                if "AMENDMENT_LIST" in json_data:
                    for item in json_data['AMENDMENT_LIST']:
                        fillings_detail.append({
                            "filing_type": item['AMENDMENT_TYPE'].replace("'", "").replace("  ", "") if item['AMENDMENT_TYPE'] is not None else "",
                            "filing_code": item['AMENDMENT_NUM'].replace("'", "").replace("  ", "") if item['AMENDMENT_NUM'] is not None else "",
                            "date": item['AMENDMENT_DATE'].replace('/', '-') if "AMENDMENT_DATE" in item and item['AMENDMENT_DATE'] is not None else ""
                        })

                DATA = {
                    "name": NAME,
                    "country_name": "North Dakota",
                    "crawler_name": "custom_crawlers.kyb.north_dakota.north_dakota.py",
                    "type": filing_type,
                    "status": status,
                    "jurisdiction": formed_in,
                    "registration_number": registration_number,
                    "industries": industries,
                    "meta_detail": {
                        "term_of_duration": term_of_duration,
                        "initial_filing_date": initial_filing_date.replace('/', '-') if initial_filing_date is not None else "",
                        "accounts_receivable_date": ar_due_date.replace('/', '-') if ar_due_date is not None else "",
                        "expiration_date" : expiration_date.replace('/', '-') if expiration_date is not None else "",
                    },
                    "additional_detail": additional_detail,
                    "fillings_detail": fillings_detail,
                    "addresses_detail": addresses_detail,
                    "people_detail": people_detail
                }

                # Check if all values in meta_detail are empty
                if all(value == "" for value in DATA["meta_detail"].values()):
                    del DATA["meta_detail"]

                ENTITY_ID = north_dakota_crawler.generate_entity_id(reg_number=registration_number)
                DATA = north_dakota_crawler.prepare_data_object(DATA)
                BIRTH_INCORPORATION_DATE = ''
                ROW = north_dakota_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)

                north_dakota_crawler.insert_record(ROW)
                DATA_SIZE += 1
            
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    north_dakota_crawler.db_log(log_data)
    north_dakota_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    north_dakota_crawler.db_log(log_data)
