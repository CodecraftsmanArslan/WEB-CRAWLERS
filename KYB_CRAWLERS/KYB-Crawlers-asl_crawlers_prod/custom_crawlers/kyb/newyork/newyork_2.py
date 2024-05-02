"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE': 'Department of State, Division of Corporations, New York',
    'COUNTRY': 'New York',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://apps.dos.ny.gov/publicInquiry/",
                      "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://apps.dos.ny.gov/publicInquiry/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "NewYork Official Registry Source Two"
}

new_york_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = new_york_crawler.get_requests_helper()

BY_ID_URL = ("https://apps.dos.ny.gov/PublicInquiryWeb/api/PublicInquiry/GetEntityRecordByID")
BY_NAME_URL = ("https://apps.dos.ny.gov/PublicInquiryWeb/api/PublicInquiry/GetNameHistoryByID")
BY_FILING_URL = ("https://apps.dos.ny.gov/PublicInquiryWeb/api/PublicInquiry/GetFilingHistoryByID")
BY_ASSUME_URL = ("https://apps.dos.ny.gov/PublicInquiryWeb/api/PublicInquiry/GetAssumedNameHistoryByID")

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Length': '173',
    'Content-Type': 'application/json;charset=UTF-8',
    'Cookie': '_ga=GA1.4.1129087865.1694168674; _gid=GA1.4.730741310.1694168674; nmstat=40875d64-a824-9651-3304-55fc746b2da4; TS00000000076=084c043756ab2800d26282ac859ef26c4056f8ced69229bda2d6a257df2a3bb019c238792ba1f13455532709c2d35e5e08235aee4809d000fb855c4361f88f1a56efba0a3acc787419c7a3f21127b3e787d385a4c55ca79bf29097072ec7f2391483b4d13eb6c82d5a5d2176a28760af27e60876194620488f0b926996913128b5eef7ee72c6cc0255b1a01b906882a024ad922a27703cfdf69e174005f3d8a16dbef9d5ff6f604241fcbd6258ce5744bb2e2ba5d721070c4c2dea36336a339849961be0176963155ae3d1faed7769d6a8ff305cf257312aa7076a60108c5fba98d6b7b669fd9aaacfcbb8fe2de7f340f2ba05878097c3ffc87077727c4af57f6449c9cb03c98c75; TSPD_101_DID=084c043756ab2800d26282ac859ef26c4056f8ced69229bda2d6a257df2a3bb019c238792ba1f13455532709c2d35e5e08235aee48063800da6ae466cf866542855469f26169691b6ee37209b8848a8ba2eb9e146727e38b8e73d7ebb879ed90b0f896416cfabba1e6a968e86429711b; TSPD_101=084c043756ab28000bb418ae05e04b4c912a127df033cc828738a65e87952849436617ef1316c78e4f83464b0c13d178081c6103fd051800d769f6b0a355369bdfa0af9ff479231cac9a412850bfed94; TS969a1eaa027=084c043756ab200036755ee560225b029ba83adc428b996ada3da13ae90ef9774dfbc12063de80d4086e6e443b113000d44f238b96990a01086384efc119e5f06bc6008cfd40fa5a146a39a8d822d20652623c318c14c77e390a2877bc39f8d9; TSbb0d7d7a077=084c043756ab2800fe5f0170c053f1a2c3029937e6c60730f636b40f607bc61a5b723733d2c493d9e5da60c8bd82fe6e08a271daf01720006a2fac27dacc684a244901965a7504ea06116e667aae0a20199f50bb8290401e',
    'Host': 'apps.dos.ny.gov',
    'Origin': 'https://apps.dos.ny.gov',
    'Referer': 'https://apps.dos.ny.gov/publicInquiry/NameHistory',
    'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}
