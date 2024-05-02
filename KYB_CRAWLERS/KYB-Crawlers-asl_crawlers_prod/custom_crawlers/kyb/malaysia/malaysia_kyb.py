"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Companies Commission of Malaysia',
    'COUNTRY' : 'Malaysia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.ssm.com.my/Pages/Quick_Link_backup/e-Search.aspx", 
                        "Source Description": "The Companies Commission of Malaysia (SSM - Suruhanjaya Syarikat Malaysia) is a statutory body under the Ministry of Finance Malaysia. It is responsible for regulating and supervising companies and businesses in Malaysia. SSM plays a crucial role in overseeing company registrations, business licenses, and other related matters in the country."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.ssm.com.my/Pages/Quick_Link_backup/e-Search.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Malaysia",
}

malaysia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = malaysia_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)
request_helper =  malaysia_crawler.get_requests_helper()

def get_table_data(soup):
    # Find the table rows (including the header row within tbody if available)
    rows = soup.find_all('tr')
    if len(rows) == 0:
        return []
    # Initialize an empty list to store the JSON data
    data = []

    # If the first row within tbody contains th, use it as the header row
    header_row = rows[0]
    header_columns = header_row.find_all(['th', 'td'])  # Accept both th and td elements as header columns
    column_names = [header_column.text.strip() for header_column in header_columns]

    # Process each row (skipping the first row if it's the header row) and extract data
    for row in rows[1:]:
        columns = row.find_all('td')
        if len(columns) == len(column_names):
            row_data = {}
            for i in range(len(column_names)):
                column_name = column_names[i]
                cell_value = columns[i].text.strip()
                row_data[column_name] = cell_value
            data.append(row_data)

    return data

def get_paras(url):
    response = request_helper.make_request(url, max_retries =10, timeout=60*60)
    soup = BeautifulSoup(response.text, "html.parser")

    res = {
        "__VIEWSTATE": soup.find(id="__VIEWSTATE")["value"] if soup.find(id="__VIEWSTATE") else '',
        "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR")["value"] if soup.find(id="__VIEWSTATEGENERATOR") else '',
        "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION")["value"] if soup.find(id="__EVENTVALIDATION") else '',
        "__REQUESTDIGEST": soup.find(id="__REQUESTDIGEST")["value"] if soup.find(id="__REQUESTDIGEST") else '',
    }

    return res

def get_page_data(idDropRegistrationType, txtCarieSearch):
    url = "https://www.ssm.com.my/Pages/Quick_Link_backup/e-Search.aspx"
    params = get_paras(url)
    payload = {
        "__VIEWSTATE": params.get('__VIEWSTATE'),
        "__VIEWSTATEGENERATOR": params.get('__VIEWSTATEGENERATOR'),
        "__EVENTVALIDATION": params.get('__EVENTVALIDATION'),
        "__REQUESTDIGEST": params.get('__REQUESTDIGEST'),
        "ctl00$ctl36$g_468c23f7_e2ba_4c0a_8350_52e4e007dcba$ctl00$idDropRegistrationType": idDropRegistrationType,
        "ctl00$ctl36$g_468c23f7_e2ba_4c0a_8350_52e4e007dcba$ctl00$txtCarieSearch": txtCarieSearch,
        "ctl00$ctl36$g_468c23f7_e2ba_4c0a_8350_52e4e007dcba$ctl00$idBtneSearch": "Search Now"
    }

    headers = {
        "Content-Length": str(len(str(payload))),
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.ssm.com.my"
    }
    
    response = request_helper.make_request(url, method="POST", data=payload, headers=headers, max_retries =10, timeout=60*60)

    return response

try:

    # LLP Registration Number range
    start_llp = 1
    end_llp = 35619
    llp_registration_numbers = [f"LLP{str(i).zfill(7)}-LGN" for i in range(start_llp, end_llp + 1)]

    # Business Registration Old range
    start_business_reg = 2
    end_business_reg = 3510463
    business_registration_old = [str(i).zfill(9) for i in range(start_business_reg, end_business_reg + 1)]

    # Company Registration Number Old range
    start_company_reg = 1
    end_company_reg = 694935
    company_registration_number_old = list(range(start_company_reg, end_company_reg + 1))

    # Combine all ranges into a single array
    all_ranges = llp_registration_numbers + business_registration_old + company_registration_number_old
    
    skip_record = sys.argv[1] if len(sys.argv) > 1 else "LLP0000001-LGN"
    flag = True
    # Loop through all ranges and print the values
    for value in all_ranges:
        if skip_record != value and flag == True:
            continue
        flag = False
        registration_type = "llp" if "LLP" in (str(value)) else ("rob" if len(str(value)) == 9 else "roc")
        print("Registration Type:", registration_type)
        print("Registration No:", value)
        response = get_page_data(registration_type, value)
        html_content = response.text
        STATUS_CODE = response.status_code
        DATA_SIZE = len(html_content)
        soup = BeautifulSoup(html_content, "html.parser")
        response = get_table_data(soup)

        for data in response:
            meta_detail = {"new_registration_number": data.get("New Registration Number")} if data.get("New Registration Number") is not None and data.get("New Registration Number") != "" else {}
            NAME = data.get("Entity Type").replace("%", "%%") if data.get("Entity Type") is not None else ""
            DATA = {
                "registration_number": data.get("Registration Number"),
                "name": NAME,
                "status": data.get("Status"),
                "tax_number": data.get("GST Number"),
                "meta_detail": meta_detail
            }
            
            ENTITY_ID = malaysia_crawler.generate_entity_id(company_name=NAME, reg_number=data.get("Registration Number"))
            BIRTH_INCORPORATION_DATE = ''
            DATA = malaysia_crawler.prepare_data_object(DATA)
            ROW = malaysia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            malaysia_crawler.insert_record(ROW)


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    malaysia_crawler.db_log(log_data)
    malaysia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    malaysia_crawler.db_log(log_data)
