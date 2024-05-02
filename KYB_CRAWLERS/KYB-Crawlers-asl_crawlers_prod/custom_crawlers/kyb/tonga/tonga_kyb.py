"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from atexit import register
from operator import le
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil import parser
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'Business Registries Office',
    'COUNTRY' : 'Tonga',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.businessregistries.gov.to/tonga-master/relay.html?url=https%%3A%%2F%%2Fwww.businessregistries.gov.to%%2Ftonga-master%%2Fservice%%2Fcreate.html%%3FtargetAppCode%%3Dtonga-master%%26targetRegisterAppCode%%3Dtonga-companies%%26service%%3DregisterItemSearch&target=tonga-master", 
                        "Source Description": "The Business Registries Office of Tonga is the official government agency responsible for the registration and administration of businesses and companies in the Kingdom of Tonga. It serves as a central repository of information on registered entities and ensures compliance with relevant laws and regulations."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.businessregistries.gov.to/tonga-master/relay.html?url=https%%3A%%2F%%2Fwww.businessregistries.gov.to%%2Ftonga-master%%2Fservice%%2Fcreate.html%%3FtargetAppCode%%3Dtonga-master%%26targetRegisterAppCode%%3Dtonga-companies%%26service%%3DregisterItemSearch&target=tonga-master'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Tonga",
}

tonga_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = tonga_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

def skip_pages():
    """
    Skips a specified number of pages in a web application.

    This function takes the starting page number as a command-line argument (if provided)
    and skips the specified number of pages by clicking on the "Next" button in the application.
    It uses the Selenium WebDriver to interact with the web pages and handles WebDriverExceptions
    that may occur during the process.

    Parameters:
    - None

    Returns:
    - int: The page count after skipping the specified number of pages.
    """
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if start_number != 0:
        for i in range(start_number-1):
            try:
                time.sleep(2)
                print("Skipping page number: ", i+1)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    page_count = start_number
    time.sleep(5)
    return page_count

def format_date(timestamp):
    """
    Formats a timestamp string into a standard date format.

    This function uses the dateutil.parser library to parse the input timestamp string
    into a datetime object. It then formats the datetime object into a string with the
    format "%m-%d-%Y". If any exception occurs during parsing or formatting, an empty
    string is returned.

    Parameters:
    - timestamp (str): A timestamp string to be formatted.

    Returns:
    - str: Formatted date string in the format "%m-%d-%Y" or an empty string if an
      exception occurs during parsing or formatting.
    """
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

def get_sharebundles(data):
    """
    Extracts share information from a nested data structure.

    This function takes a list of dictionaries as input, where each dictionary represents
    an entry in the data. It searches for entries of type "share_information" and extracts
    relevant information such as the name and number of shares. The extracted information
    is then added to a list of dictionaries, forming a collection of share bundles.

    Parameters:
    - data (list): A list of dictionaries representing data entries.

    Returns:
    - list: A list of dictionaries, each containing share information.
    """
    data_array = []
    current_entry = {}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Number of shares':
                if current_entry:
                    data_array.append({'type': 'share_information', 'data': [current_entry]})
                current_entry = {'number_of_shares': value, 'name': value, "entity_number":value}
            elif label_name == 'Name' or label_name == "Entity Name":
                current_entry['name'] = value
            elif label_name == 'Entity Number':
                current_entry['entity_number'] = value

    if current_entry:
        data_array.append({'type': 'share_information', 'data': [current_entry]})

    return data_array

