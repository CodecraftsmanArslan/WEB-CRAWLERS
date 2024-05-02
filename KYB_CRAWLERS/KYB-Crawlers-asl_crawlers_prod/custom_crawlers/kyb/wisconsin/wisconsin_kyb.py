"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import os, base64
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import nopecha 
import nopecha as nopecha1
from time import sleep
import random

nopecha.api_key = ENV.get('NOPECHA_KEY0')
nopecha1.api_key = ENV.get('NOPECHA_KEY1')

meta_data = {
    'SOURCE' :'Wisconsin Department of Financial Institutions',
    'COUNTRY' : 'Wisconsin',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.wdfi.org/apps/corpsearch/Results.aspx?type=Simple&q=a", 
                        "Source Description": "The Wisconsin Department of Financial Institutions (DFI) is a state agency in Wisconsin, USA, responsible for regulating and supervising various financial entities operating within the state. The department's mission is to protect consumers and ensure the stability and integrity of Wisconsin's financial system."},
    'URL' : 'https://www.wdfi.org/apps/corpsearch/Results.aspx?type=Simple&q=a',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': True,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Wisconsin'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

wisconsin_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  wisconsin_crawler.get_selenium_helper()

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = sys.argv[1]
else:
    start = 'a'

try:
    duplicate_array = []
    for letter in range(ord(start), ord('z')+1):
        print(chr(letter))
        domain = "https://www.wdfi.org/apps/corpsearch/"
        url = f"{domain}Results.aspx?type=Simple&q={chr(letter)}"
        

        DOES_PROXY_WORK = False
        while not DOES_PROXY_WORK:
            RANDOM_US_PROXY = wisconsin_crawler.get_a_random_US_proxy(raw=True)
            print(f'trying with proxy {RANDOM_US_PROXY}')
            driver = request_helper.create_driver(headless=True,proxy=True,proxy_server=RANDOM_US_PROXY, timeout=30)
            try:
                driver.get(url)
                DOES_PROXY_WORK = True
            except:
                driver.close()
                DOES_PROXY_WORK = False

        CONTENT_TYPE = len(driver.page_source)
        # Create a BeautifulSoup object by passing in the response content and specifying the parser
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', attrs={'id': 'results'})
        if table is not None:
            trs = table.find_all('tr')

            for tr in trs[1:]:
                sleep(3+round(random.random()*4))

                people_detail = []
                fillings_detail = []
                addresses_detail = []
                previous_names_detail = []

                link = tr.find('a')['href']
                page_url = f"{domain}{link}"
                if page_url in duplicate_array:
                    continue
                duplicate_array.append(page_url)
                driver.get(page_url)
                captcha = driver.find_elements(By.ID, 'frmCaptcha')

                retry_limit = 3
                retry_counter = 0
                captcha_solved = False

                if len(captcha) > 0:
                    while retry_counter < retry_limit and not captcha_solved:
                            el = driver.find_element(By.ID, 'img')
                            el.screenshot('captcha/captcha.png')
                            with open('captcha/captcha.png', 'rb') as image_file:
                                image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')

                            captcha_text = nopecha.Recognition.solve(
                                type='textcaptcha',
                                image_urls=[image_64_encode],
                            )
                            input_box = driver.find_element(By.ID, 'txt')
                            input_box.clear()
                            input_box.send_keys(captcha_text)

                            submit_button = driver.find_element(By.ID, 'btnSubmit')
                            if submit_button is not None:
                                submit_button.click()

                            # Wait for the response or page to load
                            time.sleep(2)

                            # Check if captcha validation failed
                            vld_captcha = driver.find_elements(By.ID, 'vldCAPTCHA')
                            if len(vld_captcha) > 0:
                                print('Captcha validation failed. Retrying...')
                                retry_counter += 1
                            else:
                                print('Captcha solved successfully!')
                                captcha_solved = True

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.find('table', attrs={'class': 'stats'})
                name_ = soup.find('h1', attrs={'id': 'entityName'})
                if name_ is not None:
                    # Remove leading and trailing spaces
                    name_ = name_.text.strip()
                    # Remove '\n' characters
                    name_ = name_.replace('\n', '')
                    # Replace multiple consecutive spaces with a single space
                    NAME = ' '.join(name_.split())
                else:
                    NAME = ""
                if table is not None:
                    # Find all <tr> elements
                    tr_elements = table.find_all('tr')

                    # Initialize a dictionary to store the extracted values
                    values = {}

                    # Iterate over the <tr> elements
                    for tr_element in tr_elements:
                        # Find the <td> elements within the current <tr> element
                        td_elements = tr_element.find_all('td')
                        if len(td_elements) >= 2:
                            if td_elements[0].get_text(strip=True) == 'Registered AgentOffice':
                                agent_name =  td_elements[1].find('div').text.strip().replace("'", "").replace("%", "%%") if td_elements[1].find('div') is not None else ""
                                agent_address = td_elements[1].find('address').text.strip().replace("'", "").replace("%", "%%") if td_elements[1].find('address') is not None else ""
                            elif td_elements[0].get_text(strip=True) == 'Status':
                                if td_elements[1] is not None and td_elements[1].find('a') is not None:
                                    td_elements[1].a.extract() 
                                    status = td_elements[1].get_text(strip=True)
                                else:
                                    status = ""
                            elif td_elements[0].get_text(strip=True) == 'Principal Office':
                                if td_elements[1] is not None:
                                    postal_address = td_elements[1].text 
                                    # Remove leading and trailing spaces
                                    postal_address = postal_address.strip()
                                    # Remove newlines and extra spaces
                                    postal_address = ' '.join(postal_address.split())
                                else:
                                    postal_address = ""
                            else:
                                label = td_elements[0].get_text(strip=True)
                                data = td_elements[1].get_text(strip=True)
                                # Store the extracted values in the dictionary
                                values[label] = data

                    registration_number = values.get('Entity ID')
                    registration_date = values.get('RegisteredEffective Date').replace("/", "-") if values.get('RegisteredEffective Date') is not None else ""
                    period_of_existence = values.get('Period of Existence').replace("'", "").replace("%", "%%") if values.get('Period of Existence') is not None else ""
                    status_date = values.get('Status Date').replace("/", "-") if values.get('Status Date') is not None else ""
                    type = values.get('Entity Type').replace("'", "").replace("%", "%%") if values.get('Entity Type') is not None else ""
                    annual_report_requirements = values.get('Annual ReportRequirements').replace("'", "").replace("%", "%%") if values.get('Annual ReportRequirements') is not None else ""
                    incorporation_date = values.get('Foreign Organization Date').replace("/", "-") if values.get('Foreign Organization Date') is not None else ""
                    paid_capital = values.get('Paid Capital Represented').replace("'", "").replace("%", "%%") if values.get('Paid Capital Represented') is not None else ""
                    jurisdiction = values.get('Foreign State').replace("'", "").replace("%", "%%") if values.get('Foreign State') is not None else ""

                    if agent_name is not None and agent_name != "":
                        people_detail.append({
                            "name": agent_name,
                            "address": ' '.join(agent_address.split()) if agent_address is not None else "",
                            "designation": "registered_agent"
                        })

                    if postal_address is not None and postal_address != "":
                        addresses_detail.append({
                            "type": "office_address",
                            "address": postal_address.replace("'", "").replace("%", "%%")
                        })

                    table = soup.find('table', attrs={'id': 'ctl00_cpContent_grdOrgEvents'})
                    if table is not None:
                        data = []
                        headers = [header.text.strip() for header in table.find_all('th')]

                        for row in table.find_all('tr')[1:]:
                            row_data = [cell.text.strip() for cell in row.find_all('td')]
                            data.append(dict(zip(headers, row_data)))

                        for val in data:
                            fillings_detail.append({
                                "title": val.get('Transaction').replace("'", "").replace("%", "%%") if val.get('Transaction') is not None else "",
                                "date": val.get('Filed Date').replace("/", "-") if val.get('Filed Date') is not None else "",
                                "description": val.get('Description').replace("'", "").replace("%", "%%") if val.get('Description') is not None else "",
                                "meta_detail": {
                                    "effective_date": val.get('Effective Date').replace("/", "-") if val.get('Effective Date') is not None else ""
                                }
                            })

                    table = soup.find('table', attrs={'id': 'ctl00_cpContent_grdOldNames'})
                    if table is not None:
                        data = []
                        headers = [header.text.strip() for header in table.find_all('th')]

                        for row in table.find_all('tr')[1:]:
                            row_data = [cell.text.strip() for cell in row.find_all('td')]
                            data.append(dict(zip(headers, row_data)))

                        for val in data:
                            if val.get('Name') is not None and val.get('Name') != "":
                                previous_names_detail.append({
                                    "update_date": val.get('Change Date').replace("/", "-") if val.get('Change Date') is not None else "",
                                    "name": val.get('Name').replace("'", "").replace("%", "%%")
                                })

                    DATA = {
                        "name": NAME,
                        "registration_number": registration_number,
                        "registration_date": registration_date,
                        "status" : status,
                        "type": type,
                        "incorporation_date": incorporation_date,
                        "jurisdiction": jurisdiction,
                        "period_of_existence": period_of_existence,
                        "status_date": status_date,
                        "annual_report_requirements": annual_report_requirements,
                        "paid_capital": paid_capital,
                        "people_detail": people_detail,
                        "fillings_detail": fillings_detail,
                        "addresses_detail": addresses_detail,
                        "previous_names_detail": previous_names_detail
                    }
                    
                    ENTITY_ID = wisconsin_crawler.generate_entity_id(reg_number=registration_number)
                    BIRTH_INCORPORATION_DATE = ''
                    DATA = wisconsin_crawler.prepare_data_object(DATA)
                    ROW = wisconsin_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                    wisconsin_crawler.insert_record(ROW)
                else:
                    print("Table not found")
                    time.sleep(60*60)
                    continue
        else:
            time.sleep(60*60)
            continue

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    wisconsin_crawler.db_log(log_data)
    wisconsin_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    wisconsin_crawler.db_log(log_data)