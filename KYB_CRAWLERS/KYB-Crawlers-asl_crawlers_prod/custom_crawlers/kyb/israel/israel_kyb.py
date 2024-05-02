"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import json, datetime, time
from CustomCrawler import CustomCrawler

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Ministry of Justice - Israel Corporations Authority (ICA)',
    'COUNTRY' : 'Israel',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8", 
                        "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Israel",
}


israel_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  israel_crawler.get_requests_helper()

def make_request(url, method="GET", headers={}, timeout=10, max_retries=3, retry_interval=60, json=None):
    for _ in range(max_retries + 1):
        try:
            response = requests.request(method, url, headers=headers, timeout=timeout, json=json)
            if response.status_code == 200:
                response.json()
                return response
        except:
            print(f"Error while getting request try again in {retry_interval} seconds")
            time.sleep(retry_interval)
    return None

def get_cookie():
    response = make_request("https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8")
    if response is not None and response.status_code == 200:
        cookies = response.cookies
        aspnet_session_id = cookies.get('ASP.NET_SessionId')
        p_hosting = cookies.get('p_hosting')
        return f"ASP.NET_SessionId={aspnet_session_id}; p_hosting={p_hosting}; _cls_v=fb5702d1-3af6-42b9-ab1f-ea608a4d1cfc; _cls_s=eca5c7f7-5106-44e1-a0f1-ea11c2d38b8f:0; _gid=GA1.3.1050493823.1694590791; _gat_gtag_UA_28824637_23=1; _ga=GA1.1.1655953683.1694590791; _ga_XBS0438WRW=GS1.1.1694590791.1.1.1694591955.0.0.0"
    return "_cls_v=fb5702d1-3af6-42b9-ab1f-ea608a4d1cfc; _gid=GA1.3.1050493823.1694590791; ASP.NET_SessionId=lsij2vlblody5w32ocfsn1o1; p_hosting=!IcL1SiU/kGUcGd5p0vuartGE7rkM2lg193qS6o+U3y/ZpxziaqamwXzBpJG/Kl34wPBWAnRm8ZO83Zc=; _cls_s=d0796ccb-aa9b-4dbb-bfce-3ffdf111622c:1; _gat_gtag_UA_28824637_23=1; _ga=GA1.1.1655953683.1694590791; _ga_XBS0438WRW=GS1.1.1694686592.8.1.1694686621.0.0.0"


def format_date(str):
    try:
        formatted_date = ""
        timestamp = int(str.replace("/Date(", "").replace(")/", "")) / 1000
        date_obj = datetime.datetime.fromtimestamp(timestamp)
        formatted_date = date_obj.strftime("%d-%m-%Y")
        return formatted_date
    except Exception as e:
        print(e)
        return formatted_date

def get_headers():
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": get_cookie(),
        "Host": "ica.justice.gov.il",
        "Origin": "https://ica.justice.gov.il",
        "Referer": "https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8",
        "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def prase_data(js_code):
    pattern = r'kendoListView\(\{([\s\S]*?)\}\);'
    match = re.search(pattern, js_code)
    if match:
        kendo_listview_data = match.group(0)
        data_string = kendo_listview_data.replace("kendoListView(", "").replace(");", "")
        pattern = r'\[{.*?}\]'
        matches = re.findall(pattern, data_string)
        if matches:
            return matches[0]


def get_debits(corporation_number):
    url = f"https://ica.justice.gov.il/GenericCorporarionInfo/GetDebits?corporationNumber={corporation_number}&unitId=8"
    response = make_request(url)
    if response is not None and response.status_code == 200:
        json_data = response.json()
        return json_data


def get_fillings(contact_id, contact_number):
    url = "https://ica.justice.gov.il/GenericCorporarionInfo/SearchRequests"
    data = {
        "contactId": contact_id,
        "contactNumber": contact_number
    }
    response = make_request(url, method="POST", headers=get_headers(), data=data)
    if response is not None and response.status_code == 200:
        print("Request was successful")
        json_data = response.json()
        if 'Html' in json_data:
            return prase_data(json_data['Html'])
    