def get_filings(driver):
    """
    Retrieves filing information from a web page using a Selenium WebDriver.

    This function interacts with a web page using the provided Selenium WebDriver (`driver`)
    to extract filing records. It waits for 2 seconds to ensure the page is loaded, then
    searches for elements representing filing records. For each filing record, it extracts
    relevant details such as title, submission date, filing date, and file URL.

    Parameters:
    - driver: A Selenium WebDriver object.

    Returns:
    - list: A list of dictionaries, each containing filing information.
    """
    time.sleep(2)
    filing_records = driver.find_elements(By.CLASS_NAME, 'appRepeaterRowContent')
    data = []
    for record in filing_records:
        if len(record.find_elements(By.CLASS_NAME, 'appFilingSubmitted')) > 0:
            meta_detail = {"submission_date": format_date(record.find_element(By.CLASS_NAME, 'appFilingSubmitted').text)} if record.find_element(By.CLASS_NAME, 'appFilingSubmitted') is not None else {}
        else:
            meta_detail = {}
        if len(record.find_elements(By.CLASS_NAME, 'appFilingName')) == 0:
            continue
        data.append({
            "title": record.find_element(By.CLASS_NAME, 'appFilingName').text,
            "meta_detail": meta_detail,
            "date": format_date(record.find_element(By.CLASS_NAME, 'appFilingEnd').text),
            "file_url": record.find_element(By.CLASS_NAME, 'appFilingName').find_element(By.TAG_NAME, 'a').get_attribute('href')
        })
    return data

def show_more_info(driver):
    try:
        click_tabes = driver.find_elements(By.CLASS_NAME, 'appExpandoCollapsed')
        for click_tabe in click_tabes:
            click_tabe.click()
    except:
        pass

def get_directors(data):
    """
    Extracts director information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to director
    details such as name, address, consent, and appointment date. It then creates a list of
    dictionaries, each containing director information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing director details.

    Returns:
    - list: A list of dictionaries, each containing director information.
    """
    data_array = []
    current_entry = {}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name' or label_name == 'Entity Name':
                if current_entry:
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'director'}
            elif label_name == 'Residential Address' or label_name == "Residential or Registered Office Address":
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Director Consent':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['consent'] = value
            elif label_name == 'Date Ceased':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['ceased_date'] = format_date(value)
                current_entry['designation'] = 'former_director'
            elif label_name == 'Date of Appointment' or label_name == "Appointed":
                current_entry['appointment_date'] = format_date(value)

    if current_entry:
        data_array.append(current_entry)
    
    return data_array

def authorised_agents(data):
    """
    Extracts registered_agent information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to registered_agent
    details such as name, address, consent, and appointment date. It then creates a list of
    dictionaries, each containing registered_agent information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing registered_agent details.

    Returns:
    - list: A list of dictionaries, each containing registered_agent information.
    """
    data_array = []
    current_entry = {}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name' or label_name == 'Entity Name':
                if current_entry:
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'registered_agent'}
            elif label_name == 'Residential Address' or label_name == "Residential or Registered Office Address":
                current_entry['address'] = value

            elif label_name == 'Date of Appointment' or label_name == "Appointed":
                current_entry['appointment_date'] = format_date(value)

    if current_entry:
        data_array.append(current_entry)

    return data_array

def get_shareholders(data):
    """
    Extracts shareholder information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to shareholder
    details such as name, address, appointment date, and number of shares. It also identifies
    if the shareholder is also a director. The function then creates a list of dictionaries,
    each containing shareholder information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing shareholder details.
    """
    data_array = []
    current_entry = {}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Shareholder is also a director' or label_name == 'Shareholders':
                if current_entry:
                    data_array.append(current_entry)
                current_entry = {'designation': 'shareholder', 'meta_detail': {'also_a_director': value}}
            elif label_name == 'Name' or label_name == 'Entity Name':
                current_entry['name'] = value
            elif label_name == 'Residential Address' or label_name == "Residential or Registered Office Address":
                current_entry['address'] = value
            elif label_name == 'Appointed' or label_name == "Date of Appointment":
                current_entry['appointment_date'] = format_date(value)
            elif label_name == 'Number of shares':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['number_of_shares'] = value
            elif label_name == 'Entity Number':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['entity_number'] = value
            elif label_name == "Place of Incorporation":
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['incorporation_place'] = value

    if current_entry:
        data_array.append(current_entry)
   
    return data_array

