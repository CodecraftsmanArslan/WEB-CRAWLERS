"""Import required library"""
import time, sys
import traceback
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from deep_translator import GoogleTranslator
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc 

import os
from dotenv import load_dotenv
load_dotenv()

"""Global Variables"""

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

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
    'SOURCE' :'Corporate and Business Registration Department (CBRD)',
    'COUNTRY' : 'Mauritius',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": " https://onlinesearch.mns.mu/", 
                        "Source Description": "The Corporate and Business Registration Department (CBRD) of Mauritius is a government agency responsible for the registration and administration of businesses and corporate entities in Mauritius. It operates under the Ministry of Financial Services and Good Governance."},
    'SOURCE_TYPE': 'HTML',
    'URL' : ' https://onlinesearch.mns.mu/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Mauritius official registry"
}

    
mauritius_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = mauritius_crawler.get_selenium_helper()

# driver = selenium_helper.create_driver(headless=False,Nopecha=False)
driver = uc.Chrome(version_main = 114, headless=True) 

def wait_for_captcha_to_be_solved(browser):
        try:
            time.sleep(3)
            iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            browser.switch_to.frame(iframe_element)
            print('trying to resolve captcha')
            wait = WebDriverWait(driver, 60) 
            checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
            print("Captcha has been Solved")
            # Switch back to the default content
            browser.switch_to.default_content()
            return browser
        except:
            print('captcha solution timeout error, retrying...')


def captcha_bypas(browser):
        pass
        # time.sleep(3)
        # div_elements = browser.find_elements(By.XPATH, '//div[@style]')
        # for div_element in div_elements:
        #     style_attribute = div_element.get_attribute('style')
        #     if 'visibility: visible' in style_attribute:
        #         wait_for_captcha_to_be_solved(driver)

def get_sibling_table(driver, keyword):
    expansion_panel = driver.find_element(By.XPATH, "//mat-panel-title[contains(text(), 'WINDING UP DETAILS')]/ancestor::mat-expansion-panel")
    table = expansion_panel.find_element(By.TAG_NAME, 'table')
    return table


def get_table(driver, keyword):
    if len(driver.find_elements(By.XPATH, f"//th[contains(text(), '{keyword}')]")) > 0:
        th_element = driver.find_element(By.XPATH, f"//th[contains(text(), '{keyword}')]")
        if len(th_element.find_elements(By.XPATH, "./ancestor::table")) > 0:
            table = th_element.find_element(By.XPATH, "./ancestor::table")
            return table
    return False

def get_charges_information(driver):
    addditional_detail = []
    table = get_table(driver, "Nature of Charge")
    if table:
        trs = table.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) == 0:
                continue
            try:
                volume = tds[1].text
                amount =tds[2].text
                property_ = tds[3].text
                date_charged = tds[4].text.replace("/", "-") if tds[4].text is not None else ""
                nature_of_charge=  tds[5].text
                date = tds[6].text.replace("/", "-") if tds[6].text is not None else ""
                currency = tds[7].text
            except:
                amount, volume, property_,date_charged ,nature_of_charge ,date ,currency = "","","","","","",""
            if nature_of_charge !="":
                addditional_detail.append({
                    "type": "charges_information",
                    "data":[{
                        "volume": volume,
                        "amount": amount,
                        "property": property_,
                        "date_charged": date_charged,
                        "nature_of_charge": nature_of_charge,
                        "date": date,
                        "currency": currency
                    }]
                }) 
    return addditional_detail

def get_business_details(driver):
    data = {}
    table = get_table(driver, "Business Registration No.")
    if table:
        trs = table.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) == 0:
                continue
            try:
                data["business_registration_no"] = tds[1].text if tds[1].text is not None else ""
                data["nature_of_business"] = tds[3].text if tds[3].text is not None else ""
                data["business_address"] = tds[4].text if tds[4].text is not None else ""
            except:
                data["business_registration_no"], data["nature_of_business"], data["business_address"] = "" , "" ,""
    return data

def get_people_data(driver, keyword):
    expansion_panel = driver.find_element(By.XPATH, f"//mat-panel-title[contains(text(), '{keyword}')]/ancestor::mat-expansion-panel")
    label_elements = expansion_panel.find_elements(By.XPATH, ".//label[@class='label']")
    data = {}
    for label_element in label_elements:
        label = label_element.text
        value_element = label_element.find_element(By.XPATH, "following-sibling::label[@class='value']")
        value = value_element.text
        data[label] = value
        data["designation"] = keyword
    return data

