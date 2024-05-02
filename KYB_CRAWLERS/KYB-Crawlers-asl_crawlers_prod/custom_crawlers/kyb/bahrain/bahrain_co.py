"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from dateutil import parser
from CustomCrawler import CustomCrawler
import json, requests
import os

meta_data = {
    'SOURCE': 'Ministry of Industry and Commerce - Commercial Registration Portal - SIJILAT',
    'COUNTRY': 'Bahrain',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.sijilat.bh/",
                      "Source Description": "The Commercial Registration Portal (SIJILAT) was launched in cooperation with the Information & eGovernment Authority and government agencies (of Bahrain) competent with business licenses in May, 2015. The commercial registers system (a single virtual platform for business) is a strategic and ambitious project for the Kingdom of Bahrain that provides a service to complete all business transactions in full on the internet. It aims to create a highly efficient and advanced electronic system in the field of registering and licensing of commercial and industrial establishments."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.sijilat.bh/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bahrain Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv
FILE_PATH = os.path.dirname(os.getcwd()) + "/bahrain"

bahrain_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = bahrain_crawler.get_requests_helper()

start_page = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 1
total_pages = 3042


# This AUTH token we manually have to change after few days as it expires.
AUTH_TOKEN = "Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJTaWppbGF0IiwidXNlcm5hbWUiOiJ1c2VyIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6IkhpIFNpamlsYXQiLCJuYmYiOjE3MDQ0MzM4OTQsImV4cCI6MTcwNDUyMDI5NCwiaXNzIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6NDQzMTIvIiwiYXVkIjoiYWxsIn0.aGkPgUlc9yS6ctUteFmAkzVyG56qkL2fxj6LzNES5SI"


def format_date(timestamp):
    # It will format the date and replace "/" with "-"
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str


def crawl():
    # The first API gets the CR no and Branch no of the companies, second part takes those two as payload and calls the API to fetch the data for that company.
    for i in range(start_page, total_pages):

        url = "https://api.sijilat.bh/api/CRdetails/AdvanceSearchCR_Paging"

        payload = {
            "draw": 2,
            "columns": [
                {"data": "CR_NO", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "CR_LNM", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "CR_ANM", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "CM_TYP_DESC", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "REG_DATE", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "EXPIRE_DATE", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "STATUS", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "ACTIVITIES", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
                {"data": "SECTOR", "name": "", "searchable": True,
                    "orderable": False, "search": {"value": "", "regex": False}},
            ],
            "order": [],
            "start": 0,
            "length": 100,
            "search": {"value": "", "regex": False},
            "CR_NO": "",
            "CR_LNM": "",
            "CR_ANM": "",
            "CM_TYP_CD": "",
            "STATUS": "",
            "CR_MUNCP_CD": "",
            "CR_BLOCK": "",
            "CM_NAT_CD": "",
            "FIRST_LEV": "",
            "PERSON_LNM": "",
            "PERSON_ANM": "",
            "PTNER_NAT_CD": "",
            "REG_DATE_FROM": "01/01/1902",
            "REG_DATE_TO": "10/10/2023",
            "CR_ROAD": "",
            "CR_FLAT": "",
            "CR_BULD": "",
            "PSPORT_NO": "",
            "PTNER_CR_NO": "",
            "VCR_YN": "",
            "ISIC4_CD": "",
            "CurrentMenuType": "A",
            "cpr_no": "",
            "CULT_LANG": "EN",
            "PaginationParams": {"Page": i, "ItemPerPage": 100}
        }

        json_payload = json.dumps(payload)

        cookie_response = requests.get(
            "https://api.sijilat.bh/api/Dropdown/NatOwnershipDropdown")
        cookies = cookie_response.cookies.get_dict()
        awsalb = cookies["AWSALB"]
        awsalbcors = cookies["AWSALBCORS"]

        headers = {
            'authority': 'api.sijilat.bh',
            'method': 'POST',
            'path': '/api/CRdetails/AdvanceSearchCR_Paging',
            'Authorization': AUTH_TOKEN,
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.sijilat.bh',
            'Referer': 'https://www.sijilat.bh/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Cookie': f'AWSALB={awsalb}; AWSALBCORS={awsalbcors}'
        }
        
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            response = requests.request(
                "POST", url, headers=headers, data=json_payload)
            if not response:
                print("No Initial Response")
            if response.status_code == 200:
                data = response.json()
                break
            else:
                print(f"Initial Error Code: {response.status_code}")
            attempts += 1

        with open(f"{FILE_PATH}/crawled_pages.txt", "a") as crawled_records:
            crawled_records.write(str(i) + "\n")
        all_companies = data["jsonData"].get("CR_list", "")

        for company in all_companies:
            cr_no = company.get("CR_NO", "")
            branch_number = company.get("BRANCH_NO", "")
            query_number = cr_no + "-" + branch_number

            url2 = "https://api.sijilat.bh/api/CRdetails/CompleteCRDetails"

            payload2 = {"cr_no": f"{cr_no}", "branch_no": f"{branch_number}", "cult_lang": "EN", "Input_CULT_LANG": "EN", "CULT_LANG": "EN", "cultLang": "EN", "CurrentMenuTyp": "A", "CurrentMenu_Type": "A", "cpr_no": "",
                        "CPR_NO_LOGIN": "", "CPR_GCC_NO": "", "CPR_OR_GCC_NO": "", "Login_CPR_No": "", "Login_CPR": "", "APPCNT_CPR_NO": "", "cprno": "", "LOGIN_PB_NO": "", "PB_NO": "", "Input_PB_NO": "", "SESSION_ID": "qn0vwnar2zljerme0csmhkyq"}

            headers2 = {
                'authority': 'api.sijilat.bh',
                'method': 'POST',
                'path': '/api/CRdetails/CompleteCRDetails',
                'scheme': 'https',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Authorization': AUTH_TOKEN,
                'Cache-Control': 'no-cache',
                'Content-Length': '361',
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://www.sijilat.bh',
                'Pragma': 'no-cache',
                'Referer': 'https://www.sijilat.bh/',
                'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
            }

            while True:
                response2 = requests.request(
                    "POST", url2, headers=headers2, json=payload2)
                if not response2:
                    print("No data response")
                    time.sleep(5)
                    continue
                if response2.status_code == 200:
                    data2 = response2.json()
                    break
                else:
                    print(f"Data Error Code {response2.status_code}")
                    time.sleep(5)

            addresses_detail = []
            people_detail = []
            all_activity_data = []
            all_previous_activity_data = []
            all_capital_data = []
            all_branches_data = []

            if data2["jsonData"]:
                all_company_data = data2["jsonData"].get("company_summary", "")
                if all_company_data:
                    name_ = all_company_data.get(
                        "CR_LNM", "") if all_company_data.get("CR_LNM", "") else ""
                    alias = all_company_data.get(
                        "CR_ANM", "") if all_company_data.get("CR_ANM", "") else ""
                    group_name = all_company_data.get(
                        "CR_GRP_LNM", "") if all_company_data.get("CR_GRP_LNM", "") else ""
                    group_name_in_arabic = all_company_data.get(
                        "CR_GRP_ANM", "") if all_company_data.get("CR_GRP_ANM", "") else ""
                    registration_number = all_company_data.get("CR_NO", "") + "-" + all_company_data.get(
                        "BRANCH_NO", "") if all_company_data.get("CR_NO", "") and all_company_data.get("BRANCH_NO", "") else ""
                    print(
                        f"Scraping Data for {registration_number} on page # {i}")
                    type_ = all_company_data.get("CM_TYP_DESC", "") if all_company_data.get(
                        "CM_TYP_DESC", "") else ""
                    registration_date = format_date(all_company_data.get(
                        "REG_DATE", "")) if all_company_data.get("REG_DATE", "") else ""
                    expiry_date = format_date(all_company_data.get(
                        "EXPIRE_DATE", "")) if all_company_data.get("EXPIRE_DATE", "") else ""
                    status_ = all_company_data.get(
                        "STATUS", "") if all_company_data.get("STATUS", "") else ""
                    financial_year_end = all_company_data.get(
                        "FN_YEAR_END", "") if all_company_data.get("FN_YEAR_END", "") else ""
                    nationality = all_company_data.get(
                        "CR_NAT", "") if all_company_data.get("CR_NAT", "") else ""
                    period_ = all_company_data.get("PRD", "").replace(
                        "N/A", "") if all_company_data.get("PRD", "") else ""

                business_activities = data2["jsonData"].get(
                    "businessActivities", "")
                if business_activities:
                    for activity in business_activities:
                        code = activity.get("ISIC4_CD", "") if activity.get(
                            "ISIC4_CD", "") else ""
                        activities = activity.get("ISIC4_NM", "") if activity.get(
                            "ISIC4_NM", "") else ""
                        ac_status = "Not Restricted"
                        ac_description = activity.get(
                            "ISIC4_DETL", "") if activity.get("ISIC4_DETL", "") else ""
                        activity_dict = {
                            "code": code,
                            "activites": activities,
                            "status": ac_status,
                            "description": ac_description.replace("\r\n", ",").replace("\r\n-", ",").replace("\"", "")
                        }

                        all_activity_data.append(activity_dict)

                url3 = "https://api.sijilat.bh/api/Actitvity/ViewOld_ActivityDetails"

                payload3 = {
                    "CR_NO": "0",
                    "BRANCH_NO": "1",
                    "cult_lang": "EN",
                    "Input_CULT_LANG": "EN",
                    "CULT_LANG": "EN",
                    "cultLang": "EN",
                    "CurrentMenuTyp": "A",
                    "CurrentMenu_Type": "A",
                    "cpr_no": "",
                    "CPR_NO_LOGIN": "",
                    "CPR_GCC_NO": "",
                    "CPR_OR_GCC_NO": "",
                    "Login_CPR_No": "",
                    "Login_CPR": "",
                    "APPCNT_CPR_NO": "",
                    "cprno": "",
                    "LOGIN_PB_NO": "",
                    "PB_NO": "",
                    "Input_PB_NO": "",
                    "SESSION_ID": "qn0vwnar2zljerme0csmhkyq"
                }

                headers3 = {
                    'authority': 'api.sijilat.bh',
                    'method': 'POST',
                    'path': '/api/Actitvity/ViewOld_ActivityDetails',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Authorization': AUTH_TOKEN,
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Origin': 'https://www.sijilat.bh',
                    'Referer': 'https://www.sijilat.bh/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
                }

                while True:
                    response3 = requests.request(
                        "POST", url3, headers=headers3, json=payload3)
                    if not response3:
                        print("No Response for Previous Activity")
                        time.sleep(10)
                        continue
                    if response3.status_code == 200:
                        data3 = response3.json()
                        break
                    else:
                        print(
                            f"Previous Activity error code: {response3.status_code}")
                        time.sleep(5)

                previous_activity_data = data3["jsonData"]
                if previous_activity_data:
                    for previous_data in previous_activity_data:
                        local_code = previous_data.get(
                            "Local_Code", "") if previous_data.get("Local_Code", "") else ""
                        international_code = previous_data.get(
                            "International_Code", "") if previous_data.get("International_Code", "") else ""
                        activity_name = previous_data.get(
                            "Old_Activity_NM", "") if previous_data.get("Old_Activity_NM", "") else ""
                        activity_code = previous_data.get(
                            "ISIC4Code", "") if previous_data.get("ISIC4Code", "") else ""
                        description_of_activity = previous_data.get(
                            "Business_Description", "") if previous_data.get("Business_Description", "") else ""
                        sufficient_funds = previous_data.get(
                            "Sufficient_Fund", "") if previous_data.get("Sufficient_Fund", "") else ""
                        previous_activity_dict = {
                            "local_code": local_code,
                            "international_code": international_code,
                            "name": activity_name,
                            "code": activity_code,
                            "description": description_of_activity.replace("\r\n", "").replace("\r\n-", "").replace("\"", ""),
                            "sufficient_fund": sufficient_funds
                        }
                        all_previous_activity_data.append(
                            previous_activity_dict)

                commercial_data = data2["jsonData"].get(
                    "commercialAddress", "")
                if commercial_data:
                    company_address = (commercial_data.get("CR_FLAT", "") if commercial_data.get("CR_FLAT", "") else "") + ", " + (commercial_data.get("CR_BULD", "") if commercial_data.get("CR_BULD", "") else "") + ", " + (commercial_data.get("CR_ROAD", "") if commercial_data.get("CR_ROAD", "") else "") + ", " + (
                        commercial_data.get("CR_ROAD_NM", "") if commercial_data.get("CR_ROAD_NM", "") else "") + ", " + (commercial_data.get("CR_BLOCK", "") if commercial_data.get("CR_BLOCK", "") else "") + ", " + (commercial_data.get("CR_TOWN_NM", "") if commercial_data.get("CR_TOWN_NM", "") else "")
                    postal_address = company_address + " " + \
                        (commercial_data.get("CR_PBOX", "")
                         if commercial_data.get("CR_PBOX", "") else "").strip()

                    general_address_dict = {
                        "type": "general_address",
                        "address": company_address
                    }
                    postal_address_dict = {
                        "type": "postal_address",
                        "address": postal_address
                    }

                    addresses_detail.append(general_address_dict)
                    addresses_detail.append(postal_address_dict)

                    website = commercial_data.get(
                        "CR_URL", "") if commercial_data.get("CR_URL", "") else ""
                    e_store = commercial_data.get(
                        "ESTORE_URL", "") if commercial_data.get("ESTORE_URL", "") else ""

                partners_data = data2["jsonData"].get("company_Partners", "")
                if partners_data:
                    for partner in partners_data:
                        partner_id = partner.get(
                            "ID_NO", "") if partner.get("ID_NO", "") else ""
                        partner_name = partner.get(
                            "LNM", "") if partner.get("LNM", "") else ""
                        partner_arabic_name = partner.get(
                            "ANM", "") if partner.get("ANM", "") else ""
                        partner_nationality = partner.get(
                            "NAT_LNM", "") if partner.get("NAT_LNM", "") else ""
                        partner_dict = {
                            "meta_detail": {
                                "id": partner_id,
                                "name_in_arabic": partner_arabic_name
                            },
                            "designation": "partner",
                            "name": partner_name,
                            "nationality": partner_nationality
                        }
                        people_detail.append(partner_dict)

                authorized_persons_data = data2["jsonData"].get(
                    "authorizedSignatories", "")
                if authorized_persons_data:
                    for auth_person in authorized_persons_data:
                        auth_name = auth_person.get(
                            "NAME", "") if auth_person.get("NAME", "") else ""
                        auth_nationality = auth_person.get(
                            "NAT_NM", "") if auth_person.get("NAT_NM", "") else ""
                        auth_arabic_name = auth_person.get(
                            "ANM", "") if auth_person.get("ANM", "") else ""
                        auth_auth_level = auth_person.get(
                            "SIG_LEV", "") if auth_person.get("SIG_LEV", "") else ""
                        auth_dict = {
                            "designation": "authorized_person",
                            "name": auth_name,
                            "nationality": auth_nationality,
                            "meta_detail": {
                                "name_in_arabic": auth_arabic_name,
                                "authority_level": auth_auth_level
                            }
                        }
                        people_detail.append(auth_dict)

                partner_shareholder_data = data2["jsonData"].get(
                    "shareholdersAndPartners", "")
                if partner_shareholder_data:
                    for psh_data in partner_shareholder_data:
                        psh_name = psh_data.get(
                            "NAME", "") if psh_data.get("NAME", "") else ""
                        psh_nationality = psh_data.get(
                            "NAT_NAME", "") if psh_data.get("NAT_NAME", "") else ""
                        psh_arabic_name = psh_data.get(
                            "ANM", "") if psh_data.get("ANM", "") else ""
                        psh_no_of_shares = psh_data.get(
                            "NUM_SHARE", "") if psh_data.get("NUM_SHARE", "") else ""
                        psh_ownership_percentage = psh_data.get(
                            "RATIO_ONER", "") if psh_data.get("RATIO_ONER", "") else ""
                        psh_mortgagor_status = psh_data.get(
                            "MORTGAGE", "") if psh_data.get("MORTGAGE", "") else ""
                        psh_sequested_status = psh_data.get(
                            "SEQUESTER", "") if psh_data.get("SEQUESTER", "") else ""
                        psh_dict = {
                            "designation": "partner/shareholder",
                            "name": psh_name,
                            "nationality": psh_nationality,
                            "meta_detail": {
                                "name_in_arabic": psh_arabic_name,
                                "share": psh_no_of_shares,
                                "ownership_percentage": psh_ownership_percentage,
                                "mortgagor_status": psh_mortgagor_status,
                                "sequester_status": psh_sequested_status
                            }
                        }
                        people_detail.append(psh_dict)

                capital_details = data2["jsonData"].get(
                    "companyCapitalDetails", "")
                if capital_details:
                    auth_capital = capital_details.get(
                        "AUTH_CAPTL", "") if capital_details.get("AUTH_CAPTL", "") else ""
                    issued_capital = capital_details.get(
                        "ISU_CAPTL", "") if capital_details.get("ISU_CAPTL", "") else ""
                    total_shares = capital_details.get(
                        "TOT_SHARE", "") if capital_details.get("TOT_SHARE", "") else ""
                    share_nominal_value = capital_details.get(
                        "NOM_VAL", "") if capital_details.get("NOM_VAL", "") else ""
                    local_investment = capital_details.get(
                        "LOCAL_INVEST_SUM", "") if capital_details.get("LOCAL_INVEST_SUM", "") else ""
                    gcc_investment = capital_details.get(
                        "GCC_INVEST_SUM", "") if capital_details.get("GCC_INVEST_SUM", "") else ""
                    foriegn_investment = capital_details.get(
                        "FOR_INVEST_SUM", "") if capital_details.get("FOR_INVEST_SUM", "") else ""
                    capital_currency = capital_details.get(
                        "CURR_CD", "") if capital_details.get("CURR_CD", "") else ""
                    cash_capital = capital_details.get(
                        "PAID_CASH", "") if capital_details.get("PAID_CASH", "") else ""
                    kind_capital = capital_details.get(
                        "PAID_INKIND", "") if capital_details.get("PAID_INKIND", "") else ""

                    capital_dict = {
                        "authorized": auth_capital,
                        "issued": issued_capital,
                        "total_shares": total_shares,
                        "share_nominal_value": share_nominal_value,
                        "local_investment": local_investment,
                        "gcc-investment": gcc_investment,
                        "foreign_investment": foriegn_investment,
                        "currency": capital_currency,
                        "paid_capital_in_cash": cash_capital,
                        "paid_capital_in_kind": kind_capital
                    }
                    if auth_capital or issued_capital or total_shares or share_nominal_value or local_investment or gcc_investment or foriegn_investment or capital_currency or cash_capital or kind_capital:
                        all_capital_data.append(capital_dict)

                all_branches = data2["jsonData"].get("otherbranchlist", "")
                if all_branches:
                    for branches in all_branches:
                        br_reg_no = (branches.get("CR_NO", "") if branches.get("CR_NO", "") else "") + "-" + (
                            branches.get("BRANCH_NO", "") if branches.get("BRANCH_NO", "") else "")
                        br_name = branches.get("CR_NAME", "") if branches.get(
                            "CR_NAME", "") else ""
                        br_reg_date = format_date(branches.get(
                            "REG_DATE", "")) if branches.get("REG_DATE", "") else ""
                        br_expiry_date = format_date(branches.get(
                            "EXPIRE_DATE", "")) if branches.get("EXPIRE_DATE", "") else ""
                        br_status = branches.get(
                            "STATUS", "") if branches.get("STATUS", "") else ""
                        branches_dict = {
                            "registration_number": br_reg_no,
                            "name": br_name,
                            "registration_date": br_reg_date,
                            "registry_expiry_date": br_expiry_date,
                            "status": br_status
                        }
                        all_branches_data.append(branches_dict)

                owners_data = data2["jsonData"].get("ownerInformation", "")
                if owners_data:
                    for owner in owners_data:
                        owner_name = owner.get(
                            "LNM", "") if owner.get("LNM", "") else ""
                        owner_arabic_name = owner.get(
                            "ANM", "") if owner.get("ANM", "") else ""
                        owner_nationality = owner.get(
                            "NAT_LNM", "") if owner.get("NAT_LNM", "") else ""
                        owner_dict = {
                            "designation": "owner",
                            "name": owner_name,
                            "meta_detail": {
                                "name_in_arabic": owner_arabic_name
                            },
                            "nationality": owner_nationality
                        }
                        people_detail.append(owner_dict)

                officers_data = data2["jsonData"].get("complianceOfficer", "")
                if officers_data:
                    for officer in officers_data:
                        officer_name = officer.get(
                            "CO_LNM", "") if officer.get("CO_LNM", "") else ""
                        officer_arabic_name = officer.get(
                            "CO_ANM", "") if officer.get("CO_ANM", "") else ""
                        officer_nationality = officer.get(
                            "CO_NAT_NM", "") if officer.get("CO_NAT_NM", "") else ""
                        officer_designation = officer.get(
                            "CO_POSITION", "") if officer.get("CO_POSITION", "") else ""
                        officer_termination_date = format_date(officer.get(
                            "CO_EXPIRE_DATE", "")) if officer.get("CO_EXPIRE_DATE", "") else ""
                        officer_status = officer.get("CO_STATUS_NM", "") if officer.get(
                            "CO_STATUS_NM", "") else ""
                        officer_dict = {
                            "designation": officer_designation,
                            "name": officer_name,
                            "nationality": officer_nationality,
                            "termination_date": officer_termination_date,
                            "meta_detail": {
                                "name_in_arabic": officer_arabic_name,
                                "status": officer_status
                            }
                        }
                        people_detail.append(officer_dict)

                OBJ = {
                    "name": name_,
                    "alias": alias,
                    "group_name": group_name,
                    "group_name_in_arabic": group_name_in_arabic,
                    "registration_number": registration_number,
                    "type": type_,
                    "registration_date": registration_date,
                    "expiry_date": expiry_date,
                    "status": status_,
                    "financial_year_end": financial_year_end,
                    "nationality": nationality,
                    "period": period_,
                    "e_store": e_store,
                    "additional_detail": [
                        {
                            "type": "business_activities",
                            "data": all_activity_data
                        },
                        {
                            "type": "old_activities_info",
                            "data": all_previous_activity_data
                        },
                        {
                            "type": "capital_info",
                            "data": all_capital_data
                        },
                        {
                            "type": "additional_branches_info",
                            "data": all_branches_data
                        }
                    ],
                    "addresses_detail": addresses_detail,
                    "contacts_detail": [
                        {
                            "type": "website",
                            "value": website
                        }
                    ],
                    "people_detail": people_detail
                }

                OBJ = bahrain_crawler.prepare_data_object(OBJ)
                ENTITY_ID = bahrain_crawler.generate_entity_id(
                    OBJ["registration_number"], OBJ["name"])
                BIRTH_INCORPORATION_DATE = ''
                ROW = bahrain_crawler.prepare_row_for_db(
                    ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
                bahrain_crawler.insert_record(ROW)

            else:
                print(f"No Data for {query_number} on page # {i}")
                continue

    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE


try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    bahrain_crawler.db_log(log_data)
    bahrain_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    bahrain_crawler.db_log(log_data)