def get_owners(data):
    """
    Extracts Owners information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to Owners
    details such as name, address, appointment date, and number of shares. It also identifies
    if the Owners is also a director. The function then creates a list of dictionaries,
    each containing Owners information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing Owners details.
    Returns:
    - data (list): 
    """
    data_array = []
    current_entry = {'meta_detail': {}}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name' or label_name == 'Entity Name':
                if current_entry and current_entry.get('name', ''):
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'owner', 'meta_detail': current_entry['meta_detail']}

            if label_name == 'Gender':
                current_entry['meta_detail']['Gender'] = value
            elif label_name == 'Owner Type':
                current_entry['meta_detail']['owner_type'] = value
            elif label_name == 'Beneficial Owners':
                current_entry['meta_detail']['beneficial_owner'] = value
            elif label_name == 'Nominee or Trustee Owners':
                current_entry['meta_detail']['also_a_trustee_owner'] = value
            elif label_name == 'Residential Address' or label_name == "Physical Address":
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Nationality':
                current_entry['nationality'] = value
            elif label_name == "Appointed":
                current_entry['appointment_date'] = value

    if current_entry and current_entry.get('name', ''):
        data_array.append(current_entry)

    return data_array

def get_page_tab_data(driver):
    """
    Retrieves label-value pairs from a web page using a Selenium WebDriver.

    This function interacts with a web page using the provided Selenium WebDriver (`driver`)
    to extract label and value elements. It then pairs each label with its corresponding value,
    considering potential duplications in labels by appending a count to the label name. The
    resulting data is returned as a dictionary.

    Parameters:
    - driver: A Selenium WebDriver object.

    Returns:
    - dict: A dictionary containing label-value pairs from the web page.
    """
    label_values_array = {}
    label_counts = {}
    label_elements = driver.find_elements(By.CLASS_NAME, 'appAttrLabelBox')
    value_elements = driver.find_elements(By.CLASS_NAME, 'appAttrValue')
    labels = [label_element.text for label_element in label_elements]
    values = [value_element.text for value_element in value_elements]
    for label, value in zip(labels, values):
        if label in label_values_array:
            label_counts[label] = label_counts.get(label, 1) + 1
            new_label = f"{label}_{label_counts[label]}"
            label_values_array[new_label] = value
        else:
            label_values_array[label] = value
            label_counts[label] = 1

    return label_values_array

