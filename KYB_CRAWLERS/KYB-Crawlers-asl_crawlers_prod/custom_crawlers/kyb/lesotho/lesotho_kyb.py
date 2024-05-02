"""Import required library"""
from atexit import register
from operator import le
import time, re
import traceback,sys
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil import parser
from selenium.common.exceptions import WebDriverException
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import Select
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.crawlers_helper_func import CrawlersFunctions
crawlers_functions = CrawlersFunctions()
from helpers.load_env import ENV

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Ministry of Trade and Industry in Lesotho',
    'COUNTRY' : 'Lesotho',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.companies.org.ls/", 
                        "Source Description": "The Ministry of Trade and Industry in Lesotho is responsible for promoting and regulating trade, industry, and investment activities in the country. They oversee various aspects related to business registration and provide support for entrepreneurs and businesses operating in Lesotho."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.companies.org.ls/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Lesotho",
}

lesotho_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = lesotho_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

def skip_pages():
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if start_number != 0:
        for i in range(start_number-1):
            try:
                time.sleep(3)
                print("Skipping page number: ", i+1)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    page_count = start_number
    time.sleep(5)
    return page_count

def process_contact_detail(data):
    def is_empty(value):
        return value is None or any(keyword in value for keyword in ['[No Country Code] [No Area Code] [No Number]', '[No Area Code] [No Number]', '[Not Supplied]'])
        
    def replace_area_code(value):
        return value.replace('[No Area Code]', '').strip()
    
    contact_detail = [
        {"type": "phone_number", "value": replace_area_code(data.get('Telephone'))} if not is_empty(data.get('Telephone')) else {},
        {"type": "phone_number_2", "value": replace_area_code(data.get('Mobile'))} if not is_empty(data.get('Mobile')) else {},
        {"type": "fax_number", "value": replace_area_code(data.get('Fax'))} if not is_empty(data.get('Fax')) else {},
        {"type": ":e_mail", "value": data.get('Email')} if not is_empty(data.get('Email')) else {},
        {"type": ":website", "value": data.get('Website')} if not is_empty(data.get('Website')) else {},
        {"type": "main_phone_number", "value": replace_area_code(data.get('Telephone_2'))} if not is_empty(data.get('Telephone_2')) else {},
        {"type": "main_phone_number_2", "value": replace_area_code(data.get('Mobile_2'))} if not is_empty(data.get('Mobile_2')) else {},
        {"type": "main_fax_number", "value": replace_area_code(data.get('Fax_2'))} if not is_empty(data.get('Fax_2')) else {},
        {"type": ":main_mail", "value": data.get('Email_2')} if not is_empty(data.get('Email_2')) else {},
        {"type": ":main_website", "value": data.get('Website_2')} if not is_empty(data.get('Website_2')) else {}
    ]

    return [item for item in contact_detail if item]  # Remove empty dictionaries from the list

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

def get_share_allocations(data):
    data_array = []
    current_entry = {}

    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Number of shares':
                if current_entry:
                    data_array.append(current_entry)
                current_entry= {'meta_detail': {'number_of_shares': value}, "designation": "shareholder"}
            elif label_name == 'Name':
                current_entry['name'] = value
    
    if current_entry:
        data_array.append(current_entry)
        
    return data_array


