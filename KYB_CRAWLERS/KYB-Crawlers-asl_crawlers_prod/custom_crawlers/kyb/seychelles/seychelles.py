"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE': 'Ministry of Finance, and Trade -Seygoconnect',
    'COUNTRY': 'Seychelles',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.registry.gov.sc/BizRegistration/WebSearchBusiness.aspx",
                      "Source Description": "The Ministry of Finance, and Trade in Seychelles works to manage the Seychelles economy through sound financial and economic policies plan carefully and structure strategies for sustainable development and economic stability with the object of promoting more national unity and social justice."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.registry.gov.sc/BizRegistration/WebSearchBusiness.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Seychelles Official Registry"
}

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv

seychelles_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = seychelles_crawler.get_requests_helper()

url = "https://www.registry.gov.sc/BizRegistration/WebSearchBusiness.aspx"

payload={'__VIEWSTATE': '/wEPDwUJODYzNDkwNDc5D2QWAmYPZBYCAgMPZBYCAgMPDxYCHgtOYXZpZ2F0ZVVybAUdaHR0cHM6Ly9tYWlsLmVnb3Yuc2MvZXhjaGFuZ2VkZGT42u63+epTb3VvxfFJoCiPdZqETHt+mKfnVfvRd5dbuw==',
'__VIEWSTATEGENERATOR': '7B40CE41',
'__EVENTVALIDATION': '/wEdAAMkhe4yejpX9Cu1kG37evbcGgOkRs/x0nQgsaQ72sj7qo5MW6XMaFjzT9nUdsIknov0w4fBLbtRNVcm/ket6T2BIe9L6Rj2oupf6VMhPWttEg==',
'ctl00$ContentPlaceHolder1$txtSearch': '.',
'ctl00$ContentPlaceHolder1$btnSearch': 'Search'}

headers = {
  'Host': 'www.registry.gov.sc',
  'Origin': 'https://www.registry.gov.sc',
  'Referer': 'https://www.registry.gov.sc/BizRegistration/WebSearchBusiness.aspx',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

response = request_helper.make_request(url, method="POST", headers=headers, data=payload, verify=False)

soup = BeautifulSoup(response.text, "html.parser")

def get_data():
    data_table = soup.find("table", id="tableResults")
    table_rows = data_table.find_all("tr")
    for tr in table_rows:
        tds = tr.find_all("td")
        registration_number = tds[0].text
        name_ = tds[1].text
        industries = tds[2].text
        type_ = tds[3].text

        OBJ = {
            "registration_number": registration_number,
            "name": name_,
            "industries": industries,
            "type": type_
        }

        OBJ = seychelles_crawler.prepare_data_object(OBJ)
        ENTITY_ID = seychelles_crawler.generate_entity_id(OBJ['registration_number'], OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ''
        ROW = seychelles_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
        seychelles_crawler.insert_record(ROW)
        
    return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = get_data()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML"}
    seychelles_crawler.db_log(log_data)
    seychelles_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    seychelles_crawler.db_log(log_data)