"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.support.ui import WebDriverWait

meta_data = {
    'SOURCE': 'Louisiana Secretary of State, Commercial Division',
    'COUNTRY': 'Louisiana',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx",
                      "Source Description": "The secretary of state of Louisiana is one of the elected constitutional officers of the U.S. state of Louisiana and serves as the head of the Louisiana Department of State. The position was created by Article 4, Section 7 of the Louisiana Constitution. The current secretary of state is Kyle Ardoin. "},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Louisiana  Official Registry",
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

Louisiana_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)

arguments = sys.argv
if len(arguments) >= 2:
    start_input = arguments[1]
else:
    start_input = 'X0'  #

start_number = int(''.join(filter(str.isdigit, start_input)))
start_char = ''.join(filter(str.isalpha, start_input))
letters = ['X', 'N', 'K', 'F', 'Q', 'D', 'J', 'W']
if start_char not in letters:
    print("Invalid starting character. Please choose one of the valid letters.")
else:
    start_combination_found = False


def find_element_by_id(soup, element_id):
    element = soup.find('span', id=element_id)
    return element.text if element else ''


def wait_for_captcha_to_be_solved(browser):
    time.sleep(5)
    if len(browser.find_elements(By.XPATH, '//iframe[@title="reCAPTCHA"]')) > 0:
        while True:
            try:
                iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                browser.switch_to.frame(iframe_element)
                wait = WebDriverWait(browser, 30)
                print('trying to resolve captcha')
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'recaptcha-checkbox-checked')))
                print("Captcha has been Solved")
                # Switch back to the default content
                browser.switch_to.default_content()
                return browser
            except:
                print('captcha solution timeout error, retrying...') 
                        
Louisiana_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = Louisiana_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=True)
driver.get("https://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx")

