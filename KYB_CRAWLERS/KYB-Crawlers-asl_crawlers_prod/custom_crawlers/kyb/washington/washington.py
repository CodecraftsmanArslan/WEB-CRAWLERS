"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from time import sleep
from CustomCrawler import CustomCrawler
import  warnings, math, requests,random
warnings.filterwarnings("ignore")

meta_data = {
    'SOURCE' :'Washington Secretary of State',
    'COUNTRY' : 'Washington',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx", 
                        "Source Description": "The Washington Secretary of State website serves as the official online platform for the Office of the Secretary of State in the state of Washington, USA. It provides a wide range of services and resources related to business filings, elections, and government information. The website offers various tools and features to assist individuals"},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Washington Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

washington_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  washington_crawler.get_requests_helper()

# def get_proxies(max_retries=3, retry_delay=5):
#     retries = 0
#     while retries < max_retries:
#         proxy_response = requests.get('https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/US/any/username/direct/US/')
#         if proxy_response.status_code == 200:
#             # Split the response text by newline character to get a list of proxies
#             proxy_list = proxy_response.text.split('\n')
#             proxies = [proxy.strip() for proxy in proxy_list if proxy.strip()]
#             if proxies:
#                 return random.choice(proxies)
#             else:
#                 print("No proxies available. Retrying in {} seconds...".format(retry_delay))
#                 time.sleep(retry_delay)
#         else:
#             print("Failed to retrieve proxies. Status code:", proxy_response.status_code)
#             retries += 1
#             print("Retrying in {} seconds...".format(retry_delay))
#             time.sleep(retry_delay)
#     print("Exceeded maximum number of retries. No proxies available.")
#     return None