def get_data(data_id, data_name, data_filing, data_assume):
    registration_number = data_id["entityGeneralInfo"].get("dosID", "")
    name_ = data_id["entityGeneralInfo"].get("entityName", "")
    trade_name = data_id["entityGeneralInfo"].get("foreignLegalName", "")
    aliases = data_id["entityGeneralInfo"].get("fictitiousName", "")
    type_ = data_id["entityGeneralInfo"].get("entityType", "")
    dissolution_date = data_id["entityGeneralInfo"].get("durationDate", "")
    section_of_law = data_id["entityGeneralInfo"].get("sectionofLaw", "")
    status_ = data_id["entityGeneralInfo"].get("entityStatus", "")
    dos_filing_date = data_id["entityGeneralInfo"].get("dateOfInitialDosFiling", "").split("T")[0]
    effective_date = data_id["entityGeneralInfo"].get("effectiveDateInitialFiling", "").split("T")[0]
    status_reason = data_id["entityGeneralInfo"].get("reasonForStatus", "")
    formation_date = data_id["entityGeneralInfo"].get("foreignFormationDate", "").split("T")[0]
    inactive_date = data_id["entityGeneralInfo"].get("inactiveDate", "").split("T")[0]
    statement_status = data_id["entityGeneralInfo"].get("statementStatus", "")
    county = data_id["entityGeneralInfo"].get("county", "")
    statement_due_date = data_id["entityGeneralInfo"].get("nextStatementDueDate", "").split("T")[0]
    jurisdiction = data_id["entityGeneralInfo"].get("jurisdiction", "")
    non_for_profit_category = data_id["entityGeneralInfo"].get("nfpCategory", "")

    people_detail_data = []

    sop_name = data_id["sopAddress"].get("name", "")
    sop_street = data_id["sopAddress"]["address"].get("streetAddress", "")
    sop_country = data_id["sopAddress"]["address"].get("country", "")
    sop_city = data_id["sopAddress"]["address"].get("city", "")
    sop_state = data_id["sopAddress"]["address"].get("state", "")
    sop_zip = data_id["sopAddress"]["address"].get("zipCode", "")
    sop_address = (sop_street + " " + sop_country + " " + sop_city + " " + sop_state + " " + sop_zip)
    sop_address = sop_address.strip()
    if sop_name != "" and sop_address != "":
        sop_details = {
            "designation": "secretary",
            "name": sop_name.replace("%", ""),
            "address": sop_address.strip()
        }
        people_detail_data.append(sop_details)
    else:
        pass

    ceo_address = data_id["ceo"].get("address", "") if data_id["ceo"]["address"] is not {} else "" 
    ceo_name = ""
    if ceo_address != "" and ceo_name != "":
        ceo_details = {
                    "designation": "ceo",
                    "name": ceo_name,
                    "address": ceo_address  
                    }
        people_detail_data.append(ceo_details)
    else:
        pass

    exec_street = data_id["poExecAddress"]["address"].get("streetAddress", "")
    exec_country = data_id["poExecAddress"]["address"].get("country", "")
    exec_city = data_id["poExecAddress"]["address"].get("city", "")
    exec_state = data_id["poExecAddress"]["address"].get("state", "")
    exec_zip = data_id["poExecAddress"]["address"].get("zipCode", "")
    p_exec_office = exec_street + " " + exec_country + " " + exec_city + " " + exec_state + " " + exec_zip 
    
    reg_street = data_id["registeredAgent"]["address"].get("streetAddress", "")
    reg_country = data_id["registeredAgent"]["address"].get("country", "")
    reg_city = data_id["registeredAgent"]["address"].get("city", "")
    reg_state = data_id["registeredAgent"]["address"].get("state", "")
    reg_zip = data_id["registeredAgent"]["address"].get("zipCode", "")

    registered_agent_name = data_id["registeredAgent"].get("name", "")
    registered_agent_address = reg_street + " " + reg_country + " " + reg_city + " " + reg_state + " " + reg_zip
    if registered_agent_address != "" and registered_agent_name != "":
        registered_agent = {
                        "designation": "registered_agent",
                        "name": registered_agent_name.replace("%", ""),
                        "address": registered_agent_address.strip()
                        }
        people_detail_data.append(registered_agent)
        
    else:
        pass
    
    primary_street = data_id["locationAddress"]["address"].get("streetAddress", "")
    primary_country = data_id["locationAddress"]["address"].get("country", "")
    primary_city = data_id["locationAddress"]["address"].get("city", "")
    primary_state = data_id["locationAddress"]["address"].get("state", "")
    primary_zip = data_id["locationAddress"]["address"].get("zipCode", "")
    primary_address = primary_street + " " + primary_country + " " + primary_city + " " + primary_state + " " + primary_zip
    primary_address = primary_address.strip()

    if primary_address != "" and primary_address is not None:
        address_data = {
        "designation": "representative",
        "name": "",
        "address": primary_address
    }
        people_detail_data.append(address_data)
    else:
        pass
    
    farming_corporation = str(data_id["farmCorpFlag"])

    share_detail_data = []
    stock_info = data_id.get("stockShareInfoList", "")
    if stock_info:
        share_value = stock_info[0]["stockTypeDescriptor"]
        number_of_shares = stock_info[0]["quantity"]
        value_per_share = stock_info[0]["stockValue"]

        if share_value != "" and number_of_shares != "" and value_per_share != "":
            share_data = {
                "share_value": share_value,
                "number_of_shares": number_of_shares,
                "value_per_share": value_per_share
            }
            share_detail_data.append(share_data)
        else:
            pass
    else:
        pass

# previous name details
    total_records = len(data_name["nameHistoryResultList"])
    previous_name_data = []
    for i in range(total_records):
       data_dict =  {
            "name": data_name["nameHistoryResultList"][i]["entityName"],
            "meta_detail": {
                "file_date": data_name["nameHistoryResultList"][i]["fileDate"].split("T")[0],
                "document_type": data_name["nameHistoryResultList"][i]["documentType"],
                "file_number": data_name["nameHistoryResultList"][i]["fileNumber"],
            }
       }
       previous_name_data.append(data_dict)