def get_people_details(driver):
    people_detail = []
    data = []
    data.append(get_people_data(driver, "LIQUIDATORS"))
    data.append(get_people_data(driver, "RECEIVERS"))
    data.append(get_people_data(driver, "ADMINISTRATORS"))
    for detail in data:
        if detail.get('Name:',"") != "":
            people_detail.append({ 
                "designation":detail.get("designation",''),           
                "name": detail.get('Name:',""),
                "address": detail.get('Address:',""),
                "appointment_date": detail.get('Appointed Date:',"").replace("/","-")
            })
    return people_detail

def get_winding_up_information(driver):
    addditional_detail = []
    table = get_sibling_table(driver, "Type")
    if table:
        trs = table.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) == 0:
                continue
            try:
                winding_type = tds[1].text.replace("/", "-") if tds[1].text is not None else ""
                start_date = tds[2].text.replace("/", "-") if tds[2].text is not None else ""
                end_date = tds[3].text.replace("/", "-") if tds[3].text is not None else ""
                winding_status = tds[3].text.replace("/", "-") if tds[3].text is not None else ""
            except:
                winding_type, start_date, end_date, winding_status = "","","",""
            if winding_type != "":
                addditional_detail.append({
                    "type": "winding_up_information",
                    "data": [{
                        "winding_type": winding_type,
                        "start_date": start_date,
                        "end_date": end_date,
                        "winding_status": winding_status
                    }]
                }) 
    return addditional_detail

def get_fillings_information(driver):
    fillings_detail = []
    table = get_table(driver, "Date of Return")
    if table:
        trs = table.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) == 0:
                continue
            try:
                return_date = tds[1].text.replace("/", "-") if tds[1].text is not None else ""
                meeting_date = tds[2].text.replace("/", "-") if tds[2].text is not None else ""
                fil_date = tds[3].text.replace("/", "-") if tds[3].text is not None else ""
            except:
                return_date, meeting_date, fil_date = "","",""
            if fil_date != "":
                fillings_detail.append({
                    "meta_detail":{
                        "return_date": return_date,
                        "meeting_date": meeting_date
                    },
                    "date": fil_date
                }) 
    return fillings_detail

def get_people_information(driver):
    people_detail = []
    if len(driver.find_elements(By.XPATH, f"//th[contains(text(), 'Position')]")) > 0:
        th_element = driver.find_element(By.XPATH, f"//th[contains(text(), 'Position')]")
        if len(th_element.find_elements(By.XPATH, "./ancestor::table")) > 0:
            table = th_element.find_element(By.XPATH, "./ancestor::table")
            trs = table.find_elements(By.TAG_NAME, 'tr')
            for tr in trs:
                tds = tr.find_elements(By.TAG_NAME, 'td')
                if len(tds) == 0:
                    continue
                people_detail.append({
                    "designation": tds[1].text if tds[1].text is not None else "",
                    "name": tds[2].text if tds[2].text is not None else "",
                    "address": tds[3].text if tds[3].text is not None else "",
                    "appointment_date": tds[4].text.replace("/", "-") if tds[4].text is not None else "",
                }) 
    return people_detail


def get_shares_information(driver):
    additional_detail = []
    if len(driver.find_elements(By.XPATH, f"//th[contains(text(), 'Type of Shares')]")) > 0:
        th_elements = driver.find_elements(By.XPATH, f"//th[contains(text(), 'Type of Shares')]")
        for th_element in th_elements:
            if len(th_element.find_elements(By.XPATH, "./ancestor::table")) > 0:
                table = th_element.find_element(By.XPATH, "./ancestor::table")
                trs = table.find_elements(By.TAG_NAME, 'tr')
                for tr in trs:
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    if len(tds) == 7:
                        additional_detail.append({
                            "type": "shares_information",
                            "data": [{
                                "share_type": tds[1].text if tds[1].text is not None else "",
                                "number_of_shares": tds[2].text if tds[2].text is not None else "",
                                "currency": tds[3].text if tds[3].text is not None else "",
                                "capital": tds[4].text if tds[4].text is not None else "",
                                "amount_unpaid": tds[5].text if tds[5].text is not None else "",
                                "par_value": tds[6].text if tds[6].text is not None else ""
                            }]
                        })
                    if len(tds) == 5:
                        additional_detail.append({
                            "type": "shareholder_information",
                            "data": [{
                                "name": tds[1].text if tds[1].text is not None else "",
                                "number_of_share": tds[2].text if tds[2].text is not None else "",
                                "type_of_share": tds[3].text if tds[3].text is not None else "",
                                "currency": tds[4].text if tds[4].text is not None else "",
                            }]
                        })
    return additional_detail