for letter in letters:
    if not start_combination_found and letter == start_char:
        start_combination_found = True 
    if not start_combination_found:
        continue  
    for num in range(start_number, 99999999):
        result = f"{num:08}{letter}" 

        radio_button = driver.find_element(By.XPATH, '//input[@id="ctl00_cphContent_radSearchByNumber"]')
        radio_button.click()
        print("number_enter",result)
        data_enter = driver.find_element(By.XPATH, '//input[@id="ctl00_cphContent_txtCharterNumber"]')
        data_enter.clear()
        data_enter.send_keys(result)

        wait_for_captcha_to_be_solved(driver)

        search_button = driver.find_element(By.XPATH, '//input[@value="Search"]')
        search_button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Helper function to handle empty values
        def handle_empty(value):
            return value if value else ''

        # Extract basic business information
        business_name = find_element_by_id(soup, 'ctl00_cphContent_lblName') or find_element_by_id(soup, 'ctl00_cphContent_lblServiceName')
        business_type = find_element_by_id(soup, 'ctl00_cphContent_lblType') or find_element_by_id(soup, 'ctl00_cphContent_lblTypesRegistered')
        business_status = find_element_by_id(soup, 'ctl00_cphContent_lblCurrentStatus') or find_element_by_id(soup, 'ctl00_cphContent_lblStatus')
        business_city_value = find_element_by_id(soup, 'ctl00_cphContent_lblCity')
        character = find_element_by_id(soup, 'ctl00_cphContent_lblCharterNumber') or find_element_by_id(soup, 'ctl00_cphContent_lblBookNumber') or find_element_by_id(soup, 'ctl00_cphContent_lblNumber')
        registration_date_value = find_element_by_id(soup, 'ctl00_cphContent_lblRegistrationDate')
        type_of_business=find_element_by_id(soup, "ctl00_cphContent_lblTypeOfBusiness")

        filing_type_element = find_element_by_id(soup, 'ctl00_cphContent_lblFilingType')
        company_name_element = find_element_by_id(soup, 'ctl00_cphContent_lblCompanyName')

        description=f"{filing_type_element}{company_name_element}"
        

        # Extract previous names
        previous_names_detail=[]
        span_element = soup.find('span', id="ctl00_cphContent_rptPreviousNames_ctl00_lblPreviousName")
        if span_element:
            text = span_element.get_text()
            name, date = text.split(' (Changed: ')
            date = date[:-1].replace("/","-")
            previous_names_detail = [{'name': name, 'date': date}]


        # Extract addresses
        addresses_detail = []
        domicile_table = soup.find('table', {'id': 'ctl00_cphContent_tblDomicile'})
        if domicile_table:
            address_span = domicile_table.find('span', {'id': 'ctl00_cphContent_lblAddress1'})
            csz_span = domicile_table.find('span', {'id': 'ctl00_cphContent_lblCSZ'})
            if address_span and csz_span:
                address_1 = handle_empty(address_span.text)
                csz_1 = handle_empty(csz_span.text)
                domicile_address = f"{address_1}{csz_1}"
                addresses_detail.append({"type": "domicile_address", "address": domicile_address})


        # Extract mailing info
        table = soup.find('table', {'id': 'ctl00_cphContent_tblMailing'})
        if table:
            mailing_address_span = table.find('span', {'id': 'ctl00_cphContent_lblMailingAddress1'})
            mailing_csz_span = table.find('span', {'id': 'ctl00_cphContent_lblMailingCSZ'})

            if mailing_address_span and mailing_csz_span:
                mailing_address = mailing_address_span.text
                mailing_csz = mailing_csz_span.text
                mail_add=f"{mailing_address}{mailing_csz}"

                addresses_detail.append({
                    "type": "postal_address",
                    "address":mail_add,
                })

        # Extract status info
        status_info = ''
        date_qualified = ''
        last_report_filed = ''
        status_type = ''
        additional_detail=[]
        status_table = soup.find('table', id='ctl00_cphContent_tblStatus')
        if status_table:
            rows = status_table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) == 2:
                    key = columns[0].text.strip().replace(":", "")
                    value = columns[1].text.strip()
                    if key == "Annual Report Status":
                        status_info = handle_empty(value)
                    elif key == "Qualified":
                        date_qualified = value.replace("/", "-")
                    elif key == "Last Report Filed":
                        last_report_filed = value.replace("/", "-")
                    elif key == "Type":
                        status_type = handle_empty(value)
        if status_info or date_qualified or last_report_filed or status_type:
            status_data = {"status_info": status_info, "date_qualified": date_qualified, "last_report_filed": last_report_filed, "status_type": status_type}
            additional_detail = [{"type": "status_info", "data": [status_data]}]

        # Extract classes info
        people_detail=[]
        class_name = find_element_by_id(soup, 'ctl00_cphContent_dgCurrentClasses_ctl02_lblClassName')
        start_date = find_element_by_id(soup, 'ctl00_cphContent_dgCurrentClasses_ctl02_lblStartDate')
        end_date = find_element_by_id(soup, 'ctl00_cphContent_dgCurrentClasses_ctl02_lblEndDate')
        class_data = {"class_name": handle_empty(class_name), "start_date": handle_empty(start_date), "end_date": handle_empty(end_date)}

        if any(class_data.values()):
            additional_detail.append({"type": "current_classes_info", "data": [class_data]})

        # Extract contact info
        contact_name = find_element_by_id(soup, 'ctl00_cphContent_lblContactName')
        contact_address = find_element_by_id(soup, 'ctl00_cphContent_lblAddress')
        contact_data = {'name': handle_empty(contact_name), 'address': handle_empty(contact_address)}
        people_detail = [contact_data]

        # Extract filing info
        fillings_detail = []
        filling_table = soup.find('table', id='ctl00_cphContent_grdAmendments')
        if filling_table:
            rows = filling_table.find_all('tr')[1:]
            for row in rows:
                row_index = rows.index(row) + 2
                amend_des = find_element_by_id(soup, f'ctl00_cphContent_grdAmendments_ctl{row_index:02d}_lblAmendmentGroup')
                amend_date = find_element_by_id(soup, f'ctl00_cphContent_grdAmendments_ctl{row_index:02d}_lblAmendmentDate')
                group_des = find_element_by_id(soup, f'ctl00_cphContent_dgAmendments_ctl{row_index:02d}_lblAmendmentGroup')
                group_type = find_element_by_id(soup, f'ctl00_cphContent_dgAmendments_ctl{row_index:02d}_lblAmendmentType')
                group_date = find_element_by_id(soup, f'ctl00_cphContent_dgAmendments_ctl{row_index:02d}_lblAmendmentDate')
                amendment_data = {"description": handle_empty(amend_des), "date": handle_empty(amend_date),
                                "meta_detail": {"group": handle_empty(group_des), "type": handle_empty(group_type), "group_date_value": handle_empty(group_date)}}
                fillings_detail.append(amendment_data)

        # Extract dates information
        exp_date = find_element_by_id(soup, 'ctl00_cphContent_lblExpirationDate')
        date_first = find_element_by_id(soup, 'ctl00_cphContent_lblDateFirstUsed')
        date_la = find_element_by_id(soup, 'ctl00_cphContent_lblDateFirstUsedInLa')
        dates_data = {"expiry_date": handle_empty(exp_date), "date_first_used": handle_empty(date_first), "date_first_used_in_LA": handle_empty(date_la)}
        if any(dates_data.values()):
            additional_detail.append({"type": "dates_information", "data": [dates_data]})

        # Extract applicant information
        applicant_name_value = ''
        applicant_description_value = ''

        applicant_element = find_element_by_id(soup, 'ctl00_cphContent_lblApplicant')
        if applicant_element:
            parts = applicant_element.split(', ', 1)
            if len(parts) == 2:
                applicant_name_value, applicant_description_value = map(str.strip, parts)
            else:
                applicant_name_value = applicant_element.strip()

        applicant_address1_value = find_element_by_id(soup, 'ctl00_cphContent_lblApplicantAddress1')
        applicant_address2_value = find_element_by_id(soup, 'ctl00_cphContent_lblApplicantCSZ')
        applicant_address = f"{applicant_address1_value}{applicant_address2_value}"

        if applicant_name_value or applicant_description_value or applicant_address:
            applicant_data = {"name": applicant_name_value, "description": applicant_description_value, "address": applicant_address}
            additional_detail.append({"type": "applicant_info", "data": [applicant_data]})

        # Extract addresses
        principal_office_address1 = find_element_by_id(soup, 'ctl00_cphContent_lblPrincipalOfficeAddress1')
        principal_office_address2 = find_element_by_id(soup, 'ctl00_cphContent_trPrincipalOfficeCSZ')
        registered_address1 = find_element_by_id(soup, 'ctl00_cphContent_lblRegisteredAddress1')
        registered_address2 = find_element_by_id(soup, 'ctl00_cphContent_trRegisteredCSZ')
        principal_business_address1 = find_element_by_id(soup, 'ctl00_cphContent_lblPrincipalLAAddress1')
        principal_business_address2 = find_element_by_id(soup, 'ctl00_cphContent_trPrincipalLACSZ')

        principal_off_address = f"{handle_empty(principal_office_address1)} {handle_empty(principal_office_address2)}"
        registered_off_address = f"{handle_empty(registered_address1)} {handle_empty(registered_address2)}"
        principle_business_off_address = f"{handle_empty(principal_business_address1)} {handle_empty(principal_business_address2)}"

        addresses_detail.append({"type": "principal_business_address", "address": principal_off_address})
        addresses_detail.append({"type": "registered_address", "address": registered_off_address})
        addresses_detail.append({"type": "principal_establishment_address", "address": principle_business_off_address})

        # Extract registered agent information
        agent_name_element = find_element_by_id(soup, "ctl00_cphContent_rptAgents_ctl00_lblAgentName")
        agent_address_element = find_element_by_id(soup, "ctl00_cphContent_rptAgents_ctl00_lblAgentAddress1")
        agent_address1_element = find_element_by_id(soup, "ctl00_cphContent_rptAgents_ctl00_lblAgentAddress2")
        agent_city_state_zip_element = find_element_by_id(soup, "ctl00_cphContent_rptAgents_ctl00_lblAgentCSZ")
        appointment_date_element = find_element_by_id(soup, "ctl00_cphContent_rptAgents_ctl00_lblAgentAppointmentDate")

        agent_name_value = handle_empty(agent_name_element)
        agent_address_value = handle_empty(agent_address_element)
        agent_address_1_value = handle_empty(agent_address1_element)
        agent_city_state_zip_value = handle_empty(agent_city_state_zip_element)
        appointment_date_value = handle_empty(appointment_date_element).replace("/", "-")

        if agent_name_value or agent_address_value or agent_address_1_value or agent_city_state_zip_value or appointment_date_value:
            registered_agent_data = {
                "designation": "registered_agent",
                'name': agent_name_value,
                "address": f"{agent_address_value} {agent_address_1_value} {agent_city_state_zip_value}",
                "appointment_date": appointment_date_value
            }
            people_detail.append(registered_agent_data)

        # Extract officer information
        officer_tables = soup.find_all('table', {'id': lambda x: x and x.startswith('ctl00_cphContent_rptOfficers')})
        for table in officer_tables:
            officer_name_element = find_element_by_id(table, lambda x: x and x.endswith('lblOfficerName'))
            officer_title_element = find_element_by_id(table, lambda x: x and x.endswith('lblOfficerTitle'))
            officer_address1_element = find_element_by_id(table, lambda x: x and x.endswith('lblOfficerAddress1'))
            officer_address2_element = find_element_by_id(table, lambda x: x and x.endswith('lblOfficerAddress2'))
            officer_cs_zip_element = find_element_by_id(table, lambda x: x and x.endswith('lblOfficerCSZ'))

            officer_name_value = handle_empty(officer_name_element)
            officer_title_value = handle_empty(officer_title_element)
            officer_address1_value = handle_empty(officer_address1_element)
            officer_address2_value = handle_empty(officer_address2_element)
            officer_cs_zip_value = handle_empty(officer_cs_zip_element)
            
            
            if officer_name_value or officer_title_value or officer_address1_value or officer_address2_value or officer_cs_zip_value:
                officer_data = {
                'name': officer_name_value,
                'designation': officer_title_value,
                'address': f"{officer_address1_value} {officer_address2_value} {officer_cs_zip_value}"
                }
                people_detail.append(officer_data)


        back_to_search=driver.find_element(By.XPATH,'//input[@name="ctl00$cphContent$btnNewSearch"]')
        back_to_search.click()

        OBJ = {
            'name': business_name, 
            'type': business_type, 
            'jurisdiction': business_city_value, 
            'status': business_status,
            'registration_number': character, 
            'industries':type_of_business,
            'description':description,
            'people_detail': people_detail,
            'additional_detail': additional_detail, 
            "addresses_detail": addresses_detail, 
            'fillings_detail': fillings_detail,
            'previous_names_detail': previous_names_detail
        }
        OBJ =  Louisiana_crawler.prepare_data_object(OBJ)
        ENTITY_ID = Louisiana_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = Louisiana_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        Louisiana_crawler.insert_record(ROW)


    log_data = {"status": 'success',
                        "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
        
    Louisiana_crawler.db_log(log_data)
    Louisiana_crawler.end_crawler()
# except Exception as e:
#     tb = traceback.format_exc()
#     print(e,tb)
#     log_data = {"status": 'fail',
#                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
#     Louisiana_crawler.db_log(log_data)