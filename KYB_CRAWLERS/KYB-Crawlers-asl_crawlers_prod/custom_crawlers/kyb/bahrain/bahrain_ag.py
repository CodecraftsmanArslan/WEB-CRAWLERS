"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from dateutil import parser
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
import sys, traceback, time, re, requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv
AUTH_TOKEN = "Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJTaWppbGF0IiwidXNlcm5hbWUiOiJ1c2VyIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6IkhpIFNpamlsYXQiLCJuYmYiOjE2OTc2MTM2NTEsImV4cCI6MTY5NzcwMDA1MSwiaXNzIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6NDQzMTIvIiwiYXVkIjoiYWxsIn0.I-6FYK9RGnrdD-Q0mmG_Jp0H6JHreBT20aygA9Y1LEk"

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

bahrain_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = bahrain_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)
URL = "https://s2.sijilat.bh/?cultLangS3=EN&menucd=A0101108"

start_status = int(ARGUMENT[1]) - 1 if len(ARGUMENT) > 1 else 0

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def crawl():
    driver.get(URL)
    time.sleep(5)
    iframe_element = driver.find_element(By.ID, 'frame_main')
    driver.switch_to.frame(iframe_element)
    status_selector = driver.find_element(By.XPATH, '//select[@name="ctl00$BodyPlaceHolder$ddlStatus"]')
    status_selector.click()
    total_status = len(driver.find_elements(By.XPATH, '//select[@id="BodyPlaceHolder_ddlStatus"]/option'))
    continue_loop = True
    for i in range(start_status, total_status - 1):
        agency_status = driver.find_elements(By.XPATH, '//select[@id="BodyPlaceHolder_ddlStatus"]/option')[i + 1]
        agency_status.click()
        time.sleep(2)
        search_button = driver.find_element(By.ID, 'BodyPlaceHolder_btnSearch')
        search_button.click()
        time.sleep(5)
        if len(driver.find_elements(By.XPATH, '//a[contains(text(),"1000 in one page")]')) > 0:
            thousand_results_button = driver.find_element(By.XPATH, '//a[contains(text(),"1000 in one page")]')
            thousand_results_button.click()
            time.sleep(5)
        agency_data_table_div = driver.find_element(By.ID, 'tab_AR_Enqy')
        agency_data_table = agency_data_table_div.find_element(By.TAG_NAME, "tbody")
        no_of_agency_rows = len(agency_data_table.find_elements(By.TAG_NAME, "tr"))
        no_of_result_pages = len(driver.find_elements(By.CLASS_NAME, 'PagingButton1'))
        for r in range(no_of_result_pages):
            agency_data_table_div = driver.find_element(By.ID, 'tab_AR_Enqy')
            agency_data_table = agency_data_table_div.find_element(By.TAG_NAME, "tbody")
            no_of_agency_rows = len(agency_data_table.find_elements(By.TAG_NAME, "tr"))
            for n in range(no_of_agency_rows):
                agency_data_table = driver.find_element(By.ID, 'tab_AR_Enqy')
                agency_row = agency_data_table.find_elements(By.TAG_NAME, "tr")[n+1]
                all_agency_cells = agency_row.find_elements(By.TAG_NAME, "td")
                cr_no = all_agency_cells[1].text.strip().split("-")[0]
                branch_number = all_agency_cells[1].text.strip().split("-")[1]
                resume_query = int(all_agency_cells[0].text.strip())
                if len(ARGUMENT) > 2 and int(ARGUMENT[2]) != resume_query and continue_loop:
                    continue
                else:
                    continue_loop = False
                print(f"Scraping data for status: {i+1} - agency # {resume_query}.")
                agency_detail_link = all_agency_cells[0].find_element(By.TAG_NAME, "a")
                agency_detail_link.click()
                time.sleep(5)
                all_window_handles = driver.window_handles
                new_window_handle = all_window_handles[-1]
                driver.switch_to.window(new_window_handle)
                get_data(branch_number=branch_number, cr_no=cr_no)
                driver.switch_to.window(all_window_handles[0])
                iframe_element = driver.find_element(By.ID, 'frame_main')
                driver.switch_to.frame(iframe_element)
            total_results = driver.find_element(By.ID, 'BodyPlaceHolder_UC_Biz_Pager1_PageStatus1').text.split("of")[-1].replace("Results", "").strip()
            current_results = driver.find_element(By.ID, 'BodyPlaceHolder_UC_Biz_Pager1_PageStatus1').text.split("of")[0].split("-")[-1].strip()
            if int(current_results) == int(total_results):
                driver.get(URL)
                time.sleep(5)
                iframe_element = driver.find_element(By.ID, 'frame_main')
                driver.switch_to.frame(iframe_element)
                status_selector = driver.find_element(By.ID, 'BodyPlaceHolder_ddlStatus')
                status_selector.click()
            else:
                next_page_button = (driver.find_elements(By.CLASS_NAME, 'PagingButton1'))[r+1]
                next_page_button.click()
                time.sleep(5)