def get_data(driver):
    item={}
    addresses_detail = []
    additional_detail = []
    people_detail = []
    fillings_detail = []
    data = get_page_tab_data(driver)
    item["name"] = data.get('Name:')
    item["file_number"] = data.get('File No.:')
    item["category"] = data.get('Category:')
    item["type"] = data.get('Type:')
    item["registration_date"] = data.get('Date Incorporated/Registered:').replace("/", "-") if data.get('Date Incorporated/Registered:') is not None else ""
    item["nature"] = data.get('Nature:')
    item["sub-category"] = data.get('Sub-category:')
    item["status"] = data.get('Status:')
    if data.get('Registered Office Address:') is not None and data.get('Registered Office Address:') != "":
        addresses_detail.append({
            "type": "office_address",
            "address": data.get('Registered Office Address:').replace("UNKNOWN", " ").replace("  ", " ")
        })
    additional_detail.extend(get_shares_information(driver))
    people_detail.extend(get_people_information(driver))
    fillings_detail.extend(get_fillings_information(driver))
    additional_detail.extend(get_winding_up_information(driver))
    people_detail.extend(get_people_details(driver))
    data = get_business_details(driver)
    item["registration_number"] = data.get("business_registration_no")
    item["industries"] = data.get("nature_of_business")
    if data.get("business_address") is not None and data.get("business_address") != "":
        addresses_detail.append({
            "type": "business_address",
            "address": data.get("business_address").replace("UNKNOWN", " ").replace("  ", " ")
        })
    additional_detail.extend(get_charges_information(driver))
    item["addresses_detail"] = addresses_detail
    item["additional_detail"] = additional_detail
    item["people_detail"] = people_detail
    item["fillings_detail"] = fillings_detail
    return item

def get_page_tab_data(driver):
    label_values_array = {}
    label_counts = {}
    label_elements = driver.find_elements(By.CLASS_NAME, 'label')
    value_elements = driver.find_elements(By.CLASS_NAME, 'value')
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

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 16
# 198104
end_number = 200
elements = ['C', 'P']
try:
    driver.get('https://onlinesearch.mns.mu/')
    driver.set_page_load_timeout(120)
    number = start_number
    for number in range(start_number,end_number):
        try:
            for element in elements:
                driver.refresh()
                wait = WebDriverWait(driver, 60) 
                print("Searching for:", element + str(number))
                search_field = wait.until(EC.presence_of_element_located((By.ID, 'company-partnership-text-field')))
                driver.execute_script("arguments[0].value = '';", search_field)
                search_field.send_keys(element + str(number))
                time.sleep(9)
                file_no_radio = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/cbris-header/div/div/form/div/div[1]/div[3]/div[2]/input')))
                file_no_radio.click()
                search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/cbris-header/div/div/form/div/div[2]/div[3]/div[2]/button')))
                search_button.click()
                time.sleep(30)
                # captcha_bypas(driver)
                # time.sleep(3)
                table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                trs = tbody.find_elements(By.TAG_NAME, 'tr')
                for tr in trs:
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    if len(tds) > 7:
                        eye_elements = tr.find_elements(By.TAG_NAME, 'fa-icon')
                        if eye_elements:
                            eye_elements[0].click()
                            time.sleep(30)
                            # captcha_bypas(driver)
                            DATA = get_data(driver)
                            print(DATA)
                            close_btn = driver.find_elements(By.CLASS_NAME, "dialog-close-button")
                            close_btn[0].click()
                            NAME = DATA.get('name').replace("%", "%%") if DATA.get('name') is not None else ""
                            ENTITY_ID = mauritius_crawler.generate_entity_id(company_name=NAME, reg_number=DATA.get('registration_number'))
                            BIRTH_INCORPORATION_DATE = ''
                            DATA = mauritius_crawler.prepare_data_object(DATA)
                            ROW = mauritius_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                            mauritius_crawler.insert_record(ROW)

        except Exception as e:
            tb = traceback.format_exc()
            # print(e,tb)
            close_btn = driver.find_elements(By.CLASS_NAME, "dialog-close-button")
            if len(close_btn) > 0:
                close_btn[0].click()
            print(f"retrying for C{str(number)}")

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    mauritius_crawler.db_log(log_data)           
