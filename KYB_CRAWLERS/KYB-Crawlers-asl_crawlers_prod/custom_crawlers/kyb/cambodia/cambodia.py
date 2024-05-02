"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from deep_translator import GoogleTranslator
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

meta_data = {
    'SOURCE': 'Cambodia Ministry of Commerce',
    'COUNTRY': 'Cambodia',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.businessregistration.moc.gov.kh",
                      "Source Description": "The Business Registration Department is a department within the Ministry of Commerce of Cambodia. It is responsible for overseeing the registration and regulation of businesses operating within the country. The department plays a crucial role in promoting and facilitating business activities, ensuring compliance with relevant laws and regulations, and supporting the growth and development of the business sector in Cambodia."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.businessregistration.moc.gov.kh'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Cambodia Ministry of Commerce"
}

# It translates the forign language words used in record.
def googleTranslator(record_):
    """Description: This method is used to translate any language to english. It take name as input and return the translated name
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'", "''").replace('\"', "")
    except:
        record_

cambodia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = cambodia_crawler.get_requests_helper()
selenium_helper = cambodia_crawler.get_selenium_helper()

# It will skip all the crawled pages to resume from where the crawler stopped.
def skip_pages():
    """
    Skip pages in a web application.

    This function takes the starting page number as a command line argument (if provided) or defaults to 1.
    It then skips pages in the web application by clicking on the 'Next' button.

    Returns:
    int: The page count after skipping pages.
    """
    start_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    if start_number != 1:
        for i in range(start_number-1):
            try:
                time.sleep(5)
                print("Skipping page number: ", i+1)
                driver.execute_script("arguments[0].click();", driver.find_element(
                    By.CLASS_NAME, "appNext").find_element(By.TAG_NAME, 'a'))
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    page_count = start_number
    time.sleep(5)
    return page_count


driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
driver.get('https://www.businessregistration.moc.gov.kh')
print("Website Opened!")

def show_more_info(driver):
    """
    Clicks on the collapsed elements with class 'appExpandoCollapsed' to expand and show more information.
    Parameters:
    - driver (WebDriver): The Selenium WebDriver instance.
    """
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
    current_entry = {'meta_detail': {}}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name (English)' or label_name == 'Name':
                if current_entry and current_entry.get('name', ''):
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'director', 'meta_detail': current_entry['meta_detail']}

            elif label_name == 'Name (Khmer)':
                current_entry['meta_detail']['aliases'] = value.replace('[Missing]','')
            elif label_name == 'Ceased':
                current_entry['meta_detail']['inactive'] = value.split('\n')[0]
            elif label_name == 'Chairman of the Board of Directors':
                current_entry['meta_detail']['is_this_a_director'] = value
            
            elif label_name == 'Postal Registered Office Address':
                current_entry['address'] = googleTranslator(value).replace(', ⠀,','').replace('⠀, ⠀, ','').replace("None,","").replace("none,","").replace("null,","").replace('⠀ ','')
            
            elif label_name == "Telephone":
                current_entry['phone_number'] = value.replace('(+855) [No Area Code] [No Number]','').replace('(+855) [No Area Code]','').replace('[No Number]','').replace('[No Country Code] [No Area Code]','').replace('[No Country Code]','')
            
    if current_entry:
        data_array.append(current_entry)
    
    return data_array

def get_partners(data):
    """
    Extracts partners information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to partners
    details such as name, address, consent, and appointment date. It then creates a list of
    dictionaries, each containing partners information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing partners details.

    Returns:
    - list: A list of dictionaries, each containing partners information.
    """
    data_array = []
    current_entry = {'meta_detail': {}}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name (English)' or label_name == 'Name':
                if current_entry and current_entry.get('name', ''):
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'partner', 'meta_detail': current_entry['meta_detail']}

            elif label_name == 'Name (Khmer)':
                current_entry['meta_detail']['aliases'] = value.replace('[Missing]','')
            elif label_name == 'Ceased':
                current_entry['meta_detail']['inactive'] = value.split('\n')[0]
            elif label_name == 'Address for Communication':
                current_entry['address'] = googleTranslator(value).replace(', ⠀,','').replace('⠀, ⠀, ','').replace("None,","").replace("none,","").replace("null,","").replace('⠀ ','')
            
            elif label_name == "Telephone":
                current_entry['phone_number'] = value.replace('(+855) [No Area Code] [No Number]','').replace('(+855) [No Area Code]','').replace('[No Number]','').replace('[No Country Code] [No Area Code]','').replace('[No Country Code]','')
            
    if current_entry:
        data_array.append(current_entry)
    
    return data_array

def get_managers(data):
    """
    Extracts manager information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to manager
    details such as name, address, consent, and appointment date. It then creates a list of
    dictionaries, each containing manager information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing manager details.

    Returns:
    - list: A list of dictionaries, each containing manager information.
    """
    data_array = []
    current_entry = {'meta_detail': {}}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name (English)' or label_name == 'Name':
                if current_entry and current_entry.get('name', ''):
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'manager', 'meta_detail': current_entry['meta_detail']}

            elif label_name == 'Name (Khmer)':
                current_entry['meta_detail']['aliases'] = value.replace('[Missing]','')
            elif label_name == 'Ceased':
                current_entry['meta_detail']['inactive'] = value.split('\n')[0]
            elif label_name == 'Address for Communication':
                current_entry['address'] = googleTranslator(value).replace(', ⠀,','').replace('⠀, ⠀, ','').replace("None,","").replace("none,","").replace("null,","").replace('⠀ ','')
            elif label_name == "Telephone":
                current_entry['phone_number'] = value.replace('(+855) [No Area Code] [No Number]','').replace('(+855) [No Area Code]','').replace('[No Number]','').replace('[No Country Code] [No Area Code]','').replace('[No Country Code]','')
            
    if current_entry:
        data_array.append(current_entry)
    
    return data_array

def get_owners(data):
    """
    Extracts owner information from a dictionary representing key-value pairs.

    This function takes a dictionary as input, where keys represent labels and values
    represent corresponding information. It searches for key patterns related to owner
    details such as name, address, consent, and appointment date. It then creates a list of
    dictionaries, each containing owner information.

    Parameters:
    - data (dict): A dictionary containing key-value pairs representing owner details.

    Returns:
    - list: A list of dictionaries, each containing owner information.
    """
    data_array = []
    current_entry = {'meta_detail': {}}
    for key, value in data.items():
        if key:
            label_name = key.split('_')[0]
            if label_name == 'Name (English)' or label_name == 'Name':
                if current_entry and current_entry.get('name', ''):
                    data_array.append(current_entry)
                current_entry = {'name': value, 'designation': 'owner', 'meta_detail': current_entry['meta_detail']}

            elif label_name == 'Name (Khmer)':
                current_entry['meta_detail']['aliases'] = value.replace('[Missing]','')

            elif label_name == 'Postal Registered Office Address' or label_name == 'Postal Address':
                current_entry['address'] = googleTranslator(value).replace(', ⠀,','').replace('⠀, ⠀, ','').replace("None,","").replace("none,","").replace("null,","").replace('⠀ ','')
            
            elif label_name == "Telephone":
                current_entry['phone_number'] = value.replace('(+855) [No Area Code] [No Number]','').replace('(+855) [No Area Code]','').replace('[No Number]','').replace('[No Country Code] [No Area Code]','').replace('[No Country Code]','')
            
            elif label_name == "Appointed":
                current_entry['appointment_date'] = value.split('\n')[0]
            
    if current_entry:
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
    addresses_detail = []
    people_detail = []
    previous_names_detail = []
    item = {}

    for ul_element in ul_elements:
        if ul_element.text in ['General Details', 'Addresses', 'Directors', 'Owner Details', 'Partners','Managers']:
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
            time.sleep(2)
            data = get_page_tab_data(driver)
            
            match = re.search(r'\((\d+)\)', data.get(''))
            if match:
                number = match.group(1)
            item['registration_number'] = number
            item['name'] = data.get('Company Name (in English)', data.get('Partnership Name (in English)', data.get('Sole Proprietorship Name (English)','')))
            item['type'] = data.get('_2').split(')')[-1].strip()
            item['tax_registration_date'] = data.get('Tax Registration Date','').split('\n')[0].strip()
            item['status'] = data.get('Company Status', data.get('Status',data.get('Sole Proprietorship Status',''))) 
            item['aliases'] = data.get('Sole Proprietorship Name (Khmer)', data.get('Partnership Name (in Khmer)', data.get('Proposed Name (in Khmer)', data.get('Company Name (in Khmer)', ''))))
            item['registration_date'] = data.get('Re-Registration Date','').split('\n')[0].strip()
            item['incorporation_date'] = data.get('Incorporation Date','').split('\n')[0].strip()
            item['previous_registration_number'] = data.get('Original Entity Identifier','')
            item['Annual_last_filed_date'] = data.get('Annual Return Last Filed on','').split('\n')[0].strip()
            item['tax_number'] = data.get('Tax Identification Number (TIN)','').strip() if  data.get('Tax Identification Number (TIN)') is not None else ""
            item['effective_date'] = data.get('Effective Date','').split('\n')[0].strip()
            item['Previous Name'] = data.get('Previous Name','')
            item['Start Date'] = data.get('Start Date','').split('\n')[0].replace('00:00:00','').strip()
            item['End Date'] = data.get('End Date','').split('\n')[0].replace('00:00:00','').strip()
                
            try:
                all_bussines_objectives = driver.find_elements(By.CLASS_NAME, 'appRecordEntityClassifications')

                activities_information = []
                for bussines_object in all_bussines_objectives:
                    business_details = bussines_object.text
                    business_details = business_details.split('Business Objective')[1].split("Main Business Activities")
                    business_objective = business_details[0]
                    business_activities = business_details[1]

                    activities_information.append({
                        "objectives": business_objective.replace("\n", ""),
                        "main_activities": business_activities.replace("\n", "")
                    })
            except NoSuchElementException as e:
                activities_information = []

            additional_detail = []
            activities_information = {
                "type": "activities_information",
                "data": activities_information
            }
            additional_detail.append(activities_information)
            if any(value for value in [data.get('male', data.get('Male')), data.get('female',data.get('Female')), data.get('Number_of_Cambodian', data.get('Number of Cambodian Employees')), data.get('Number_of_Foreign', data.get('Number of Foreign Employees'))]):
                employee_info = {
                    "type": "employee_information",
                    "data": [
                        {
                            "male": data.get('male', data.get('Male')),
                            "female": data.get('female', data.get('Female')),
                            "domestic_employees": data.get('Number_of_Cambodian', data.get('Number of Cambodian Employees')),
                            "foreign_employees": data.get('Number_of_Foreign', data.get('Number of Foreign Employees'))
                        }
                    ]
                }
                additional_detail.append(employee_info)
        

        item['additional_detail'] = additional_detail
        
        if tab_names[idx] == "Addresses":
            show_more_info(driver)
            time.sleep(2)
            data = get_page_tab_data(driver)
            item['email'] = data.get('Contact Email')
            item['contact_number'] = data.get('Contact Telephone Number')

            if data.get('Physical Registered Office Address') is not None and data.get('Physical Registered Office Address') != "":
                meta_detail = {"effective_date": data.get('Start Date').split('\n')[0].strip()} if data.get('Start Date') is not None and data.get('Start Date') != "" else {}
                addresses_detail.append({
                    "type": "office_address",
                    "address": googleTranslator(data.get('Physical Registered Office Address')).replace('none,','').replace("None,","").replace("None",""),
                    "meta_detail": meta_detail
                })

            if data.get('Physical Registered Office Address_2') is not None and data.get('Physical Registered Office Address_2') != "":
                meta_detail = {"effective_date": data.get('Start Date_2').split('\n')[0].strip(),"end_date":data.get('End Date','').split('\n')[0].strip()} if data.get('Effective Date_2') is not None and data.get('Effective Date_2') != "" else {}
                addresses_detail.append({
                    "type": "historical_office_address",
                    "address": data.get('Physical Registered Office Address_2').replace("None,","").replace("none,","").replace("None",""),
                    "meta_detail": meta_detail
                })
            if data.get('Postal Registered Office Address') is not None and data.get('Postal Registered Office Address') != "":
                meta_detail = {"effective_date": data.get('Start Date_3').split('\n')[0].strip()} if data.get('Start Date_3') is not None and data.get('Start Date_3') != "" else {}
                addresses_detail.append({
                    "type": "postal_address",
                    "address": data.get('Postal Registered Office Address').replace("None,","").replace("none,","").replace("None",""),
                    "meta_detail": meta_detail
                })

        if tab_names[idx] == "Directors":
            show_more_info(driver)
            data = get_page_tab_data(driver)
            people_detail.extend(get_directors(data))
        
        if tab_names[idx] == "Owner Details":
            show_more_info(driver)
            data = get_page_tab_data(driver)
            people_detail.extend(get_owners(data))
        

        if tab_names[idx] == "Partners":
            show_more_info(driver)
            data = get_page_tab_data(driver)
            people_detail.extend(get_partners(data))
        
        if tab_names[idx] == "Managers":
            show_more_info(driver)
            data = get_page_tab_data(driver)
            people_detail.extend(get_managers(data))
        
        item['addresses_detail'] = addresses_detail
        item['people_detail'] = people_detail

    return item

# It opens the webpage, enter the search keyword, scrape data and dump it in Database.
def crawl(aplhabet_digit):
    """
    Perform web crawling on a specific web application.

    This function navigates through the web application, searches for entities, and extracts detailed information
    about each entity. The information is then processed and inserted into a database.

    Raises:
    TimeoutException: If a timeout occurs while waiting for an element to be present.
    NoSuchElementException: If a required element is not found on the web page.
    """
    while True:
        try:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//div/a[@aria-controls = "appMainNavigation"]')))
            break
        except TimeoutException:
            driver.refresh()

    online_search = driver.find_element(By.XPATH, '//div/a[@aria-controls = "appMainNavigation"]')
    online_search.click()
    time.sleep(2)

    search_entity = driver.find_element(By.XPATH, '//span[contains(text(), "Search Entity")]')
    search_entity.click()
    print("Search page opened!")
    wait = WebDriverWait(driver, 25)
    while True:
        try:
            search_field = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'QueryString')))
            search_field.send_keys(aplhabet_digit)
            print("\nCurrent Aplhabet Digit", aplhabet_digit)
            time.sleep(1)
            select_register = driver.find_element(By.XPATH, '//*[@id="SourceAppCode"]/option[1]')
            select_register.click()
            print("Select Any_Register!")
            appSearchButton = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//button/span[text() = "Search"]')))
            appSearchButton.click()
            print("Search initiated!")
            page_size = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//label[text()="Page size"]/following-sibling::select')))
            page_size.click()
            select_option = driver.find_element(By.XPATH, '//option[@value="4"]')
            select_option.click()
            time.sleep(10)
            print("Showing 200 records per page now!")
            break
        except:
            print("Element not found. Refreshing the page...")
            driver.refresh()

    page_number = skip_pages()
    time.sleep(3)
    for page in range(page_number, 201):
        print('page number',page)
        
        # Wait until the elements with the specified class name are present
        company_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")))
        for i, element in enumerate(company_links):
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")))
            company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
            company_tags[i].click()
            if len(driver.find_elements(By.CLASS_NAME, 'appTabs')) == 0:
                driver.back()
                continue
            data = get_page_data(driver)
            
            OBJ = {
                "name": data.get('name'),
                "aliases": data.get('aliases'),
                "type": data.get('type'),
                "status": data.get('status'),
                'effective_date':data.get('effective_date'),
                "registration_number": data.get('registration_number'),
                "registration_date": data.get('registration_date',''),
                "oei_number": data.get('previous_registration_number',''),
                "incorporation_date": data.get('incorporation_date',''),
                "tax_number": data.get('tax_number',''),
                "tax_registration date": data.get('tax_registration','').split('\n')[0],
                "last_annual_return_filed": data.get('Annual_last_filed_date','').split('\n')[0],
                "additional_detail": data.get('additional_detail'),
                "addresses_detail": data.get('addresses_detail'),
                "contacts_detail": [
                    {
                        "type": "email",
                        "value": data.get('email','')
                    },
                    {
                        "type": "phone_number",
                        "value": data.get('contact_number','').replace('(+855) [No Area Code] [No Number]','').replace('(+855) [No Area Code]','').replace('[No Number]','').replace('[No Country Code] [No Area Code]','').replace('[No Country Code]','')
                    }
                ],
                "people_detail": data.get('people_detail'),
                'previous_names_detail':[
                        {
                            'name':data.get('Previous Name',''),
                            'meta_detail':{'start_date':data.get('Start Date',''),'end_date':data.get('End Date','')}
                        }
                    ]
            }
           
            OBJ = cambodia_crawler.prepare_data_object(OBJ)
            ENTITY_ID = cambodia_crawler.generate_entity_id(OBJ.get('registration_number'),OBJ.get('name'))
            NAME = OBJ['name'].replace('%',"%%")
            BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date",'')
            ROW = cambodia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
            cambodia_crawler.insert_record(ROW)
            print("\nCurrent Aplhabet Digit", aplhabet_digit)

            try:
                driver.back()
                time.sleep(2)
            except TimeoutException:
                time.sleep(20)
                driver.back()
                time.sleep(8)

        if len(driver.find_elements(By.CLASS_NAME, 'appNext')) > 0:
            next_button = driver.find_element(By.CLASS_NAME, 'appNext')
            next_button.click()
            time.sleep(5)
        else:
            break

try:
    # English Alphabets
    english_alphabets = [chr(i) for i in range(ord('A'), ord('Z')+1)]

    # Khmer Alphabets
    khmer_alphabets = [
        'ក', 'ខ', 'គ', 'ឃ', 'ង', 'ច', 'ឆ', 'ជ', 'ឈ', 'ញ',
        'ដ', 'ឋ', 'ឌ', 'ឍ', 'ណ', 'ត', 'ថ', 'ទ', 'ធ', 'ន',
        'ប', 'ផ', 'ព', 'ភ', 'ម', 'យ', 'រ', 'ល', 'វ', 'ឝ',
        'ឞ', 'ស', 'ហ', 'ឡ', 'អ'
        ]
    # Digits 0-9
    digits = [str(i) for i in range(10)]
    arg = str(sys.argv[1]) if len(sys.argv) > 1 else "A"
    # Combine all into one list
    combined_list = english_alphabets + khmer_alphabets + digits
    flag = True
    for aplhabet_digit in combined_list:
        if flag and arg != aplhabet_digit:
          continue
        else:
           flag = False
        crawl(aplhabet_digit)

    cambodia_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    cambodia_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    cambodia_crawler.db_log(log_data)