def get_data(cr_no, branch_number):
    time.sleep(2)
    iframe_element = driver.find_element(By.ID, 'MoveFrame')
    driver.switch_to.frame(iframe_element)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    addresses_detail = []
    people_detail = []
    
    agency_number = soup.find("th", string="Agency No.")
    agency_number = agency_number.find_next_sibling().text.strip() if agency_number else ""
    agency_status = soup.find("th", string=" Agency Status") or soup.find("th", string="Agency Status")
    agency_status = agency_status.find_next_sibling().text.strip() if agency_status else ""
    agency_registration_date = soup.find("th", string="Registration Date")
    if agency_registration_date:
        agency_registration_date = agency_registration_date.find_next_sibling().text.strip() 
        agency_registration_date = format_date(agency_registration_date)
    else:
        agency_registration_date = ""
    agency_expiry_date = soup.find("th", string="Expiration Date")
    if agency_expiry_date:
        agency_expiry_date = agency_expiry_date.find_next_sibling().text.strip()
        agency_expiry_date = format_date(agency_expiry_date)
    else:
        agency_expiry_date = ""
    agent_registration_number = soup.find("th", string=re.compile("CR No."))
    agent_registration_number = agent_registration_number.find_next_sibling().text.strip() if agent_registration_number else ""
    agent_status = soup.find("th", string=re.compile("Status"))
    agent_status = agent_status.find_next_sibling().text.strip() if agent_status else ""
    agent_com_name_ar = soup.find("th", string="Commercial Name (Arabic)")
    agent_com_name_ar = agent_com_name_ar.find_next_sibling().text.strip() if agent_com_name_ar else ""
    agent_com_name_en = soup.find("th", string="Commercial Name (English)")
    agent_com_name_en = agent_com_name_en.find_next_sibling().text.strip() if agent_com_name_en else ""
    agent_flat = soup.find("th", string="Flat / Shop No.")
    agent_flat = agent_flat.find_next_sibling().text.strip() if agent_flat else ""
    if agent_flat == "0":
        agent_flat = ""
    else:
        agent_flat = f"{agent_flat}-"
    agent_building = soup.find("th", string="Building")
    agent_building = agent_building.find_next_sibling().text.strip() if agent_building else ""
    agent_road = soup.find("th", string="Road / Street")
    agent_road = agent_road.find_next_sibling().text.strip() if agent_road else ""
    agent_block = soup.find("th", string="Block")
    agent_block = agent_block.find_next_sibling().text.strip() if agent_block else ""
    agent_town = soup.find("th", string="Town")
    agent_town = agent_town.find_next_sibling().text.strip() if agent_town else ""
    agent_po_box = soup.find("th", string="P.O. Box")
    agent_po_box = agent_po_box.find_next_sibling().text.strip() if agent_po_box else ""
    agent_physical_address = f"{agent_flat}{agent_building}, {agent_road}, {agent_block}, {agent_town}"
    agent_postal_address = f"{agent_physical_address}, {agent_po_box}"
    agent_physical_address_dict = {
        "type": "agency_general_address",
        "address": agent_physical_address
    }
    agent_postal_address_dict = {
        "type": "agency_postal_address",
        "address": agent_postal_address
    }
    addresses_detail.append(agent_physical_address_dict)
    addresses_detail.append(agent_postal_address_dict)

    agent_mobile_number = soup.find("th", string="Mobile No.")
    agent_mobile_number = agent_mobile_number.find_next_sibling().text.strip() if agent_mobile_number else ""
    agent_email_address = soup.find("th", string="Email")
    agent_email_address = agent_email_address.find_next_sibling().text.strip() if agent_email_address else ""
    agent_phone_no = soup.find("th", string="Phone No.")
    agent_phone_no = agent_phone_no.find_next_sibling().text.strip() if agent_phone_no else ""
    agent_fax_number = soup.find("th", string="Fax No.")
    agent_fax_number = agent_fax_number.find_next_sibling().text.strip() if agent_fax_number else ""

    principal_table_div = soup.find("div", string="Principal Details")
    if principal_table_div:
        principal_table = principal_table_div.find_next_sibling()
    principal_name = principal_table.find("th", string="Name")
    principal_name = principal_name.find_next_sibling().text.strip() if principal_name else ""
    principal_nationality = principal_table.find("th", string="Nationality")
    principal_nationality = principal_nationality.find_next_sibling().text.strip() if principal_nationality else ""
    principal_address = principal_table.find("th", string="Address")
    principal_address = principal_address.find_next_sibling().text.strip() if principal_address else ""
    principal_email = principal_table.find("th", string="Email")
    principal_email = principal_email.find_next_sibling().text.strip() if principal_email else ""
    principal_phone = principal_table.find("th", string=re.compile("Phone No."))
    principal_phone = principal_phone.find_next_sibling().text.strip() if principal_phone else ""
    principal_fax_number = principal_table.find("th", string=re.compile("Fax No."))
    principal_fax_number = principal_fax_number.find_next_sibling().text.strip() if principal_fax_number else ""
    principal_dict = {
        "designation": "agency_agent",
        "name": principal_name,
        "nationality": principal_nationality,
        "address": principal_address,
        "email": principal_email,
        "phone_number": principal_phone,
        "fax_number": principal_fax_number
    }
    people_detail.append(principal_dict)

    prod_ser_table_div = soup.find("div", string=re.compile("Products / Services Details"))
    if prod_ser_table_div:
        prod_ser_table = prod_ser_table_div.find_next_sibling()
        prod_ser_rows = prod_ser_table.find_all("tr")
        all_prod_details = []
        for prod_ser_row in prod_ser_rows[1:]:
            all_prod_ser_data = prod_ser_row.find_all("td")
            if len(all_prod_ser_data) > 0:
                prod_industry = all_prod_ser_data[0].text.strip()
                prod_products = all_prod_ser_data[1].text.strip()
                prod_codes = all_prod_ser_data[2].text.strip()
                prod_dict = {
                    "industry": prod_industry,
                    "products": prod_products,
                    "brand_codes": prod_codes
                }
                if prod_industry or prod_products or prod_codes:
                    all_prod_details.append(prod_dict)

    amendment_table_div = soup.find("div", string="Amendment History")
    all_amendment_details = []
    if amendment_table_div:
        amendment_table = amendment_table_div.find_next_sibling()
        amendment_table_rows = amendment_table.find_all("tr")
        for amendment_table_row in amendment_table_rows[1:]:
            amendment_data = amendment_table_row.find_all("td")
            amendment_date = amendment_data[0].text.strip()
            amendment_operation = amendment_data[1].text.strip()
            amendment_dict = {
                "date": format_date(amendment_date),
                "title": amendment_operation
            }
            if amendment_date or amendment_operation:
                all_amendment_details.append(amendment_dict)
    
    driver.close()

    url2 = "https://api.sijilat.bh/api/CRdetails/CompleteCRDetails"

    payload2 = {"cr_no":f"{cr_no}","branch_no":f"{branch_number}","cult_lang":"EN","Input_CULT_LANG":"EN","CULT_LANG":"EN","cultLang":"EN","CurrentMenuTyp":"A","CurrentMenu_Type":"A","cpr_no":"","CPR_NO_LOGIN":"","CPR_GCC_NO":"","CPR_OR_GCC_NO":"","Login_CPR_No":"","Login_CPR":"","APPCNT_CPR_NO":"","cprno":"","LOGIN_PB_NO":"","PB_NO":"","Input_PB_NO":"","SESSION_ID":"qn0vwnar2zljerme0csmhkyq"}

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
        response2 = requests.request("POST", url2, headers=headers2, json=payload2)
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

    if data2["jsonData"]:
        all_company_data = data2["jsonData"].get("company_summary", "")
        if all_company_data:
            name_ = all_company_data.get("CR_LNM", "") if all_company_data.get("CR_LNM", "") else ""
            alias = all_company_data.get("CR_ANM", "") if all_company_data.get("CR_ANM", "") else ""
            group_name = all_company_data.get("CR_GRP_LNM", "") if all_company_data.get("CR_GRP_LNM", "") else ""
            group_name_in_arabic = all_company_data.get("CR_GRP_ANM", "") if all_company_data.get("CR_GRP_ANM", "") else ""
            registration_number = all_company_data.get("CR_NO", "") + "-" + all_company_data.get("BRANCH_NO", "") if all_company_data.get("CR_NO", "") and all_company_data.get("BRANCH_NO", "") else ""
            type_ = all_company_data.get("CM_TYP_DESC", "") if all_company_data.get("CM_TYP_DESC", "") else ""
            registration_date = format_date(all_company_data.get("REG_DATE", "")) if all_company_data.get("REG_DATE", "") else ""
            expiry_date = format_date(all_company_data.get("EXPIRE_DATE", "")) if all_company_data.get("EXPIRE_DATE", "") else ""
            status_ = all_company_data.get("STATUS", "") if all_company_data.get("STATUS", "") else ""
            financial_year_end = all_company_data.get("FN_YEAR_END", "") if all_company_data.get("FN_YEAR_END", "") else ""
            nationality = all_company_data.get("CR_NAT", "") if all_company_data.get("CR_NAT", "") else ""
            period_ = all_company_data.get("PRD", "").replace("N/A", "") if all_company_data.get("PRD", "") else ""

            
        business_activities = data2["jsonData"].get("businessActivities", "")
        if business_activities:
            all_activity_data = []
            for activity in business_activities:
                code = activity.get("ISIC4_CD", "")
                activities = activity.get("ISIC4_NM", "")
                ac_status = "Not Restricted"
                ac_description = activity.get("ISIC4_DETL", "")
                activity_dict  = {
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
            response3 = requests.request("POST", url3, headers=headers3, json=payload3)
            if not response3:
                print("No Response for Previous Activity")
                time.sleep(10)
                continue
            if response3.status_code == 200:
                data3 = response3.json()
                break
            else:
                print(f"Previous Activity error code: {response3.status_code}")
                time.sleep(5)

        previous_activity_data = data3["jsonData"]
        if previous_activity_data:
            all_previous_activity_data = []
            for previous_data in previous_activity_data:
                local_code = previous_data.get("Local_Code", "") if previous_data.get("Local_Code", "") else ""
                international_code = previous_data.get("International_Code", "") if previous_data.get("International_Code", "") else ""
                activity_name = previous_data.get("Old_Activity_NM", "") if previous_data.get("Old_Activity_NM", "") else ""
                activity_code = previous_data.get("ISIC4Code", "") if previous_data.get("ISIC4Code", "") else ""
                description_of_activity = previous_data.get("Business_Description", "") if previous_data.get("Business_Description", "") else ""
                sufficient_funds = previous_data.get("Sufficient_Fund", "") if previous_data.get("Sufficient_Fund", "") else ""
                previous_activity_dict = {
                            "local_code": local_code,
                            "international_code": international_code,
                            "name": activity_name,
                            "code": activity_code,
                            "description": description_of_activity.replace("\r\n", "").replace("\r\n-", "").replace("\"", ""),
                            "sufficient_fund": sufficient_funds
                            }
                all_previous_activity_data.append(previous_activity_dict)

        commercial_data = data2["jsonData"].get("commercialAddress", "")
        if commercial_data:
            company_address = (commercial_data.get("CR_FLAT", "") if commercial_data.get("CR_FLAT", "") else "") + ", " + (commercial_data.get("CR_BULD", "") if commercial_data.get("CR_BULD", "") else "") + ", " + (commercial_data.get("CR_ROAD", "") if commercial_data.get("CR_ROAD", "") else "") + ", " + (commercial_data.get("CR_ROAD_NM", "") if commercial_data.get("CR_ROAD_NM", "") else "") + ", " + (commercial_data.get("CR_BLOCK", "") if commercial_data.get("CR_BLOCK", "") else "") + ", " + (commercial_data.get("CR_TOWN_NM", "") if commercial_data.get("CR_TOWN_NM", "") else "")
            postal_address = company_address + " " + (commercial_data.get("CR_PBOX", "") if commercial_data.get("CR_PBOX", "") else "").strip()

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

            website = commercial_data.get("CR_URL", "") if commercial_data.get("CR_URL", "") else ""
            e_store = commercial_data.get("ESTORE_URL", "") if commercial_data.get("ESTORE_URL", "") else ""

        partners_data = data2["jsonData"].get("company_Partners", "")
        if partners_data:
            for partner in partners_data:
                partner_id = partner.get("ID_NO", "") if partner.get("ID_NO", "") else ""
                partner_name  = partner.get("LNM", "") if partner.get("LNM", "") else ""
                partner_arabic_name = partner.get("ANM", "") if partner.get("ANM", "") else ""
                partner_nationality = partner.get("NAT_LNM", "") if partner.get("NAT_LNM", "") else ""
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

        authorized_persons_data = data2["jsonData"].get("authorizedSignatories", "")
        if authorized_persons_data:
            for auth_person in authorized_persons_data:
                auth_name = auth_person.get("NAME", "") if auth_person.get("NAME", "") else ""
                auth_nationality = auth_person.get("NAT_NM", "") if auth_person.get("NAT_NM", "") else ""
                auth_arabic_name = auth_person.get("ANM", "") if auth_person.get("ANM", "") else ""
                auth_auth_level = auth_person.get("SIG_LEV", "") if auth_person.get("SIG_LEV", "") else ""
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

        # amendments_data = data2["amendhistory"]
        # for amendment in amendments_data:
        #     amend_data = amendment["CRT_DATE"]
        #     amend_title = amendment["AMEND_LNM"]
        #     amend_url = amendment["URL"]

        partner_shareholder_data = data2["jsonData"].get("shareholdersAndPartners", "")
        if partner_shareholder_data:
            for psh_data in partner_shareholder_data:
                psh_name = psh_data.get("NAME", "") if psh_data.get("NAME", "") else ""
                psh_nationality = psh_data.get("NAT_NAME", "") if psh_data.get("NAT_NAME", "") else ""
                psh_arabic_name = psh_data.get("ANM", "") if psh_data.get("ANM", "") else ""
                psh_no_of_shares = psh_data.get("NUM_SHARE", "") if psh_data.get("NUM_SHARE", "") else ""
                psh_ownership_percentage = psh_data.get("RATIO_ONER", "") if psh_data.get("RATIO_ONER", "") else ""
                psh_mortgagor_status = psh_data.get("MORTGAGE", "") if psh_data.get("MORTGAGE", "") else ""
                psh_sequested_status = psh_data.get("SEQUESTER", "") if psh_data.get("SEQUESTER", "") else ""
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

        capital_details = data2["jsonData"].get("companyCapitalDetails", "")
        all_capital_data = []
        if capital_details:
            auth_capital = capital_details.get("AUTH_CAPTL", "") if capital_details.get("AUTH_CAPTL", "") else ""
            issued_capital = capital_details.get("ISU_CAPTL", "") if capital_details.get("ISU_CAPTL", "") else ""
            total_shares = capital_details.get("TOT_SHARE", "") if capital_details.get("TOT_SHARE", "") else ""
            share_nominal_value = capital_details.get("NOM_VAL", "") if capital_details.get("NOM_VAL", "") else ""
            local_investment = capital_details.get("LOCAL_INVEST_SUM", "") if capital_details.get("LOCAL_INVEST_SUM", "") else ""
            gcc_investment = capital_details.get("GCC_INVEST_SUM", "") if capital_details.get("GCC_INVEST_SUM", "") else ""
            foriegn_investment = capital_details.get("FOR_INVEST_SUM", "") if capital_details.get("FOR_INVEST_SUM", "") else ""
            capital_currency = capital_details.get("CURR_CD", "") if capital_details.get("CURR_CD", "") else ""
            cash_capital = capital_details.get("PAID_CASH", "") if capital_details.get("PAID_CASH", "") else ""
            kind_capital = capital_details.get("PAID_INKIND", "") if capital_details.get("PAID_INKIND", "") else ""
            
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
            all_branches_data = []
            for branches in all_branches:
                br_reg_no = (branches.get("CR_NO", "") if branches.get("CR_NO", "") else "") + "-" + (branches.get("BRANCH_NO", "") if branches.get("BRANCH_NO", "") else "")
                br_name = branches.get("CR_NAME", "") if branches.get("CR_NAME", "") else ""
                br_reg_date = format_date(branches.get("REG_DATE", "")) if branches.get("REG_DATE", "") else ""
                br_expiry_date = format_date(branches.get("EXPIRE_DATE", "")) if branches.get("EXPIRE_DATE", "") else ""
                br_status = branches.get("STATUS", "") if branches.get("STATUS", "") else ""
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
                owner_name = owner.get("LNM", "") if owner.get("LNM", "") else ""
                owner_arabic_name = owner.get("ANM", "") if owner.get("ANM", "") else ""
                owner_nationality = owner.get("NAT_LNM", "") if owner.get("NAT_LNM", "") else ""
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
                officer_name = officer.get("CO_LNM", "") if officer.get("CO_LNM", "") else ""
                officer_arabic_name = officer.get("CO_ANM", "") if officer.get("CO_ANM", "") else ""
                officer_nationality = officer.get("CO_NAT_NM", "") if officer.get("CO_NAT_NM", "") else ""
                officer_designation = officer.get("CO_POSITION", "") if officer.get("CO_POSITION", "") else ""
                officer_termination_date = format_date(officer.get("CO_EXPIRE_DATE", "")) if officer.get("CO_EXPIRE_DATE", "") else ""
                officer_status = officer.get("CO_STATUS_NM", "") if officer.get("CO_STATUS_NM", "") else ""
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
                },
                {
                    "type": "agency_detail",
                    "data": [
                        {
                            "agency_number": agency_number,
                            "agency_status": agency_status,
                            "registration_date": agency_registration_date,
                            "expiry_date": agency_expiry_date,
                            "registration_number": agent_registration_number,
                            "status": agent_status,
                            "alias": agent_com_name_ar,
                            "name": agent_com_name_en
                        }
                    ]
                },
                {
                    "type": "agency_products_or_services_information",
                    "data": all_prod_details
                },
                {
                    "type": "agency_amendment_history",
                    "data": all_amendment_details
                }
            ],
            "addresses_detail": addresses_detail,
            "contacts_detail": [
                {
                    "type": "website",
                    "value": website
                },
                {
                    "type": "agency_mobile_number",
                    "value": agent_mobile_number
                },
                {
                    "type": "agency_email",
                    "value": agent_email_address
                },
                {
                    "type": "agency_phone_number",
                    "value": agent_phone_no
                },
                {
                    "type": "agency_fax_number",
                    "value": agent_fax_number
                }
            ],
            "people_detail": people_detail
        }

        OBJ = bahrain_crawler.prepare_data_object(OBJ)
        ENTITY_ID = bahrain_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
        BIRTH_INCORPORATION_DATE = ''
        ROW = bahrain_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
        bahrain_crawler.insert_record(ROW)
    
    else:
        pass

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