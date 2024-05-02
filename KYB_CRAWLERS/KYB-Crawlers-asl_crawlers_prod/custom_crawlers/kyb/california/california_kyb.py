"""Set System Path"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from dateutil import parser

meta_data = {
    'SOURCE' : 'California Secretary of State',
    'COUNTRY' : 'California',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://bizfileonline.sos.ca.gov/search/business", 
                        "Source Description": "The California Business Search provides access to available information for corporations, limited liability companies and limited partnerships of record with the California Secretary of State, with free PDF copies of over 17 million imaged business entity documents, including the most recent imaged Statements of Information filed for Corporations and Limited Liability Companies."},
    'URL' : 'https://bizfileonline.sos.ca.gov/search/business',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'California'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://bizfileonline.sos.ca.gov'

california_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  california_crawler.get_requests_helper()

def get_range():
    for i in range(0, 10000):
        yield f"{i:05d}"

    for i in range(1, 10000000000):
        yield f"{i:012d}"

# default 0000000015 to 0000274165
start = 123
end = 274165

def make_request(url, method="GET", headers={}, timeout=10, max_retries=3, retry_interval=60, json=None):
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(method, url, headers=headers, timeout=timeout, json=json)
            if response.status_code == 200:
                response.json()
                return response
        except:
            print(f"Waiting for retry in {retry_interval} seconds...")
            time.sleep(retry_interval)
    return None

def format_date(timestamp):
    try:
        datetime_obj = parser.parse(timestamp)
        return datetime_obj.strftime("%d-%m-%Y")
    except:
        return ""

def get_history_list(history_list, id):
    hist_list = []
    for item in history_list:
        if item.get("AMENDMENT_ID") == id:
            hist_list.append(item)
    return hist_list


try:
    start = sys.argv[1] if len(sys.argv) > 1 else '00000'
    flag = True
    reg_numbers = get_range()
    for reg_num in reg_numbers:
        if start != str(reg_num) and flag:
            continue
        else:
            flag = False
        print(f"Record no: {reg_num}")
        url = f'https://bizfileonline.sos.ca.gov/api/Records/businesssearch'
        data = {
            "SEARCH_VALUE": reg_num,
            "SEARCH_FILTER_TYPE_ID": "0",
            "SEARCH_TYPE_ID": "1",
            "FILING_TYPE_ID": "",
            "STATUS_ID": "",
            "FILING_DATE": {"start": None, "end": None},
            "CORPORATION_BANKRUPTCY_YN": False,
            "CORPORATION_LEGAL_PROCEEDINGS_YN": False,
            "OFFICER_OBJECT": {"FIRST_NAME": "", "MIDDLE_NAME": "", "LAST_NAME": ""},
            "NUMBER_OF_FEMALE_DIRECTORS": "99",
            "NUMBER_OF_UNDERREPRESENTED_DIRECTORS": "99",
            "COMPENSATION_FROM": "",
            "COMPENSATION_TO": "",
            "SHARES_YN": False,
            "OPTIONS_YN": False,
            "BANKRUPTCY_YN": False,
            "FRAUD_YN": False,
            "LOANS_YN": False,
            "AUDITOR_NAME": ""
        }
        headers = {
            "Authorization" : "undefined",
            "Origin": "https://bizfileonline.sos.ca.gov",
            "Referer": "https://bizfileonline.sos.ca.gov/search/business",
        }
        response = make_request(url, method="POST", json=data, headers=headers, retry_interval=60*60, max_retries=10)
        if response is None:
            continue
        json_data = response.json()            
        STATUS_CODE = response.status_code
        if 'rows' in json_data:
            for row in json_data['rows'].values():
                additional_detail = []
                addresses_detail = []
                people_detail = []
                fillings_detail = []

                id = row['ID']
                registration_number = row['RECORD_NUM']
                print(f"Record no: {reg_num}, Registration number: {registration_number}")
                NAME = row['TITLE'][0].replace("%", "%%").replace(registration_number, '').replace('()', '') if row['TITLE'][0] is not None else ""
                url = f"https://bizfileonline.sos.ca.gov/api/FilingDetail/business/{id}/false"

                
                response = make_request(url, headers=headers, retry_interval=60*60, max_retries=10)
                if response is None:
                    continue
                json_data = response.json()
                if 'DRAWER_DETAIL_LIST' not in json_data:
                    continue
                values = {}
                for item in json_data['DRAWER_DETAIL_LIST']:
                    label = item['LABEL']
                    value = item['VALUE']
                    values[label] = value

                initial_filing_date = values.get('Initial Filing Date').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Initial Filing Date') is not None else ""
                status = values.get('Status').replace('%', '%%').replace("'", "").replace("  ", "") if values.get('Status') is not None else ""
                inactive_date = values.get('Inactive Date') if values.get('Inactive Date') is not None else ""
                jursidiction = values.get('Formed In').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Formed In') is not None else ""
                aliases = values.get('Foreign Name').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Foreign Name') is not None else ""
                type = values.get('Entity Type') if values.get('Entity Type') is not None else ""
                statement_filing_due_date = format_date(values.get('Statement of Info Due Date')) if values.get('Statement of Info Due Date') is not None else ""
                
                if values.get('Standing - SOS') is not None:
                    additional_detail.append({
                        "type": "standings_information",
                        "data":[{
                            "standing_sos": values.get('Standing - SOS').replace('%', '%%').replace("'", "") if values.get('Standing - SOS') is not None else "",
                            "standing_ftb": values.get('Standing - FTB').replace('%', '%%').replace("'", "") if values.get('Standing - FTB') is not None else "",
                            "standing_agent": values.get('Standing - Agent').replace('%', '%%').replace("'", "") if values.get('Standing - Agent') is not None else "",
                            "standing_vcfcf": values.get('Standing - VCFCF').replace('%', '%%').replace("'", "") if values.get('Standing - VCFCF') is not None else ""
                        }]
                    })

                if values.get('Principal Address') is not None and values.get('Principal Address') != "":
                    addresses_detail.append({
                        "type": "principal_address",
                        "address": values.get('Principal Address').replace('\n', ' ').replace("%", "%%").replace("'", "").replace("  ", "")
                    })

                if values.get('Mailing Address') is not None and values.get('Mailing Address') != "":
                    addresses_detail.append({
                        "type": "mailing_address",
                        "address": values.get('Mailing Address').replace('\n', ' ').replace("%", "%%").replace("'", "").replace("  ", "")
                    })

                ca_registered_agent = values.get('CA Registered Corporate (1505) Agent Authorized Employee(s)').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('CA Registered Corporate (1505) Agent Authorized Employee(s)') is not None else ""
                if ca_registered_agent is not None and ca_registered_agent != "":
                    if '\n\n' in ca_registered_agent:
                        multiple_agents = ca_registered_agent.split('\n\n')
                        for multiple_agent in multiple_agents:
                            ca_agent_name = multiple_agent.split('\n')[0] if multiple_agent is not None else ""
                            if ca_agent_name != "":
                                people_detail.append({
                                    "name": ca_agent_name,
                                    "address": ', '.join(multiple_agent.split('\n')[1:]) if multiple_agent is not None else "",
                                    "designation": "ca_registered_agent"
                                })
                    else:
                        people_detail.append({
                            "name": ca_registered_agent.split('\n')[0] if ca_registered_agent is not None else "",
                            "address": ', '.join(ca_registered_agent.split('\n')[1:]) if ca_registered_agent is not None else "",
                            "designation": "ca_registered_agent"
                        })

                _agent_ = values.get('Agent').replace("%", "%%").replace("'", "").replace("  ", "") if values.get('Agent') is not None else ""
                if _agent_ is not None and _agent_ != "":                    
                    meta_detail = {"type": _agent_.split('\n')[0] if _agent_ is not None and len(_agent_.split('\n')) > 0 else ""}
                    people_detail.append({
                        "name": _agent_.split('\n')[1] if _agent_ is not None and len(_agent_.split('\n')) > 1 else "",
                        "address": ', '.join(_agent_.split('\n')[2:]) if _agent_ is not None  and len(_agent_.split('\n')) > 2 else "",
                        "designation": "registered_agent",
                        "meta_detail": meta_detail
                    })

                url = f"https://bizfileonline.sos.ca.gov/api/History/business/{registration_number}"
                response = make_request(url, headers=headers, retry_interval=60*60, max_retries=10)
                if response is not None:
                    json_data = response.json()
                else:
                    json_data = []
                if "AMENDMENT_LIST" in json_data:
                    for item in json_data['AMENDMENT_LIST']:
                        history_list = get_history_list(json_data["HISTORY_LIST"], item['AMENDMENT_ID'])
                        meta_detail = {}
                        for index, hist in enumerate(history_list):
                            meta_detail[f"field_{index+1}"] = hist.get("DISPLAY_NAME", "")
                            meta_detail[f"changed_from_{index+1}"] = format_date(hist.get("CHANGED_FROM", ""))
                            meta_detail[f"changed_to_{index+1}"] = format_date(hist.get("CHANGED_TO", ""))
                        meta_detail = {key: value for key, value in meta_detail.items() if value}
                        fillings_detail.append({
                            "title":item["AMENDMENT_TYPE"], 
                            "filing_type": item['AMENDMENT_TYPE'].replace("'", "").replace("  ", "") if item['AMENDMENT_TYPE'] is not None else "",
                            "filing_code": item['AMENDMENT_NUM'].replace("'", "").replace("  ", "") if item['AMENDMENT_NUM'] is not None else "",
                            "date": item['AMENDMENT_DATE'].replace('/', '-') if "AMENDMENT_DATE" in item and item['AMENDMENT_DATE'] is not None else "",
                            "file_url": f"{BASE_URL}{item['DOWNLOAD_LINK']}" if item['DOWNLOAD_LINK'] != "" and item['DOWNLOAD_LINK'] is not None else "",
                            "meta_detail": meta_detail                         
                        })

                DATA = {
                    "name": NAME,
                    "registration_number": registration_number,
                    "status": status,
                    "inactive_date": format_date(inactive_date),
                    "jurisdiction": jursidiction,
                    "aliases": aliases,
                    "type": type,
                    "statement_filing_due_date": format_date(statement_filing_due_date),
                    "initial_filing_date": format_date(initial_filing_date),
                    "additional_detail": additional_detail,
                    "fillings_detail": fillings_detail,
                    "addresses_detail": addresses_detail,
                    "people_detail": people_detail
                }

                ENTITY_ID = california_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
                BIRTH_INCORPORATION_DATE = ''
                DATA = california_crawler.prepare_data_object(DATA)
                ROW = california_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                california_crawler.insert_record(ROW)

            
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    california_crawler.db_log(log_data)
    california_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    california_crawler.db_log(log_data)