def get_members(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Also a director': 'also_a_director',
        'Name': 'name',
        'Residential or Registered Office Address': 'address',
        'Postal Address': 'postal_address',
        "Member's Contribution": 'member_contribution',
        'Appointed': 'appointment_date'
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    current_entry["designation"] = "member"
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    current_entry["designation"] = "member"
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Also a director':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["also_a_director"] = value
            elif label_name == 'Name':
                current_entry['name'] = value
            elif label_name == 'Residential Address' or label_name == 'Residential or Registered Office Address':
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == "Member's Contribution":
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["member_contribution"] = value
            elif label_name == 'Appointed':
                current_entry['appointment_date'] = format_date(value)
    if current_entry:
        current_entry["designation"] = "member"
        data_array.append(current_entry)
    return data_array

def get_shareholders(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Shareholder is also a director': 'also_a_director',
        'Name': 'name',
        'Residential Address': 'address',
        'Appointed': 'appointment_date',
        'Also a director': 'also_a_director',
        'Residential or Registered Office Address': 'address',
        'Postal Address': 'postal_address',
        'Ceased': 'ceased'
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
                        current_entry["designation"] = "former_shareholder"
                    else:
                        current_entry["designation"] = "shareholder"
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
                        current_entry["designation"] = "former_shareholder"
                    else:
                        current_entry["designation"] = "shareholder"
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Shareholder is also a director' or label_name == 'Also a director':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["also_a_director"] = value
            elif label_name == 'Ceased':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["ceased"] = value
            elif label_name == 'Name':
                current_entry['name'] = value
            elif label_name == 'Residential Address' or label_name == 'Residential or Registered Office Address':
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Appointed':
                current_entry['appointment_date'] = format_date(value)
    if current_entry:
        if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
            current_entry["designation"] = "former_shareholder"
        else:
            current_entry["designation"] = "shareholder"
        data_array.append(current_entry)
    return data_array



def get_officers(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Name': 'name',
        'Position': 'designation',
        'Required to accept service?': 'required_to_accept_service?',
        'Physical Address': 'address',
        'Postal Address': 'postal_address',
        'Nationality': 'nationality',
        'Date of Appointment': 'appointment_date',
        'Date of Termination': 'termination_date'
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    if 'termination_date' in current_entry:
                        current_entry["designation"] = "former_officer"
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    if 'termination_date' in current_entry:
                        current_entry["designation"] = "former_officer"
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Name':
                current_entry['name'] = value
            elif label_name == 'Position':
                current_entry['designation'] = value
            elif label_name == 'Required to accept service?':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['required_to_accept_service'] = value
            elif label_name == 'Physical Address':
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Nationality':
                current_entry['nationality'] = value
            elif label_name == 'Date of Appointment':
                current_entry['appointment_date'] = format_date(value)
            elif label_name == 'Date of Termination':
                current_entry['termination_date'] = format_date(value)

    if current_entry:
        if 'termination_date' in current_entry:
            current_entry["designation"] = "former_officer"
        data_array.append(current_entry)
    return data_array


def get_page_tab_data(driver):
    label_values_array = {}
    label_counts = {}
    label_elements = driver.find_elements(By.CLASS_NAME, 'appAttrLabelBox')
    for label_element in label_elements:
        if len(label_element.find_elements(By.XPATH, "following-sibling::div")) > 0:
            next_sibling = label_element.find_element(By.XPATH, "following-sibling::div")
            value = next_sibling.text
        else:
            next_sibling = label_element.find_element(By.XPATH, "following-sibling::ul")
            if len(next_sibling.find_elements(By.TAG_NAME, "a")) > 0:
                anchor_tag = next_sibling.find_element(By.TAG_NAME, "a")
                href_val = anchor_tag.get_attribute('href')
                value = f"{next_sibling.text} {href_val}"
            else:
                value = next_sibling.text
        label = label_element.text
        if label in label_values_array:
            label_counts[label] = label_counts.get(label, 1) + 1
            new_label = f"{label}_{label_counts[label]}"
            label_values_array[new_label] = value
        else:
            label_values_array[label] = value
            label_counts[label] = 1
    return label_values_array

def get_page_data(driver):
    tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
    ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
    scripts_tob_executed = []
    tab_names = []
    additional_detail = []
    addresses_detail = []
    contact_detail = []
    people_detail = []
    item = {}

    for ul_element in ul_elements:
        tab_names.append(ul_element.text)
        a_tag = ul_element.find_element(By.TAG_NAME, 'a')
        to_be_executed = a_tag.get_attribute("onclick")
        to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
        scripts_tob_executed.append(to_be_executed)
    for idx, script in enumerate(scripts_tob_executed):
        data = {}
        time.sleep(3)
        driver.execute_script(script)
        time.sleep(3)
        if tab_names[idx] == "General Details": 
            try:
                expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
                expand_button[1].click()
                time.sleep(1)
            except Exception as e:
                pass
            data = get_page_tab_data(driver)
            item['name'] = data.get('Company Name').replace('"', '').replace("%", "%%") if data.get('Company Name') is not None else ""
            item['status'] = data.get('Company Status')
            item['incorporation_date'] = format_date(data.get('Incorporation Date'))
            item['type'] = data.get('Company Type')
            item['aliases'] = data.get('Trade Name').replace('"', '').replace("%", "%%") if data.get('Trade Name') is not None else ""
            item['single_or_multiple_shareholders'] = data.get('Single or Multiple Shareholders')
            item['does_the_company_adopt_its_own_articles'] = data.get('Does the company adopt its own articles?')
            item['share_capital'] = data.get('Share Capital')
            item['annual_takeover'] = data.get('Annual Turnover')
            item['number_of_employees'] = data.get('Employees?')
            item['annual_filing_day'] = data.get('Annual Filing Day')
            item['annual_filing_month'] = data.get('Annual Filing Month')
            bussiness_activity_element = driver.find_elements(By.CLASS_NAME, 'appSelect2Option')
            if data.get('Previous Status') != "" and data.get('Previous Status') is not None:
                additional_detail.append({
                    "type": "previous_status_history",
                    "data": [{
                        'previous_status': data.get('Previous Status'),
                        'start_date': format_date(data.get('Start Date')),
                        'end_date': format_date(data.get('End Date'))
                    }]
                })
            industry_detail = []
            for activity_text in bussiness_activity_element:
                text = activity_text.text
                industry_detail.append({
                        "code": text[:4],
                        "description": text[4:].strip()
                })
            if len(industry_detail) > 0:
                additional_detail.append({
                        "type": "industry_detail",
                        "data": industry_detail
                })
        elif tab_names[idx] == "Addresses":
            data = get_page_tab_data(driver)
            if data.get('Physical Address') is not None and data.get('Physical Address') != "":
                meta_detail = {"start_date": format_date(data.get('Start Date'))} if data.get('Start Date') is not None and data.get('Start Date') != "" else {}
                addresses_detail.append({
                    "type": "physical_address",
                    "address": data.get('Physical Address'),
                    "meta_detail": meta_detail
                })
            if data.get('Postal Address') is not None and data.get('Postal Address') != "":
                meta_detail = {"start_date": data.get('Start Date_2')} if data.get('Start Date_2') is not None and data.get('Start Date') != "" else {}
                addresses_detail.append({
                    "type": "postal_address",
                    "address": data.get('Postal Address'),
                    "meta_detail": meta_detail
                })
            contact_detail.extend(process_contact_detail(data))
            item['is_the_address_where_company_registers_are_kept_the_same_as_the_registered_office_address?'] = data.get('Is the Address where company registers are kept the same as the Registered Office Address?')
            if data.get('At the registered office') is not None and data.get('At the registered office').strip() != "":
                additional_detail.append({
                    "type": "document_submission_address",
                    "data": [{
                        "at_the_registered_office": data.get('At the registered office'),
                        "at_the_main_business_address": data.get('At the main business address'),
                        "on_a_director_or_officer_accepting_service": data.get('On a director or officer accepting service')
                    }]
                })
        elif tab_names[idx] == "Officers":
            expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
            if len(expand_button) > 0:
                expand_button[1].click()
            data = get_page_tab_data(driver)
            people_detail.extend(get_officers(data))
        elif tab_names[idx] == "Shares & Shareholders":
            expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
            if len(expand_button) > 0:
                expand_button[1].click()
            data = get_page_tab_data(driver)
            if data.get("Total Shares") is not None and data.get("Total Shares").strip() != "":
                additional_detail.append({
                    "type": "shares_information",
                    "data": [{
                        "total_shares": data.get("Total Shares"),
                        "do_you_have_extensive_shareholding": data.get("Do you have extensive shareholding?"),
                        "ordinary_shareholder_signatures": data.get("Ordinary Shareholder signatures (Form 1A)") if data.get("Ordinary Shareholder signatures (Form 1A)") is not None else "",
                        "more_than_one_class_of_shared": data.get("More than one class of share")
                    }]
                })
            filtered_data = {k: v for k, v in data.items() if k.strip()}
            people_detail.extend(get_shareholders(filtered_data))
        elif tab_names[idx] == "Share Allocations":
            data = get_page_tab_data(driver)
            filtered_data = {k: v for k, v in data.items() if k.strip()}
            people_detail.extend(get_share_allocations(filtered_data))
        elif tab_names[idx] == "Documents":
            data = get_page_tab_data(driver)
            if "Application to register a non-profit organisation" in data and "https" in data.get("Application to register a non-profit organisation"):
                parts = data.get('Application to register a non-profit organisation').split('https')
                additional_detail.append({
                    "type": "document_details",
                    "data": [{
                        "document_title": parts[0].strip() if len(parts) > 1 else "",
                        "document_url": 'https' + parts[1].strip() if len(parts) > 1 else ""
                    }]
                })
        elif tab_names[idx] == "Members":
            data = get_page_tab_data(driver)
            people_detail.extend(get_members(data))

        item['contact_detail'] = contact_detail
        item['addresses_detail'] = addresses_detail
        item['additional_detail'] = additional_detail
        item['people_detail'] = people_detail
    return item


def main_function(interval_start, interval_end, skip_flag):
    """
    Description: Main Function for inserting data in DB and papare data object.
    @param:
    - interval_start: (int)
    - interval_end: (int)
    - skip_flag: (bool)
    @return:
    - DATA SIZE
    """
    url = "https://www.companies.org.ls/"
    driver.get(url)
    DATA_SIZE = len(driver.page_source)
    driver.set_page_load_timeout(120)
    wait = WebDriverWait(driver, 30)
    search_company_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Company Search")))
    search_company_btn.click()
    
    input_box = driver.find_element(By.ID, "QueryString")
    input_box.clear()
    input_box.send_keys("LTD")
    advance_button = driver.find_element(By.CLASS_NAME, "appRestrictedExpand")
    if len(driver.find_elements(By.CLASS_NAME, "appRestrictedExpandCollapsed")) > 0:
        a_tag = driver.find_element(By.CLASS_NAME, "appRestrictedExpandCollapsed")
        a_tag.click()
    select_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'appSearchOpsSelect')))
    select_element = select_div.find_element(By.TAG_NAME, 'select')
    select = Select(select_element)
    select.select_by_value('Between')
    start_date = driver.find_element(By.ID, "RegistrationDate")
    start_date.clear()
    start_date.send_keys(interval_start)
    end_date = driver.find_element(By.ID, "RegistrationDate2")
    end_date.clear()
    end_date.send_keys(interval_end)
    search_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Search")))
    search_button.click()
    if skip_flag:
        page_count = skip_pages()
    else:
        page_count = 0

    while True:
        print("Page Number: ", page_count)
        print("Date:", interval_start)
        page_count += 1
        # Wait until the elements with the specified class name are present
        company_links = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu"))
        )
        for i, element in enumerate(company_links):
            company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
            if i > len(company_tags): break
            try: 
                company_tags[i].click()
            except:
                time.sleep(4)
                company_tags[i].click()
            if len(driver.find_elements(By.CLASS_NAME, 'appTabs')) == 0:
                driver.back()
                continue
            data = get_page_data(driver)
            NAME = data.get("name")
            try:
                xpath_expression = f"//*[contains(text(), '{NAME}')]"
                element = driver.find_element(By.XPATH, xpath_expression)
                pattern = r'\((.*?)\)'
                matches = re.findall(pattern, element.text)
                registration_number = matches[len(matches) - 1] if len(matches) > 0 else ""
            except:
                registration_number = ""
            DATA = {
                "name": NAME,
                "status": data.get("status"),
                "registration_number": registration_number,
                "incorporation_date": data.get("incorporation_date"),
                "type": data.get("type"),
                "aliases": data.get("aliases"),
                "single_or_multiple_shareholders": data.get("single_or_multiple_shareholders"),
                "does_the_company_adopt_its_own_articles": data.get("does_the_company_adopt_its_own_articles?"),
                "share_capital": data.get("share_capital"),
                "annual_takeover": data.get("annual_takeover"),
                "number_of_employees": data.get("number_of_employees"),
                "annual_filing_day": data.get("annual_filing_day"),
                "annual_filing_month": data.get("annual_filing_month"),
                "additional_detail": data.get("additional_detail"), 
                "addresses_detail": data.get("addresses_detail"),
                "contacts_detail": data.get("contact_detail"),
                "people_detail": data.get("people_detail")
            }

            ENTITY_ID = lesotho_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = lesotho_crawler.prepare_data_object(DATA)
            ROW = lesotho_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            query = """INSERT INTO reports_testing (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports_testing.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports_testing.image THEN reports_testing.image || '{6}'::jsonb ELSE reports_testing.image END,data='{7}',updated_at='{10}'""".format(*ROW)
            crawlers_functions.db_connection(query)
            lesotho_crawler.insert_record(ROW)
            driver.back()

        try:
            time.sleep(2)
            driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
            time.sleep(5)
        except:
            break
    return DATA_SIZE

