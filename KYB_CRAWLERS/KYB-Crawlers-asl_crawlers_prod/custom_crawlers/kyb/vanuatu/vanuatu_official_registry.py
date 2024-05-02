"""Set System Path"""
import sys
from pathlib import Path
import traceback
from CustomCrawler import CustomCrawler
import json
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from bs4 import BeautifulSoup
import requests, time,re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from dateutil import parser

ENV =  {
           'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')                 
        }

meta_data = {
    'SOURCE' :'Vanuatu Financial Services Commission (VFSC)',
    'COUNTRY' : 'Vanuatu',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.vfsc.vu/vanuatu-master/viewInstance/view.html?id=a5c1e83ff0a6678befb27619920661eb02f5eb90e4f80cc3&_timestamp=444162467888918", 
                        "Source Description": "The Vanuatu Financial Services Commission (VFSC) is the regulatory authority responsible for overseeing and regulating the financial services sector in Vanuatu, a small island nation in the South Pacific Ocean. The VFSC is tasked with ensuring the integrity, stability, and transparency of the financial services industry in Vanuatu."},
    'URL' : 'https://www.vfsc.vu/vanuatu-master/viewInstance/view.html?id=a5c1e83ff0a6678befb27619920661eb02f5eb90e4f80cc3&_timestamp=444162467888918',
    'SOURCE_TYPE' : 'HTML'
}
ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Vanuatu Official Registry"
}



vanuatu_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  vanuatu_crawler.get_requests_helper()

selenium_helper =  vanuatu_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

# Check if a command-line argument is provided
# arguments = sys.argv
# page_number = int(arguments[1]) if len(arguments)>1 else 1
# Define the search range

wait = WebDriverWait(driver, 30)
driver.get('https://www.vfsc.vu/')
register_search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[4]/div/div/div[2]/div/article/div/a[2]')))
register_search_btn.click()

select_field = wait.until(EC.presence_of_element_located((By.ID, "SourceAppCode")))
select = Select(select_field)
select.select_by_index(0)

def get_historic_addresses(browser):
    addresses_detail = []
    expand_buttons = browser.find_elements(By.CLASS_NAME, "appExpando")
    for index in range(len(expand_buttons)):
        if index % 2 == 1:
            expand_buttons[index].click()
            time.sleep(1)
    expando_childrens = browser.find_elements(By.CLASS_NAME, "appExpandoChildren")
    if len(expando_childrens) > 0:
        data = get_page_tab_data(browser)
        if data.get('Registered Office Address_2') is not None and data.get('Registered Office Address_2') != "":
            meta_detail = {"end_date": format_date(data.get('End Date')), "effective_date": format_date(data.get('Effective Date_2'))}
            addresses_detail.append({
                "type": "historic_registered_address",
                "address": data.get('Registered Office Address_2'),
                "meta_detail": meta_detail
            })
        if data.get('Postal Address_2') is not None and data.get('Postal Address_2') != "":
            meta_detail = {"end_date": format_date(data.get('End Date_2')), "effective_date": format_date(data.get('Effective Date_4'))}
            addresses_detail.append({
                "type": "historic_postal_address",
                "address": data.get('Postal Address_2'),
                "meta_detail": meta_detail
            })
    return addresses_detail

