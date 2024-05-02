"""Set System Path"""
import sys, traceback,time,json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Virgin Islands Department of Licensing and Consumer Affairs (DLCA)',
    'COUNTRY' : 'Virgin Island (US)',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://secure.dlca.vi.gov/license/Asps/Search/License_search.aspx", 
                        "Source Description": "The Virgin Islands Department of Licensing and Consumer Affairs (DLCA) is a government agency responsible for overseeing licensing, consumer protection, and regulatory affairs in the United States Virgin Islands. The DLCA aims to ensure fair and ethical business practices, protect consumers, and promote a healthy marketplace on the islands."},
    'URL' : 'https://secure.dlca.vi.gov/license/Asps/Search/License_search.aspx',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': True,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Virgin Island (US)'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

virgin_island_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  virgin_island_crawler.get_requests_helper()

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 0

try:
    while True:
        print('Page No. ', start)
        url = f"https://secure.dlca.vi.gov/license/Asps/Search/License_search.aspx"
        payload = {
            "__EVENTTARGET": "ctl00$top$LicSearchcontrol$btnNext",
            "ctl00$top$LicSearchcontrol$txtName": "___",
            "ctl00$top$LicSearchcontrol$hdnPgIndex": start
        }
        response = request_helper.make_request(url, method="POST", data=payload, proxy=True)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        html_content = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find('table', attrs={'id': 'ctl00_top_LicSearchcontrol_gvSearch'})

        if table is None:
            break

        # Extract the table headers
        headers = [th.text.strip() for th in table.find_all('th')]

        # Extract the table rows
        rows = []
        for tr in table.find_all('tr'):
            row = [td.text.strip() for td in tr.find_all('td')]
            if row:
                rows.append(row)

        # Create a list of dictionaries where each dictionary represents a row
        data = []
        for row in rows:
            data.append(dict(zip(headers, row)))
        
        registration_number = ""

        for record in data:
            NAME = record.get('Business Name')

            DATA = {
                "name": NAME,
                "aliases": record.get('Trade Name'),
                "addresses_detail": [{
                    "type": "general_address",
                    "address": record.get('Address')
                }] if record.get('Address') is not None else [],
                "industries": record.get('License Type'),
                "license_number": record.get('Lic #'),
                "expiration_date": record.get('Exp Date').replace("/", "-") if record.get('Exp Date') is not None else "",
                "registration_number": registration_number
            }

            ENTITY_ID = virgin_island_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = virgin_island_crawler.prepare_data_object(DATA)
            ROW = virgin_island_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)

            virgin_island_crawler.insert_record(ROW)
            
        start += 1
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    virgin_island_crawler.db_log(log_data)
    virgin_island_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    virgin_island_crawler.db_log(log_data)