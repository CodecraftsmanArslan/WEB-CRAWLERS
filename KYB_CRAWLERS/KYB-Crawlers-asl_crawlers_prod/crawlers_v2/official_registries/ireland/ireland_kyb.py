"""Import required library"""
import traceback, sys, requests, time, os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV
from dateutil import parser
from datetime import datetime

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

if ENV["ENVIRONMENT"] == "LOCAL":
    FILE_PATH = os.path.dirname(os.getcwd())+ "/ireland"
else:
    FILE_PATH = os.path.dirname(os.getcwd())+ "/KYB-Crawlers/crawlers_v2/official_registries/ireland"

# Define global variables and metadata
meta_data = {
    'SOURCE' :'Companies Registration Office (CRO)',
    'COUNTRY' : 'Ireland',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://core.cro.ie/", 
                        "Source Description": "The Companies Registration Office (CRO) is the central repository of public statutory information on Irish companies and business names. The CRO provides access to this data through its website, which includes a Company Search facility."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://core.cro.ie/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Ireland",
}

# Create an instance of the CustomCrawler class with the provided configuration and environment variables.
ireland_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
# Get a request helper instance associated with the CustomCrawler, which can be used for making HTTP requests.
request_helper = ireland_crawler.get_requests_helper()

# Define a function for making HTTP requests with retries and proxies
def make_request(url, method="GET", headers={}, timeout=10, max_retries=3, retry_interval=60, json=None):
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

# Define a function to generate a range of search prefixes and postfixes
def set_ranges():
    prefixes = ['RN', 'LP']
    postfixes = ['SA', 'F', 'R', 'T']
    merged_range = []
    numbers = range(1, 99999)
    merged_range.extend([str(number).zfill(7) for number in range(0, 1200000)])
    merged_range.extend([str(number).zfill(8) for number in range(6000000, 20000000)])
    merged_range.extend([f"{prefix}{number:05d}" for prefix in prefixes for number in numbers])
    merged_range.extend([f"{number:05d}{postfix}" for postfix in postfixes for number in numbers])
    return merged_range

# Define a function to format a date
def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

# Define a function to get request headers
def get_headers():
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB',
        'Cache-Control': 'no-cache, no-store',
        'Content-Type': 'application/json',
        'Expires': '0',
        'Origin': 'https://core.cro.ie',
        'Pragma': 'no-cache',
        'Referer': 'https://core.cro.ie/',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    return headers

# Define functions to retrieve Event information from the API
def get_events(id):
    url = f"https://api.cro.ie/api/entity/latest-events/{id}?maxNumEvents=5"
    response = make_request(url, headers=get_headers())
    if response is not None:
        data = response.json()
        return data  

# Define functions to retrieve previous information from the API
def get_pervious_info(id):
    url = f"https://api.cro.ie/api/entity/names/{id}"
    response = make_request(url, headers=get_headers())
    if response is not None:
        data = response.json()
        return data    

# Define functions to retrieve basic information from the API
def profile_info(id):
    url = f"https://api.cro.ie/api/entity/{id}"
    response = make_request(url, headers=get_headers())
    if response is not None:
        data = response.json()
        return data['data']

# Define a function to extract and format data for a specific entity
def get_data(entity_id):
    result = {}
    addresses_detail = []
    previous_names_detail = []
    announcements_detail = []
    data = profile_info(entity_id)
    if data is not None:
        result["registration_number"] = data.get("entityRegNumber")
        result["name"] = data.get("entityRegName").replace("%", "%%") if data.get("entityRegName") is not None else ""
        result["type"] = data.get("entityTypeDesc")
        result["status"] = data.get("entityStatusDesc")
        result["effective_date"] = format_date(data.get("entityStatusEffectiveDate"))
        result["registration_date"] = format_date(data.get("entityRegDate"))
        result["next_annual_return"] = format_date(data.get("annualReturnDueDate"))
        try:
            if "entityRegAddress" in data and "addressOneLine" in  data['entityRegAddress'] and data['entityRegAddress']['addressOneLine'] is not None and data['entityRegAddress']['addressOneLine'].replace("********NO ADDRESS DETAILS*******", "").replace(" ", "").replace(",","") != "":
                addresses_detail.append({
                    "type": "registered_address",
                    "address": data['entityRegAddress']['addressOneLine'] 
                })
        except:
            pass
        pervious_info = get_pervious_info(entity_id)
        if pervious_info and 'data' in pervious_info and pervious_info['data'] is not None:
            for arr in pervious_info['data']:
                previous_names_detail.append({
                    "name": arr.get('name'),
                    "meta_detail": {
                        "effective_date": format_date(arr.get('effectiveFrom'))
                    }
                })

        events = get_events(entity_id)
        if events and "data" in events and events['data'] is not None:
            for event in events['data']:
                announcements_detail.append({
                    "title": event.get('eventDesc'),
                    "date": format_date(event.get('eventDate')),
                    "meta_detail": {
                        "announcement_status": event.get('eventTypeDesc') if event.get('eventTypeDesc') is not None else ""
                    }
                })
            
        result["addresses_detail"] = addresses_detail
        result["previous_names_detail"] = previous_names_detail
        result["announcements_detail"] = announcements_detail
    return result

# Define a function to get entity IDs based on a search query
def get_entity_ids(num):
    url = 'https://api.cro.ie/api/entity/quick-search'
    
    payload = {
        'searchText': num
    }
    response = make_request(url, method="POST", headers=get_headers(), json=payload)
    if response is not None:
        data = response.json()
        entity_ids = [item['entityId'] for item in data['data']]
        return entity_ids
    return []

flag = True
#Main script logic for iterating through entity IDs and extracting data
try:  
    start = sys.argv[1] if len(sys.argv) > 1 else "0"
    for num in set_ranges():
        if flag and num.isdigit() and start.isdigit():
            if int(start) > int(num):
                continue
            else:
                flag = False
        elif flag:
            if num != start:
                continue
            else:
                flag = False
        entity_ids = get_entity_ids(num)
        if entity_ids is None: continue
        for entity_id in entity_ids:
            print(f"Record No:", num, "Entity id:", entity_id)
            data = get_data(entity_id)
            if data is not None and len(data) > 0:
                ENTITY_ID = ireland_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
                BIRTH_INCORPORATION_DATE = ''
                print(data)
                DATA = ireland_crawler.prepare_data_object(data)
                ROW = ireland_crawler.prepare_row_for_db(ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
                ireland_crawler.insert_record(ROW)
        
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ireland_crawler.db_log(log_data)
    ireland_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    ireland_crawler.db_log(log_data)
    with open(f"{FILE_PATH}/failed_records.txt", "a") as crawled_records:
        crawled_records.write(str(entity_id) + "\n")