def get_page_data(driver):
    """
    Retrieves comprehensive data from various tabs on a web page using a Selenium WebDriver.

    This function interacts with a web page using the provided Selenium WebDriver (`driver`)
    to extract data from specific tabs such as General Details, Addresses, Directors, Shares &
    Shareholders, Share Bundles, and Filings. It organizes the extracted information into a
    dictionary, including general details, addresses details, people details (directors and shareholders),
    filings details, and additional details.

    Parameters:
    - driver: A Selenium WebDriver object.

    Returns:
    - dict: A dictionary containing comprehensive data from different tabs on the web page.
    """
    tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
    ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
    scripts_tob_executed = []
    tab_names = []
    additional_detail = []
    addresses_detail = []
    people_detail = []
    fillings_detail = []
    previous_names_detail = []
    item = {}

    for ul_element in ul_elements:
        if ul_element.text in ['General Details', 'Addresses', 'Directors', 'Shares & Shareholders', 'Share Bundles', 'Filings', 'Owners', 'Authorised Agents']:
            tab_names.append(ul_element.text)
            a_tag = ul_element.find_element(By.TAG_NAME, 'a')
            to_be_executed = a_tag.get_attribute("onclick")
            if to_be_executed is None: continue
            to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
            scripts_tob_executed.append(to_be_executed)
    for idx, script in enumerate(scripts_tob_executed):
        data = {}
        driver.execute_script(script)
        time.sleep(3)
        if tab_names[idx] == "General Details": 
            show_more_info(driver)
            time.sleep(3)
            data = get_page_tab_data(driver)
            
            item['registration_number'] = data.get('').split('(')[1].split(')')[0] if '(' in data.get('') else ""
            item['name'] = data.get('').replace('"', '').replace("[Local]", "").replace(f"({item['registration_number']})", '').strip() if data.get('') is not None and item['registration_number'] is not None else ""
            item['registration_date'] = format_date(data.get('Effective Date'))
            item['re_registration_date'] = format_date(data.get('Re-Registration Date'))
            item['status'] = data.get('Entity Status', data.get('Business Name Status')) 
            item['licence_status'] = data.get('Business Licence Status')
            item['incorporation_date'] = format_date(data.get('Incorporation Date',data.get('Commencement Date','')))
            item['ar_filing_month'] = data.get('Annual Renewal Filing Month')
            item['have_own_rules'] = data.get('Do you have your own Constitution?')
            item['filing_month'] = data.get('Annual Return Filing Month',data.get('Annual Renewal Month'))
            item['country_of_incorporation'] = data.get('Country of Incorporation')
            item['last_filed_date'] = format_date(data.get('Annual Return Last Filed on',data.get('Annual Renewal Last Filed on')))
            item['tax_number'] = data.get('Tax Identification Number (TIN)', data.get('Taxpayer Identification Number (TIN)',data.get('Tax Identification Number (TIN)'))).strip() if  data.get('Tax Identification Number (TIN)', data.get('Taxpayer Identification Number (TIN)')) is not None else ""
            item['struck_off_date'] = data.get('De-Registration Date') if data.get('De-Registration Date') is not None else ""
            item['cancellation_date'] = format_date(data.get('Cancellation Date',''))
            item['cancellation_reason'] = data.get('Cancellation Reason','')
            try:
                appDocumentLinks = driver.find_elements(By.CLASS_NAME,'appDocumentLink')
                item['certificate_of_incorporation'] = appDocumentLinks[0].get_attribute('href')
                item['company_constitution'] = appDocumentLinks[1].get_attribute('href')
            except:
                pass
            for key in data.keys():
                if 'Previous Name' in key:
                    Previous_extracted_data = {
                        'name': data.get('Previous Name', ""),
                        'meta_detail': {
                            'start_date': data.get('Start Date', "").split(' ')[0].strip(),
                            'end_date': data.get('End Date', "").split(' ')[0].strip()
                        }
                    }
                    if any(Previous_extracted_data.values()):
                        previous_names_detail.append(Previous_extracted_data)

            type_add = False
            unique_activities = set()
            for key in data.keys():
                if 'Business Activity' in key:
                    index = key.split('_')[-1]
                    extracted_data_ = {
                            'business_activity': data.get('Business Activity_{}'.format(index), data.get('Business Activity')),
                            'commence_date': data.get('Date Business Activity Commenced_{}'.format(index),data.get('Date of Commencement of Business Activity_{}'.format(index),data.get('Date Business Activity Commenced',data.get('Date of Commencement of Business Activity','')))),
                            }
                    if any(extracted_data_.values()) and tuple(extracted_data_.items()) not in unique_activities:
                        if not type_add:
                            additional_detail.append({"type": "activities_information", "data": []})
                            type_add = True
                        unique_activities.add(tuple(extracted_data_.items()))
                        additional_detail[0]['data'].append(extracted_data_)
            
            type_added = False
            for key in data.keys():
                if 'Previous Status' in key:
                    index = key.split('_')[-1]
                    previous_status_extracted_data = {
                        'previous_status': data.get('Previous Status_{}'.format(index), data.get('Previous Status','')),
                        'start_date': data.get('Start Date_{}'.format(index), data.get('Start Date','')).split(' ')[0],
                        'end_date': data.get('End Date_{}'.format(index), data.get('End Date','')).split(' ')[0],
                        "cancellation_reason": data.get('Cancellation Reason_{}'.format(index), data.get('Cancellation Reason','')),
                    }
                    if any(previous_status_extracted_data.values()):
                        if not type_added:
                            additional_detail.append({"type": "previous_status_history", "data": []})
                            type_added = True
                        try:
                            additional_detail[1]["data"].append(previous_status_extracted_data)
                        except:
                            additional_detail[0]["data"].append(previous_status_extracted_data)
        
        if tab_names[idx] == "Addresses":
            show_more_info(driver)
            time.sleep(2)
            data = get_page_tab_data(driver)

            meta_detail = {"effective_date": format_date(data.get('Effective Date')),"start_date":format_date(data.get('Start Date'))} if data.get('Effective Date',data.get('Start Date','')) is not None and data.get('Effective Date',data.get('Start Date','')) != "" else {}
            addresses_detail.append({
                "type": "office_address",
                "address": data.get('Address of Registered Office', data.get('_2',data.get('Principal Place of Business',''))),
                "meta_detail": meta_detail
            })
            if data.get('Address of Registered Office_2',data.get('_3','')) is not None and data.get('Address of Registered Office_2',data.get('_3','')) != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_2')),"end_date":format_date(data.get('End Date','')),"start_date":format_date(data.get('Start Date_2',''))}
                addresses_detail.append({
                    "type": "historical_office_address_1",
                    "address": data.get('Address of Registered Office_2',data.get('_3')),
                    "meta_detail": meta_detail
                })
            
            if data.get('Address of Registered Office_3') is not None and data.get('Address of Registered Office_3') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_3')),"end_date":format_date(data.get('End Date_2',''))} if data.get('Effective Date_2') is not None and data.get('Effective Date_2') != "" else {}
                addresses_detail.append({
                    "type": "historical_office_address_2",
                    "address": data.get('Address of Registered Office_3'),
                    "meta_detail": meta_detail
                })

            if data.get('Address for Service') is not None and data.get('Address for Service') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_2'))} if data.get('Effective Date_2') is not None and data.get('Effective Date_2') != "" else {}
                addresses_detail.append({
                    "type": "service_address",
                    "address": data.get('Address for Service'),
                    "meta_detail": meta_detail
                })
            if data.get('Address for Service_2') is not None and data.get('Address for Service_2') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_6')), "end_date":format_date(data.get('End Date',''))} if data.get('Effective Date_6') is not None and data.get('Effective Date_3') != "" else {}
                addresses_detail.append({
                    "type": "historical_service_address",
                    "address": data.get('Address for Service_2'),
                    "meta_detail": meta_detail
                })
            if data.get('Address for Communication') is not None and data.get('Address for Communication') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_3'))} if data.get('Effective Date_3') is not None and data.get('Effective Date_3') != "" else {}
                addresses_detail.append({
                    "type": "communication_address",
                    "address": data.get('Address for Communication'),
                    "meta_detail": meta_detail
                })
            
            if data.get('Additional Place of Business Address',data.get('_3')) is not None and data.get('Additional Place of Business Address',data.get('_3')) != "":
                meta_detail = {"start_date": format_date(data.get('Start Date_3'))} if data.get('Start Date_3') is not None and data.get('Start Date_3') != "" else {}
                addresses_detail.append({
                    "type": "other_address",
                    "address": data.get('Additional Place of Business Address',data.get('_3')),
                    "meta_detail": meta_detail
                })
        
        if tab_names[idx] == "Directors":
            show_more_info(driver)
            data = get_page_tab_data(driver)
            people_detail.extend(get_directors(data))
        if tab_names[idx] == "Owners":
            data = get_page_tab_data(driver)
            people_detail.extend(get_owners(data))
        if tab_names[idx] == "Shares & Shareholders":
            data = get_page_tab_data(driver)
            filtered_data = {k: v for k, v in data.items() if k.strip()}
            people_detail.extend(get_shareholders(filtered_data))
        if tab_names[idx] == "Authorised Agents":
            data = get_page_tab_data(driver)
            people_detail.extend(authorised_agents(data))
        if tab_names[idx] == "Share Bundles":
            data = get_page_tab_data(driver)
            additional_detail = get_sharebundles(data)
        if tab_names[idx] == "Filings":
            fillings_detail.extend(get_filings(driver))
        item['addresses_detail'] = addresses_detail
        item['people_detail'] = people_detail
        item['fillings_detail'] = fillings_detail
        item['additional_detail'] = additional_detail
        item['previous_names_detail'] = previous_names_detail
    
    return item

