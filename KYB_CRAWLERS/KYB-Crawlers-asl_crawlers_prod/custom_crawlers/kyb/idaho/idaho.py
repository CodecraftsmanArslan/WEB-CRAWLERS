"""Import required library"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Secretary of States Office, Idaho',
    'COUNTRY' : 'Idaho',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://sosbiz.idaho.gov/search/business", 
                        "Source Description": "The secretary of state of Idaho is one of the constitutional officers of the U.S. state of Idaho. It is an elected position within the executive branch of the state government. The current secretary of state is Phil McGrane. The secretary's office registers business entities files liens under the Uniform Commercial Code, and registers trademarks and service marks within the state."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://sosbiz.idaho.gov/search/business'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Idaho Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

idaho_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = idaho_crawler.get_requests_helper()
s =  idaho_crawler.get_requests_session()

API_URL = 'https://sosbiz.idaho.gov/api/Records/businesssearch'
headers = {
    'Content-Type':'application/json',
    'Referer':'https://sosbiz.idaho.gov/search/business',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}
arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 0
end_number  = int(arguments[2]) if len(arguments)>2 else 9999999

# Define a function for making HTTP requests with retries and proxies
def make_request(url, method="GET", headers={}, timeout=10, max_retries=3, retry_interval=60, json=None):
    """
    Make an HTTP request with retries and support for proxies.
    Args:
        url (str): The URL to make the request to.
        method (str, optional): The HTTP method to use (default is "GET").
        headers (dict, optional): Additional headers to include in the request (default is an empty dictionary).
        timeout (int, optional): Timeout for the request in seconds (default is 10 seconds).
        max_retries (int, optional): Maximum number of retries in case of failure (default is 3).
        retry_interval (int, optional): Interval between retries in seconds (default is 60 seconds).
        json (object, optional): JSON data to include in the request body (default is None).
    Returns:
        requests.Response or None: The response object if the request is successful, otherwise None.
    """
    proxies={
        "http": "http://ljayoggy-rotate:kfk2b2al877m@p.webshare.io:80/",
        "https": "http://ljayoggy-rotate:kfk2b2al877m@p.webshare.io:80/"
    }
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(method, url, headers=headers, timeout=timeout, json=json, proxies=proxies)
            if response.status_code == 200:
                return response
        except Exception as e:
            print(f"Request with proxy failed: {e}")
        if attempt < max_retries:
            print(f"Request failed. Next retry in {retry_interval} seconds...")
            time.sleep(retry_interval)
    return None

try:
    for number in range(start_number, end_number):
        print("\nSearch Number", number)
        payload = {"SEARCH_VALUE":f"{number}","STARTS_WITH_YN":True,"CRA_SEARCH_YN":False,"ACTIVE_ONLY_YN":False}
        
        while True:
            response = make_request(API_URL,method='POST',headers=headers, json=payload)
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            print(response)
            if not response:
                continue
            if response.status_code == 200:
                data_response = response.json()
                break
            else:
                time.sleep(8)
        if len(data_response['rows']) == 0:
            continue
        
        if 'rows' in data_response:
            for row in data_response['rows'].values():
                additional_detail = []
                addresses_detail = []
                people_detail = []
                fillings_detail = []

                id = row['ID']
                NAME = row['TITLE'][0] if row['TITLE'][0] is not None else ""
                registration_number = row['RECORD_NUM']
                url = f"https://sosbiz.idaho.gov/api/FilingDetail/business/{id}/false"
                
                while True:
                    FilingDetail_response = make_request(url, headers=headers)
                    if not FilingDetail_response:
                        continue
                    if FilingDetail_response.status_code ==200:
                        FilingDetail = FilingDetail_response.json()
                        break
                    else:
                        time.sleep(6)
                
                values = {}
                for item in FilingDetail['DRAWER_DETAIL_LIST']:
                    label = item['LABEL']
                    value = item['VALUE']
                    values[label] = value
                
                filing_type = values.get('Filing Type', '') if values.get('Filing Type') is not None else ""
                status = values.get('Status', '') if values.get('Status') is not None else ""
                formed_in = values.get('Formed In', '') if values.get('Formed In') is not None else ""
                term_of_duration = values.get('Term of Duration', '') if values.get('Term of Duration') is not None else ""
                initial_filing_date = values.get('Initial Filing Date', '') if values.get('Initial Filing Date') is not None else ""
                ar_due_date = values.get('AR Due Date', '') if values.get('AR Due Date') is not None else ""
                inactive_filing_date = values.get('Inactive Filing Date', '') if values.get('Initial Filing Date') is not None else ""
                
                # address_detail
                if values.get('Principal Address') is not None and values.get('Principal Address') != "":
                            addresses_detail.append({
                                "type": "general_address",
                                "address": values.get('Principal Address').replace('\n',' ')
                            })

                if values.get('Mailing Address') is not None and values.get('Mailing Address') != "":
                    addresses_detail.append({
                        "type": "mailing_address",
                        "address": values.get('Mailing Address').replace('\n',' ')
                    })
                # people_detail
                registered_agent = values.get('Registered Agent', '') if values.get('Registered Agent') is not None else ""
                if registered_agent is not None and registered_agent != "":
                    registered_agent = registered_agent
                    people_detail.append({
                        "name": registered_agent.split('\n')[2] if registered_agent is not None else "",
                        "address": ', '.join(registered_agent.split('\n')[3:]) if registered_agent is not None else "",
                        "designation": "registered_agent",
                        "meta_detail":{
                            "type":registered_agent.split('\n')[0] if registered_agent is not None else "",
                            "code":registered_agent.split('\n')[1] if registered_agent is not None else ""
                        }
                    })
                # people_detail
                Commercial_registered_agent = values.get('Commercial Registered Agent', '') if values.get('Commercial Registered Agent') is not None else ""
                if Commercial_registered_agent is not None and Commercial_registered_agent != "":
                    Commercial_registered_agent = Commercial_registered_agent
                    people_detail.append({
                        "designation": "registered_agent",
                        "name": Commercial_registered_agent.split('\n')[2] if Commercial_registered_agent is not None else "",
                        "address": ', '.join(Commercial_registered_agent.split('\n')[3:]) if Commercial_registered_agent is not None else "",
                        "meta_detail":{
                            "type":Commercial_registered_agent.split('\n')[0] if Commercial_registered_agent is not None else "",
                            "code":Commercial_registered_agent.split('\n')[1] if Commercial_registered_agent is not None else ""
                        }
                    })
            
                # fillings_detail
                History_url = f"https://sosbiz.idaho.gov/api/History/business/{registration_number}"
                while True:
                    History_response = make_request(History_url, headers=headers)
                    if not History_response:
                        continue
                    if History_response.status_code == 200:
                        History_data = History_response.json()
                        break
                    else: 
                        time.sleep(8)
            
                base_ul = 'https://sosbiz.idaho.gov'
                # Iterate over AMENDMENT_LIST
                if 'AMENDMENT_LIST' in History_data: 
                    for amendment_item in History_data['AMENDMENT_LIST']:
                        meta_detail = {} 
                        count = 1
                        for history_item in History_data['HISTORY_LIST']:
                            if history_item['AMENDMENT_ID'] == amendment_item['AMENDMENT_ID']:
                                # Assign meta details to the meta_detail dictionary with numbered keys
                                meta_detail[f'changed_from{count}'] = history_item['CHANGED_FROM'].replace("\n"," ").replace("/","-").replace("12:00:00 AM", "").strip()
                                meta_detail[f'changed_to{count}'] = history_item['CHANGED_TO'].replace("/","-").replace("12:00:00 AM", "").strip()
                                meta_detail[f'field{count}'] = history_item['DISPLAY_NAME']
                                count += 1  # Increment count for the next set of meta details

                        fillings_detail.append({
                            "filing_type": amendment_item['AMENDMENT_TYPE'],
                            "filing_code": amendment_item['AMENDMENT_NUM'],
                            "date": amendment_item['AMENDMENT_DATE'].replace('/', '-'),
                            "file_url": base_ul + amendment_item['DOWNLOAD_LINK'].replace("%","%%") if 'DOWNLOAD_LINK' in amendment_item else "",
                            "meta_detail": meta_detail
                        })
                
                OBJ = {
                        "name": NAME.replace('\"',''),
                        "type": filing_type,
                        "status": status,
                        "jurisdiction": formed_in,
                        "registration_number": registration_number,
                        "term_of_duration": term_of_duration,
                        "inactive_date": initial_filing_date.replace('/', '-') if initial_filing_date is not None else "",
                        "annual_return_due_date": ar_due_date.replace('/', '-') if ar_due_date is not None else "",
                        "fillings_detail": fillings_detail,
                        "addresses_detail": addresses_detail,
                        "people_detail": people_detail
                    }
                
                OBJ =  idaho_crawler.prepare_data_object(OBJ)
                ENTITY_ID = idaho_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = ''
                ROW = idaho_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                idaho_crawler.insert_record(ROW)

    idaho_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    idaho_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    idaho_crawler.db_log(log_data) 