# filing details
    filing_record_number = len(data_filing["filingHistoryResultList"])
    filing_data = []
    if filing_record_number:
        for i in range(filing_record_number):
            dict = {
                "date": data_filing["filingHistoryResultList"][i]["fileDate"].split("T")[0],
                "filing_type": data_filing["filingHistoryResultList"][i]["documentType"],
                "title": data_filing["filingHistoryResultList"][i]["documentType"],
                "description": data_filing["filingHistoryResultList"][i]["amendmentDescription"] if data_filing["filingHistoryResultList"][i]["amendmentDescriptionFlag"] != False else "",
                "filing_code": data_filing["filingHistoryResultList"][i]["fileNumber"],
                "meta_detail": {
                     "cert_code": data_filing["filingHistoryResultList"][i]["certCode"]
                }
            }
            filing_data.append(dict)

# assumed name details

    assumed_name_data = []
    total_name_records = len(data_assume["assumedNameHistoryResultList"])
    for i in range(total_name_records):
        the_dict = {
            "file_date": data_assume["assumedNameHistoryResultList"][i].get("fileDate", "").split("T")[0],
            "name": data_assume["assumedNameHistoryResultList"][i].get("assumedName", ""),
            "file_id": data_assume["assumedNameHistoryResultList"][i].get("assumedNameID", ""),
            "status": data_assume["assumedNameHistoryResultList"][i].get("status", ""),
            "location": data_assume["assumedNameHistoryResultList"][i].get("principalLocation", "")
        }
        assumed_name_data.append(the_dict)

    OBJ = {
        "registration_number": registration_number,
        "name": name_,
        "trade_name": trade_name,
        "aliases": aliases,
        "type": type_,
        "dissolution_date": dissolution_date,
        "section_of_law": section_of_law,
        "status": status_,
        "dos_filing_date": dos_filing_date,
        "effective_date": effective_date,
        "status_reason": status_reason,
        "formation_date": formation_date,
        "inactive_date": inactive_date,
        "statement_status": statement_status,
        "county": county,
        "statement_due_date": statement_due_date,
        "jurisdiction": jurisdiction,
        "non_for_profit_category": non_for_profit_category,
        "people_detail": people_detail_data,
        "addresses_detail": [
            {
                "type": "principal_address",
                "address": p_exec_office.strip()

            }
        ],
        "farming_corporation": farming_corporation,
        "additional_detail": [
            {
                "type": "share_information",
                "data": share_detail_data
            },
            {
                "type": "assumed_name_information",
                "data": assumed_name_data
            }
        ],
        "previous_names_detail": previous_name_data,
        "fillings_detail": filing_data
    } 

    print(OBJ)

    OBJ = new_york_crawler.prepare_data_object(OBJ)
    ENTITY_ID = new_york_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = new_york_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name").replace("%","%%"), BIRTH_INCORPORATION_DATE, OBJ)
    new_york_crawler.insert_record(ROW)


def crawl():
    arguments = sys.argv
    DUMMY_COR = int(arguments[1]) if len(arguments)>1 else 18316
    for i in range(DUMMY_COR, 9999999):
        print(f"Scrapping Record Number: {i}")
        data = {"SearchID":i,"AssumedNameFlag":"false","ListSortedBy":"ALL","listPaginationInfo":{"listStartRecord":1,"listEndRecord":50}}

        while True:
            by_id_res = request_helper.make_request(url=BY_ID_URL, method="POST", json=data, headers=headers)
            if not by_id_res:
                continue
            if by_id_res.status_code == 200:
                id_data = by_id_res.json()
                break
            else:
                time.sleep(5)

        while True:
            by_name_res = request_helper.make_request(url=BY_NAME_URL, method="POST", json=data, headers=headers)
            if not by_name_res:
                continue
            if by_name_res.status_code == 200:
                name_data = by_name_res.json()
                break
            else:
                time.sleep(5)

        while True:
            by_filing_res = request_helper.make_request(url=BY_FILING_URL, method="POST", json=data, headers=headers)
            if not by_filing_res:
                continue
            if by_filing_res.status_code == 200:
                filing_data = by_filing_res.json()
                break
            else:
                time.sleep(5)

        while True:
            by_assume_res = request_helper.make_request(url=BY_ASSUME_URL, method="POST", json=data, headers=headers)
            if not by_assume_res:
                continue
            if by_assume_res.status_code == 200:
                assume_data = by_assume_res.json()
                break
            else:
                time.sleep(5)

        SATAUS_CODE = by_id_res.status_code
        DATA_SIZE = len(by_id_res.content)
        CONTENT_TYPE = (by_id_res.headers['Content-Type'] if 'Content-Type' in by_id_res.headers else 'N/A')

        get_data(data_id=id_data, data_name=name_data, data_filing=filing_data, data_assume=assume_data)

    return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE


try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
    new_york_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML"}
    new_york_crawler.db_log(log_data)
    new_york_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    new_york_crawler.db_log(log_data)