def keys_mapping(data):
    result = {}
    addresses_detail = []
    fillings_detail = []
    result["name"] = data['Company']['Name']
    result["registration_number"] = f"{data['Company']['CompanyNumber']}"
    result["aliases"] = data['Company']['Name']
    result["located_in"] = data['DisplayCompanyType']
    result["status"] = data['Company']['StatusString']
    result["law_compromised"] = data['DisplayCompanyViolates']
    result["incorporation_year"] = data['ContactValidations']['LastYearlyReport']
    result["incorporation_date"] = data['DisplayCompanyRegistrationDate'].replace("/", "-") if data['DisplayCompanyRegistrationDate'] is not None else ""
    result["sub_status"] = data['DisplayCompanySubStatus']
    result["description"] = data['Company']['PurposeDescription']
    result["purpose"] = data['DisplayCompanyPurpose']
    result["governmet_company"] = data['Company']['IsGovernmental']
    result["limitation"] = data['DisplayCompanyLimitType']
    debits = get_debits(data['Company']['CompanyNumber'])
    result["fee_in_2023"] = debits.get('TollYearly').replace("/", "-") if debits is not None and "TollYearly" in debits else ""
    result["fee_obligations"] = debits.get('TollDebts') if debits is not None and "TollDebts" in debits else ""

    if 'Company' in data and 'Addresses' in data['Company'] and data['Company']['Addresses']:
        full_address = data['Company']['Addresses'][0]['FullAddressStringInDocument']
    else:
        full_address = ""
    country_name = data.get('Company', {}).get('CountryName', "")
    address = f"{full_address} {country_name}"
    addresses_detail.append({
        "type": "general_address",
        "address": address
    })

    fillings = get_fillings(data['Company']['Id'], data['Company']['CompanyNumber'])
    if fillings is not None:
        for filling in json.loads(fillings):
            fillings_detail.append({
                "title": filling.get('DisplayRequestType'),
                "date": format_date(filling.get('RequestCreatedDate')),
                "meta_detail": {
                    "corporate_number": filling.get('RequestContactId'),
                    "corporate_name": filling.get('RequestContactName'),
                    "filing_status": filling.get('DisplayRequestStatus'),
                    "treatment_date": format_date(filling.get('RequestStatusDate')),
                    "contact_number": filling.get('RequestId'),
                    "document_identification": "https://login.gov.il/nidp/saml2/sso?id=usernamePasswordSMSOtp&sid=2&option=credential&sid=2"
                }
            })
    result["addresses_detail"] = addresses_detail
    result["fillings_detail"] = fillings_detail
    return result

def get_record_data(num):
    url = "https://ica.justice.gov.il/GenericCorporarionInfo/SearchGenericCorporation"
    data = {
        "UnitsType": "8",
        "CorporationType": "3",
        "ContactType": "3",
        "CorporationNameDisplayed": "no",
        "CorporationNumberDisplayed": "0",
        "CorporationName": "",
        "CorporationNumber": num,
        "currentJSFunction": "Process.SearchCorporation.Search()",
        "RateExposeDocuments": "36.00",
        "TollCodeExposeDocuments": "129",
        "RateCompanyExtract": "11.00",
        "RateYearlyToll": "1614.00",
    }
    response = request_helper.make_request(url, method="POST", headers=get_headers(), data=data)
    if response is not None and response.status_code == 200:
        print("Request was successful")
        json_data = response.json()
        return json_data
try:   
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 510000000
    url = "https://apps.ilsos.gov/businessentitysearch/"
    for reg_num in range(start, 599999999):
        print("Record No.", reg_num)
        items = get_record_data(reg_num)
        if items is not None and 'Data' in items:
            for val in items['Data']:
                data = keys_mapping(val)
                ENTITY_ID = israel_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
                BIRTH_INCORPORATION_DATE = ''
                DATA = israel_crawler.prepare_data_object(data)
                ROW = israel_crawler.prepare_row_for_db(ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
                israel_crawler.insert_record(ROW)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    israel_crawler.db_log(log_data)
    israel_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    israel_crawler.db_log(log_data)
