"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Belize Financial Services Commission',
    'COUNTRY' : 'Belize',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.belizefsc.org.bz/struckoff/", 
                        "Source Description": "The Financial Services Commission is a statutory authority established in Belize to regulate & supervise non-bank financial services, provided by entities licensed or registered under the Financial Services Commission Act, Cap. 272 and the Securities Industry Act, 2021 (SIA)."},
    'URL' : 'https://www.belizefsc.org.bz/struckoff/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Belize'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

belize_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  belize_crawler.get_requests_helper()

def get_nonce():
    response = request_helper.make_request("https://www.belizefsc.org.bz/struckoff2/?wdt_search=&submit=Submit")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        hidden_input = soup.find('input', {'id': 'wdtNonceFrontendEdit_10'})
        if hidden_input:
            nonce_value = hidden_input.get('value')
            return nonce_value
        
def get_data(page_number, limit=50000):
    url=f"https://www.belizefsc.org.bz/wp-admin/admin-ajax.php?action=get_wdtable&table_id=10"
    data = {
        'draw': '4',
        'columns[0][data]': '0',
        'columns[0][name]': 'renum',
        'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'true',
        'columns[0][search][value]': '',
        'columns[0][search][regex]': 'false',
        'columns[1][data]': '1',
        'columns[1][name]': 'recname',
        'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true',
        'columns[1][search][value]': '',
        'columns[1][search][regex]': 'false',
        'columns[2][data]': '2',
        'columns[2][name]': 'struckoff',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '',
        'columns[2][search][regex]': 'false',
        'order[0][column]': '0',
        'order[0][dir]': 'asc',
        'start': page_number*limit,
        'length': limit,
        'search[value]': '',
        'search[regex]': 'false',
        'wdtNonce': get_nonce(),
        'sRangeSeparator': '|'
    }
    response = request_helper.make_request(url=url, method="POST", data=data)
    if response.status_code == 200:
        json_data = response.json()
        if 'data' in json_data and len(json_data['data']) > 0:
            return json_data['data']

if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 0

try:
    while True:
        print('Page No. ', start)
        result = get_data(start)
        if result is None: break
        for data in result:
            NAME = data[1].replace("%", "%%") if data[1] is not None else ""
            registration_number = data[0]
            inactive_date = data[2].replace("/", "-") if data[2] is not None else ""
            DATA = {
                'registration_number': registration_number,
                'name': NAME,
                'inactive_date': inactive_date,
                'status': 'struck-off'
            }
            ENTITY_ID = belize_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = belize_crawler.prepare_data_object(DATA)
            ROW = belize_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            belize_crawler.insert_record(ROW)
        start += 1
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    belize_crawler.db_log(log_data)
    belize_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    belize_crawler.db_log(log_data)