def get_committee_members(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Name': 'name',
        'Occupation':'occupation',
        'Appointed Date': 'appointment_date',
        'Ceases Date': 'ceases_date',
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    if 'meta_detail' in current_entry and 'ceases_date' in current_entry["meta_detail"]:
                        current_entry["designation"] = f"former_{current_entry['meta_detail']['designation']}"
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    if 'meta_detail' in current_entry and 'ceases_date' in current_entry["meta_detail"]:
                        current_entry["designation"] = f"former_{current_entry['meta_detail']['designation']}"
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Name':
                current_entry['name'] = value
            elif label_name == 'Occupation':
                current_entry['designation'] = value
            elif label_name == 'Appointed Date':
                current_entry['appointment_date'] = format_date(value)
            elif label_name == 'Ceases Date':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["ceases_date"] = value

    if current_entry:
        if 'meta_detail' in current_entry and 'ceases_date' in current_entry["meta_detail"]:
            current_entry["designation"] = f"former_{current_entry['meta_detail']['designation']}"
        data_array.append(current_entry)
    return data_array

def get_authorised_agents(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Residential Address': 'address',
        'Name': 'name',
        'Postal Address':'postal_address',
        'Date of Appointment': 'appointment_date',
        'Entity Name': 'name',
        'Entity Number': 'entity_number',
        'Registered Office Address': 'address',
        'Email Address': 'email',
        'Contact Number': 'phone_number'
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Name' or label_name == 'Entity Name':
                current_entry['designation'] = 'registered_agent'
                current_entry['name'] = value
            elif label_name == 'Residential Address' or label_name == 'Registered Office Address':
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Appointed' or label_name == 'Date of Appointment':
                current_entry['appointment_date'] = format_date(value)
            elif label_name == 'Email Address' or label_name == 'Email':
                current_entry['email'] = value
            elif label_name == 'Contact Number':
                current_entry['phone_number'] = value.replace('[No Area Code]', '')
            elif label_name == 'Entity Number':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["entity_number"] = value

    if current_entry:
        data_array.append(current_entry)
    return data_array


def get_share_allocations(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Number of shares': 'number_of_shares',
        'Name': 'name',
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Number of shares':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["number_of_shares"] = value
            elif label_name == 'Name' or label_name == 'Company Name':
                current_entry['designation'] = 'shareholder'
                current_entry['name'] = value
    if current_entry:
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
        'Ceased': 'ceased',
        'Company Number': 'company_number',
        'Company Name': 'name',
        'Primary Address': 'address'
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
            elif label_name == 'Company Number':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["company_number"] = value
            elif label_name == 'Name' or label_name == 'Company Name':
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

def get_directors(data):
    data_array = []
    current_entry = {}
    label_mappings = {
        'Name': 'name',
        'Residential Address': 'address',
        'Date of Appointment': 'appointment_date',
        'Postal Address': 'postal_address',
        'Ceased': 'ceased',
        'Director Consent': 'consent'
    }
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name in label_mappings:
                if label_mappings[label_name] in current_entry:
                    if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
                        current_entry["designation"] = "former_director"
                    else:
                        current_entry["designation"] = "director"
                    data_array.append(current_entry)
                    current_entry = {}
                elif "meta_detail" in current_entry and label_mappings[label_name] in current_entry["meta_detail"]:
                    if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
                        current_entry["designation"] = "former_director"
                    else:
                        current_entry["designation"] = "director"
                    data_array.append(current_entry)
                    current_entry = {}
            if label_name == 'Name':                    
                current_entry = {'name': value}
            elif label_name == 'Residential Address':
                current_entry['address'] = value
            elif label_name == 'Postal Address':
                current_entry['postal_address'] = value
            elif label_name == 'Director Consent':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry['meta_detail']['consent'] = value
            elif label_name == 'Date of Appointment':
                current_entry['appointment_date'] = format_date(value)
            elif label_name == 'Ceased':
                if 'meta_detail' not in current_entry:
                    current_entry['meta_detail'] = {}
                current_entry["meta_detail"]["ceased"] = value

    if current_entry:
        if 'meta_detail' in current_entry and 'ceased' in current_entry["meta_detail"]:
            current_entry["designation"] = "former_director"
        else:
            current_entry["designation"] = "director"
        data_array.append(current_entry)
    return data_array

def get_filings(driver):
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

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

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
                value =  f"{next_sibling.text}"
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
    contacts_detail = []
    people_detail = []
    previous_names_detail = []
    fillings_detail = []
    item = {}

    for ul_element in ul_elements:
        if ul_element.text in ['General', 'General Details', 'Details','Addresses', 'Directors', 'Shares & Shareholders', 'Share Allocations', 'Filings', 'Authorised Persons / Agents', 'Registered Agent', 'Committee Members']:
            tab_names.append(ul_element.text)
            a_tag = ul_element.find_element(By.TAG_NAME, 'a')
            to_be_executed = a_tag.get_attribute("onclick")
            to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
            scripts_tob_executed.append(to_be_executed)
    for idx, script in enumerate(scripts_tob_executed):
        data = {}
        time.sleep(2)
        driver.execute_script(script)
        selected_tab = driver.find_element(By.CSS_SELECTOR, "li.appTabSelected")
        time.sleep(2)
        if tab_names[idx] == "General Details" or tab_names[idx] == "General" or tab_names[idx] == "Details": 
            try:
                expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
                expand_button[1].click()
                time.sleep(1)
            except Exception as e:
                pass
            data = get_page_tab_data(driver)
            item['name'] = data.get('')
            item['entity_type'] = data.get('Entity Type')
            item['type'] = data.get('Company Type') if data.get('Company Type') is not None else ""
            item['status'] = data.get('Entity Status') if data.get('Entity Status') is not None else ""
            item['registration_date'] = format_date(data.get('Registration Date'))
            item['re_registration_date'] = data.get('Re-Registration Date')
            item['removal_date'] = data.get('De-Registration Date')
            item['have_own_rules'] = data.get('Have Own Rules?')
            item['renewal_filing_month'] = data.get('Renewal Filing Month')
            item['filing_month'] = data.get('Annual Return Filing Month')
            item['last_filed_date'] = data.get('Annual Return Last Filed on')
            if item['status'] == "":
                item['status'] = data.get('Charitable Association Status')
            item['incorporation_date'] = data.get('Incorporation Date') if data.get('Incorporation Date') is not None else ""
            item['filing_month'] = data.get('Annual Report Filing Month')
            item['objects_of_the_committee_of_the_charitable_association'] = data.get('Objects of the Committee of the Charitable Association')
            item['statement_of_assets_and_liabilities'] = data.get('Statement of Assets and Liabilities')
            item['articles/rules/constitution'] = data.get('Articles / Rules / Constitution')

            previous_names_detail.append({
                'previous_status': data.get('Previous Status', ''),
                'start_date': data.get('Start Date', ''),
                'end_date': data.get('End Date', '')
            })
            if data.get('Model Rules') is not None and data.get('Model Rules') != '':
                if 'https' in data.get('Model Rules'):
                    parts = data.get('Model Rules').split('https')
                    additional_detail.append({
                        "type": "constitution_information",
                        "data": [{
                            "name": parts[0].strip() if len(parts) > 1 else "",
                            "file_url": 'https' + parts[1].strip() if len(parts) > 1 else ""
                        }]
                    })
            if data.get('Business Activity') is not None:
                additional_detail.append({
                    "type": "activity_information",
                    "data": [{
                        "activity_name": data.get('Business Activity'),
                        "commencement_date": data.get('Date of Commencement of Business Activity')
                    }]
                })
        elif tab_names[idx] == "Addresses":
            data = get_page_tab_data(driver)
            if data.get('Registered Office Address') is not None and data.get('Registered Office Address') != "" or data.get('Registered Office') is not None and data.get('Registered Office') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date'))} if data.get('Effective Date') is not None and data.get('Effective Date') != "" else {}
                office_address = data.get('Registered Office Address') if data.get('Registered Office Address') else data.get('Registered Office')
                addresses_detail.append({
                    "type": "office_address",
                    "address": office_address,
                    "meta_detail": meta_detail
                })
            if data.get('Principal Place of Business') is not None and data.get('Principal Place of Business') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date'))} if data.get('Effective Date') is not None and data.get('Effective Date') != "" else {}
                addresses_detail.append({
                    "type": "office_address",
                    "address": data.get('Principal Place of Business'),
                    "meta_detail": meta_detail
                })
            if data.get('Postal Address') is not None and data.get('Postal Address') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_2'))} if data.get('Effective Date_2') is not None and data.get('Effective Date_2') != "" else {}
                addresses_detail.append({
                    "type": "postal_address",
                    "address": data.get('Postal Address'),
                    "meta_detail": meta_detail
                })
            if data.get('Email') is not None and data.get('Email') != "":
                contacts_detail.append({
                    "type": "email",
                    "value": data.get("Email")
                })
            if data.get('Address for Records') is not None and data.get('Address for Records') != "":
                meta_detail = {"effective_date": format_date(data.get('Effective Date_3'))} if data.get('Effective Date_3') is not None and data.get('Effective Date_3') != "" else {}
                addresses_detail.append({
                    "type": "address_for_records",
                    "address": data.get('Address for Records'),
                    "description": data.get('Description of Records'),
                    "meta_detail": meta_detail
                })
            addresses_detail.extend(get_historic_addresses(driver))

        elif tab_names[idx] == "Shares & Shareholders":
            expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
            if len(expand_button) > 0:
                expand_button[1].click()
            data = get_page_tab_data(driver)
            if data.get('Total Shares') is not None and data.get('Total Shares').strip() != "":
                additional_detail.append({
                    "type": "share_information",
                    "data":[{
                        "total_shares": data.get('Total Shares'),
                        "more_than_one_class": data.get('Is there more than one class of share for this company?')
                    }]
                })
            filtered_data = {k: v for k, v in data.items() if k.strip()}
            people_detail.extend(get_shareholders(filtered_data))
        elif tab_names[idx] == "Share Allocations":
            data = get_page_tab_data(driver)
            filtered_data = {k: v for k, v in data.items() if k.strip()}
            people_detail.extend(get_share_allocations(filtered_data))
        elif tab_names[idx] == "Filings":
            fillings_detail.extend(get_filings(driver))
        elif tab_names[idx] == "Directors":
            expand_button = driver.find_elements(By.CLASS_NAME, "appExpando")
            if len(expand_button) > 0:
                expand_button[1].click()
            data = get_page_tab_data(driver)
            people_detail.extend(get_directors(data))
        elif tab_names[idx] == "Authorised Persons / Agents" or tab_names[idx] == "Registered Agent":
            data = get_page_tab_data(driver)
            people_detail.extend(get_authorised_agents(data))
        elif tab_names[idx] == "Committee Members":
            data = get_page_tab_data(driver)
            people_detail.extend(get_committee_members(data))

    item['contacts_detail'] = contacts_detail
    item['addresses_detail'] = addresses_detail
    item['additional_detail'] = additional_detail
    item['people_detail'] = people_detail
    item['previous_names_detail'] = previous_names_detail
    item['fillings_detail'] = fillings_detail
    return item

def skip_pages():
    start_number = int(sys.argv[2]) if len(sys.argv) > 2 else 0
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


try:
    flag = True
    wait = WebDriverWait(driver, 20)
    start_char = sys.argv[1] if len(sys.argv) > 2 else "a"
    characters = list(range(ord('a'), ord('z') + 1)) + list(range(ord('0'), ord('9') + 1))
    for char in characters:
            if chr(char) != start_char and flag:
                continue
            else:
                flag = False
            time.sleep(3)
            search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="QueryString"]')))
            search_input.clear()
            search_input.send_keys(chr(char))
            search_input.send_keys(Keys.RETURN)
            page_count = skip_pages()
            while True:
                print(f"Character: {chr(char)} Page Number: {page_count}")
                page_count += 1
                company_links = wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu"))
                )

                for i, element in enumerate(company_links):
                    company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
                    if i > len(company_tags): break 
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
                    data["registration_number"] = registration_number
                    ENTITY_ID = vanuatu_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
                    BIRTH_INCORPORATION_DATE = ''
                    DATA = vanuatu_crawler.prepare_data_object(data)
                    ROW = vanuatu_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                    vanuatu_crawler.insert_record(ROW)
                    driver.back()
                try:
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
                    time.sleep(5)
                except:
                    break

    vanuatu_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    vanuatu_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    vanuatu_crawler.db_log(log_data) 