try:
    skip_flag = True
    url = "https://www.businessregistries.gov.to/tonga-master/relay.html?url=https%3A%2F%2Fwww.businessregistries.gov.to%2Ftonga-master%2Fservice%2Fcreate.html%3FtargetAppCode%3Dtonga-master%26targetRegisterAppCode%3Dtonga-companies%26service%3DregisterItemSearch&target=tonga-master"
    driver.get(url)
    wait = WebDriverWait(driver, 25)
    start = sys.argv[2] if len(sys.argv) > 2 else 'a'
    for letter in range(ord(start), ord('z')+1):
        input_box = driver.find_element(By.ID, "QueryString")
        input_box.clear()
        input_box.send_keys(chr(letter))
        select_element = Select(driver.find_element(By.ID, 'SourceAppCode'))
        select_element.select_by_index(0)
        time.sleep(2)
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "appSearchButton")))
        search_button.click()

        page_size = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='appSearchPageSize']//select")))
        select = Select(page_size)
        select.select_by_index(4)
        page_count = skip_pages()        

        while True:
            print(chr(letter), "- Page Number:", page_count)
            page_count += 1
            # Wait until the elements with the specified class name are present
            company_links = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu"))
            )

            for i, element in enumerate(company_links):
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")))
                company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
                company_tags[i].click()
                if len(driver.find_elements(By.CLASS_NAME, 'appTabs')) == 0:
                    driver.back()
                    continue
                data = get_page_data(driver)
                DATA = {
                    "name": data.get("name"),
                    "registration_number": data.get("registration_number"),
                    "registration_date": data.get("registration_date"),
                    "re_registration_date":data.get('re_registration_date'),
                    "status": data.get("status") if data.get("status") is not None else "",
                    "incorporation_date": data.get("incorporation_date"),
                    "have_own_rules": data.get("have_own_rules"),
                    "certificate_of_incorporation":data.get('certificate_of_incorporation',''),
                    "company_constitution":data.get('company_constitution',''),
                    "licence_status":data.get('licence_status'),
                    "cancellation_date":data.get('cancellation_date'),
                    "cancellation_reason":data.get('cancellation_reason'),
                    "jurisdiction":data.get('country_of_incorporation') if data.get('country_of_incorporation') is not None else "",
                    "ar_filing_month":data.get('ar_filing_month'),
                    "filing_month": data.get("filing_month"),
                    "last_filed_date": data.get("last_filed_date"),
                    "tax_number": data.get("tax_number"),
                    "struck_off_date": data.get("struck_off_date"),
                    "addresses_detail": data.get("addresses_detail"),
                    "people_detail": data.get("people_detail"),
                    "fillings_detail": data.get('fillings_detail'),
                    "additional_detail":data.get('additional_detail'),
                    "previous_names_detail":data.get('previous_names_detail')
                }
                
                ENTITY_ID = tonga_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
                BIRTH_INCORPORATION_DATE = data['incorporation_date']
                DATA = tonga_crawler.prepare_data_object(DATA)
                ROW = tonga_crawler.prepare_row_for_db(ENTITY_ID, data.get("name").replace("%","%%"), BIRTH_INCORPORATION_DATE, DATA)

                tonga_crawler.insert_record(ROW)
                driver.back()
            try:
                time.sleep(2)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
                time.sleep(5)
            except:
                break

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    tonga_crawler.db_log(log_data)
    tonga_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    tonga_crawler.db_log(log_data)