intervals = [
    ("01-Jan-1996", "31-Dec-1996"),
    ("01-Jan-1997", "31-Dec-1997"),
    ("01-Jan-1998", "31-Dec-1998"),
    ("01-Jan-1999", "31-Dec-1999"),
    ("01-Jan-2000", "31-Dec-2000"),
    ("01-Jan-2001", "31-Dec-2001"),
    ("01-Jan-2002", "31-Dec-2002"),
    ("01-Jan-2003", "31-Dec-2003"),
    ("01-Jan-2004", "31-Dec-2004"),
    ("01-Jan-2005", "31-Dec-2005"),
    ("01-Jan-2006", "31-Dec-2006"),
    ("01-Jan-2007", "31-Dec-2007"),
    ("01-Jan-2008", "31-Dec-2008"),
    ("01-Jan-2009", "31-Dec-2009"),
    ("01-Jan-2010", "31-Dec-2010"),
    ("01-Jan-2011", "31-Dec-2011"),
    ("01-Jan-2012", "31-Dec-2012"),
    ("01-Jan-2013", "31-Dec-2013"),
    ("01-Jan-2014", "31-Dec-2014"),
    ("01-Jan-2015", "31-Dec-2015"),
    ("01-Jan-2016", "31-Dec-2016"),
    ("01-Jan-2017", "31-Dec-2017"),
    ("01-Jan-2018", "31-Dec-2018"),
    ("01-Jan-2019", "31-Dec-2019"),
    ("01-Jan-2020", "31-Dec-2020"),
    ("01-Jan-2021", "31-Dec-2021"),
    ("01-Jan-2022", "31-Dec-2022"),
    ("01-Jan-2023", "31-Dec-2023")
]
interval_start_date = sys.argv[2] if len(sys.argv) > 2 else "01-Jan-1996"

# Find the index of the starting date in the intervals list
start_index = next((i for i, (start, end) in enumerate(intervals) if start == interval_start_date), -1)

if start_index == -1:
    raise ValueError(f"Start date {interval_start_date} not found in intervals.")

flag = True
skip_flag = True

try:
    for i in range(start_index, len(intervals)):
        try:
            interval_start, interval_end = intervals[i]
            time.sleep(3)
            DATA_SIZE = main_function(interval_start, interval_end, skip_flag)
            skip_flag = False
        except Exception as e:
            print(e)
            pass
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}

    lesotho_crawler.db_log(log_data)
    lesotho_crawler.end_crawler()      
except Exception as e:
    tb = traceback()
    print(e, tb)
    log_data = {"status": 'fail',
            "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    lesotho_crawler.db_log(log_data)
