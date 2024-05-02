"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import traceback
from CustomCrawler import CustomCrawler
from load_env import ENV
import json
import sys, time
import cloudscraper, requests
from random import randint

meta_data = {
    'SOURCE': 'Montana Secretary of State, Business Services Division',
    'COUNTRY': 'Montana',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://biz.sosmt.gov/search/business",
                      "Source Description": "The Division assists businesses with the filing of their registration, articles of organization, assumed business name, and trademarks. Additionally, the division is responsible for filing and maintaining records under the Uniformed Commercial Code (UCC)."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://biz.sosmt.gov/search/business'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Montana Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

montana_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
scraper = cloudscraper.create_scraper(delay=10, browser="chrome")

all_alphabets = ["C", "A", "E", "D", "F", "R", "RN", "P"]

start_alphabet = ARGUMENT[1].capitalize() if len(ARGUMENT) > 1 else all_alphabets[0]
start_number = int(ARGUMENT[2]) if len(ARGUMENT) > 2 else 1
start_number = str(start_number).zfill(6)
end_number = 99999999

proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/username/direct/-/"
proxy_response = scraper.get(proxy_url).text.split("\n")
proxy_response = [proxy.replace("\r", "")[:-22] for proxy in proxy_response if proxy]

all_proxies = []
for proxies in proxy_response:
    proxy = {"http": f"http://{proxies}",
             "https": f"http://{proxies}"}
    all_proxies.append(proxy)

session = requests.Session()
small_headers = {
    'authority': 'biz.sosmt.gov',
    'method': 'POST',
    'path': '/api/Records/businesssearch',
    'Content-Type': 'application/json',
    'Origin': 'https://biz.sosmt.gov',
    'Referer': 'https://biz.sosmt.gov/search/business',
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}
cookies_response = session.post(url="https://biz.sosmt.gov/api/Records/businesssearch", headers=small_headers)
cookies = cookies_response.cookies.get_dict()
print(cookies)
input()
__cf_nm = cookies["__cf_bm"]
session_id = cookies["ASP.NET_SessionId"]
    
headers = {
    'authority': 'biz.sosmt.gov',
    'method': 'POST',
    'path': '/api/Records/businesssearch',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Content-Type': 'application/json',
    'Cookie': f'cf_chl_2=2e7d2f316e21ff0; __cf_bm={__cf_nm}; ASP.NET_SessionId={session_id}; cf_clearance=66GmbdEAvOzuDzJ7asPJ0ZLIVnYDZ.izlwLr8Z513gY-1697786461-0-1-3cc46060.e1ddb803.6bc53f80-0.2.1697786461	',
    'Origin': 'https://biz.sosmt.gov',
    'Referer': 'https://biz.sosmt.gov/search/business',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

for alphabet in all_alphabets:
    if alphabet != start_alphabet:
        continue
    for number in range(int(start_number), end_number):
        search_number = alphabet+str(number).zfill(6)
        payload = {
            "SEARCH_VALUE": f"{search_number}",
            "QUERY_TYPE_ID": 1010,
            "FILING_TYPE_ID": "0",
            "FILING_SUBTYPE_ID": "0",
            "STATUS_ID": "0",
            "STATE": "",
            "COUNTY": "",
            "CRA_SEARCH_YN": False,
            "FILING_DATE": {
                "start": None,
                "end": None
            },
            "EXPIRATION_DATE": {
                "start": None,
                "end": None
            }
        }

        json_data = json.dumps(payload)

        response = scraper.post(url='https://biz.sosmt.gov/api/Records/businesssearch', headers=headers, json=json_data)
        try:
            data = response.json()
            print(data)
        except:
            data = response.text
            print(data, "Bot Detected")
        try:
            id_ = list(data['rows'].keys())[0]
        except:
            id_ = ""
            print(f"no records for: {search_number}")
            time.sleep(randint(3,5))

        if id_:
            detail_url = f"https://biz.sosmt.gov/api/FilingDetail/business/{id_}/false"
            detail_response = scraper.get(url=detail_url, headers=headers)
            company_data = detail_response.json()
            print(company_data)
            input()
            time.sleep(randint(5,10))