def get_proxy_list():
    response = request_helper.make_request("https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/username/direct/-/")
    data = response.text
    lines = data.strip().split('\n')
    proxy_list = [line.replace('\r', '') for line in lines]
    return proxy_list

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
    arguments = sys.argv
    PAGE_NUM = int(arguments[1]) if len(arguments)>1 else 1
    
    BUSSINESS_STATUS_API = 'https://cfda.sos.wa.gov/api/Lookup/GetLookUpData?name=BusinessStatus'
    API_URL = f'https://cfda.sos.wa.gov/api/BusinessSearch/GetAdvanceBusinessSearchList'
        
    headers = {
        "accept":"application/json, text/plain, */*",
        "content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "accept":"multipart/form-data",
        "user-agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    while True:
        bussiness_response = make_request(BUSSINESS_STATUS_API)
        STATUS_CODE = bussiness_response.status_code
        DATA_SIZE = len(bussiness_response.content)
        CONTENT_TYPE = bussiness_response.headers['Content-Type'] if 'Content-Type' in bussiness_response.headers else 'N/A'
        if not bussiness_response:
            print("bussiness_response is here", bussiness_response)
            continue
        if bussiness_response.status_code == 200:
            bussiness_statuses = bussiness_response.json()
            break
        else:
            sleep(3)
    # bussiness_statuses = [1,10,3,6,9,2,15,8,7,12,5,11,13,4]
    for bussiness_status in bussiness_statuses:
        Key = bussiness_status
        payload = {
                "Type":"Agent",
                "BusinessStatusID":Key,
                "SearchEntityName":"",
                "SearchType":"",
                "BusinessTypeID":0,
                "AgentName":"",
                "PrincipalName":"",
                "StartDateOfIncorporation":"",
                "EndDateOfIncorporation":"",
                "ExpirationDate": "",
                "IsSearch":True,
                "IsShowAdvanceSearch":True,
                "AgentAddress[IsAddressSame]":False,
                "AgentAddress[IsValidAddress]":False,
                "AgentAddress[isUserNonCommercialRegisteredAgent]":False,
                "AgentAddress[IsInvalidState]":False,
                "AgentAddress[baseEntity][FilerID]":0,
                "AgentAddress[baseEntity][UserID]":0,
                "AgentAddress[baseEntity][CreatedBy]":0,
                "AgentAddress[baseEntity][ModifiedBy]":0,
                "AgentAddress[FullAddress]":", WA, USA",
                "AgentAddress[ID]":0,
                "AgentAddress[State]":"WA",
                "AgentAddress[Country]":"USA",
                "PrincipalAddress[IsAddressSame]":False,
                "PrincipalAddress[IsValidAddress]":False,
                "PrincipalAddress[isUserNonCommercialRegisteredAgent]":False,
                "PrincipalAddress[IsInvalidState]":False,
                "PrincipalAddress[baseEntity][FilerID]":0,
                "PrincipalAddress[baseEntity][UserID]":0,
                "PrincipalAddress[baseEntity][CreatedBy]":0,
                "PrincipalAddress[baseEntity][ModifiedBy]":0,
                "PrincipalAddress[FullAddress]":", WA, USA",
                "PrincipalAddress[ID]":0,
                "PrincipalAddress[State]":"",
                "PrincipalAddress[Country]":"USA",
                "IsHostHomeSearch":"",
                "IsPublicBenefitNonProfitSearch":"",
                "IsCharitableNonProfitSearch":"",
                "IsGrossRevenueNonProfitSearch":"",
                "IsHasMembersSearch":"",
                "IsHasFEINSearch":"",
                "NonProfit[IsNonProfitEnabled]":False,
                "NonProfit[chkSearchByIsHostHome]":False,
                "NonProfit[chkSearchByIsPublicBenefitNonProfit]":False,
                "NonProfit[chkSearchByIsCharitableNonProfit]":False,
                "NonProfit[chkSearchByIsGrossRevenueNonProfit]":False,
                "NonProfit[chkSearchByIsHasMembers]":False,
                "NonProfit[chkSearchByIsHasFEIN]":False,
                "NonProfit[FEINNoSearch]":"",
                "NonProfit[chkIsHostHome][none]":False,
                "NonProfit[chkIsHostHome][yes]":False,
                "NonProfit[chkIsHostHome][no]":False,
                "NonProfit[chkIsPublicBenefitNonProfit][none]":False,
                "NonProfit[chkIsPublicBenefitNonProfit][yes]":False,
                "NonProfit[chkIsPublicBenefitNonProfit][no]":False,
                "NonProfit[chkIsCharitableNonProfit][none]":False,
                "NonProfit[chkIsCharitableNonProfit][yes]":False,
                "NonProfit[chkIsCharitableNonProfit][no]":False,
                "NonProfit[chkIsGrossRevenueNonProfit][none]":False,
                "NonProfit[chkIsGrossRevenueNonProfit][yes]":False,
                "NonProfit[chkIsGrossRevenueNonProfit][no]":False,
                "NonProfit[chkIsGrossRevenueNonProfit][over500k]":False,
                "NonProfit[chkIsGrossRevenueNonProfit][under500k]":False,
                "NonProfit[chkIsHasMembers][none]":False,
                "NonProfit[chkIsHasMembers][yes]":False,
                "NonProfit[chkIsHasMembers][no]":False,
                "NonProfit[chkIsHasFEIN][yes]":False,
                "NonProfit[chkIsHasFEIN][no]":False,
                "PageID":1,
                "PageCount":25
            }
        while True:
            data_response = make_request(API_URL, method='POST', data = payload, headers=headers)
            if not data_response:
                    print("data_response is here", data_response)
                    continue
            if data_response.status_code == 200:
                data_res = data_response.json()
                TotalRowCount = data_res[0]['Criteria']['TotalRowCount']
                PageCount = math.ceil(TotalRowCount/payload['PageCount'])
                break
            else:
                sleep(3)
        for page_num in range(PAGE_NUM,PageCount+1):
            payload['PageID'] = page_num

            print("Page Number", page_num)
            while True:
                data_response_ = make_request(API_URL, method='POST', data = payload, headers=headers)
                if not data_response_:
                    print("Data_response")
                    continue
                if data_response_.status_code == 200:
                    data_res_ = data_response_.json()
                    break
                else:
                    sleep(3)
            for data in data_res_:
                BusinessID = data['BusinessID']
                business_api = f'https://cfda.sos.wa.gov/api/BusinessSearch/BusinessInformation?businessID={BusinessID}'
                while True:
                    response = make_request(business_api)
                    if not response:
                        print("BusinessID response is here")
                        continue
                    if response.status_code == 200:
                        business_data = response.json()
                        break
                    else:
                        sleep(3)
                
                FILING_API = f'https://cfda.sos.wa.gov/api/BusinessSearch/GetBusinessFilingList?IsOnline=true&businessId={BusinessID}'
                while True:
                    filing_response = make_request(FILING_API)
                    if not filing_response:
                        print("filing_response is here")
                        continue
                    if filing_response.status_code ==200:
                        filings_details = filing_response.json()
                        break
                    else:
                        sleep(3)

                filings_details_ = []
                for filing_detail in filings_details:
                    filing_ = {
                            "filing_code":str(filing_detail['FilingNumber']),
                            "date":filing_detail['FilingDateTime'].split("T")[0],
                            "meta_detail":{
                                "effective_date":filing_detail['EffectiveDate'].replace("T00:00:00","")
                            },
                            "filing_type":filing_detail['FilingTypeName']
                    }
                    filings_details_.append(filing_)
                previous_api = f'https://cfda.sos.wa.gov/api/BusinessSearch/GetBusinessNameHistoryList?businessId={BusinessID}'
                while True:
                    previous_response = make_request(previous_api)
                    if not previous_response:
                        print("previous_response is here")
                        continue
                    if previous_response.status_code ==200:
                        previous_NAME_DATA = previous_response.json()
                        break
                    else:
                        sleep(3)
                if len(previous_NAME_DATA) == 0:
                    previous_NAME = []
                else:
                    previous_NAME = []
                    for previous_name_ in previous_NAME_DATA:
                        previous_name = {
                            "name":previous_name_.get('OldName','').replace("%","%%"),
                            "update_date":previous_name_.get('FilingDateTime','').replace('T08:12:23',""),
                            "meta_detail":{
                                "new_name":previous_name_.get('NewName','').replace("%","%%"),
                                "code":str(previous_name_.get('FilingNumber','')),
                            }
                        }
                        previous_NAME.append(previous_name)
                
                for principlist in business_data['PrincipalsList']:
                    title = principlist['PrincipalBaseType']
                    e_type = principlist['TypeID']
                    ful_name = principlist['FullName'] if principlist['FullName'] is not None else ""
                    c_name = principlist['FirstName'] + ' ' + principlist['LastName']


                OBJ = {
                        "name":business_data['BusinessName'].replace("\t","").replace("%","%%").replace("\"",""),
                        "registration_number":business_data['UBINumber'],
                        "type":business_data['BusinessType'],
                        "status":business_data['BusinessStatus'],
                        "addresses_detail":[
                            {
                                "type":"office_address",
                                "address": business_data['PrincipalOffice']['PrincipalStreetAddress']['FullAddress'].replace("%","%%")
                            },
                            {
                                "type":"postal_address",
                                "address": business_data['PrincipalOffice']['PrincipalMailingAddress']['FullAddress'].replace("%","%%")
                            }
                        ],
                        "expiration_date":business_data['NextARDueDate'].replace('T00:00:00',""),
                        "registration_date":business_data['DateOfIncorporation'],
                        "period_of_duration":'',
                        "inactive_date":business_data['InActiveDate'].replace('T00:00:00',""),
                        "industries":business_data['BINAICSCodeDesc'].replace("%","%%"),
                        "people_detail":[
                                    {
                                        "designation": "registered_agent",
                                        "name": business_data['Agent']['FullName'].replace("%","%%"),
                                        'address': business_data['Agent']['StreetAddress']['FullAddress'].replace("%","%%"),
                                        "postal_address": business_data['Agent']['MailingAddress']['FullAddress'].replace("%","%%")
                                    },
                                    {
                                        "designation": title,
                                        "meta_detail":{
                                            "entity_type": e_type,
                                            "entity_name": ful_name.replace("%","%%"),
                                        },
                                        "name": str(c_name).strip().replace("%","%%")
                                    }
                                ],
                        "fillings_detail":filings_details_,
                        "previous_names_detail":previous_NAME
                    }
                print(OBJ)
                OBJ =  washington_crawler.prepare_data_object(OBJ)
                ENTITY_ID = washington_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
                NAME = OBJ['name']
                BIRTH_INCORPORATION_DATE = ""
                ROW = washington_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                washington_crawler.insert_record(ROW)

    washington_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    washington_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    washington_crawler.db_log(log_data)

    