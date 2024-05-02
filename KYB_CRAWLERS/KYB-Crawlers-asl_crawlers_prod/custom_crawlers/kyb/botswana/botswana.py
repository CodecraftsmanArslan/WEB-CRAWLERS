import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import ssl
import undetected_chromedriver as uc
from CustomCrawler import CustomCrawler
from dateutil import parser

ssl._create_default_https_context = ssl._create_unverified_context

meta_data = {
    'SOURCE' :'Companies and Intellectual Property Authority (CIPA)',
    'COUNTRY' : 'Botswana',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.cipa.co.bw/ng-cipa-master/ui/XP-3EsoJZfyA6IBRBam7tJWYU_I4Izp_OoYEG07WZYYNzHI7NJOu8VUI1RCVNZkhnbRLCawlNIo-TAu37Vcxuct-c6XcjjLJOFOElWxQ4zzXrI-SS", 
                        "Source Description": "Description:The Companies and Intellectual Property Authority (CIPA) is a government agency in Botswana responsible for the administration and regulation of companies, intellectual property, and related matters within the country. CIPA plays a crucial role in facilitating business registration, promoting innovation, and protecting intellectual property rights."},
    'URL' : 'https://www.cipa.co.bw/ng-cipa-master/ui/XP-3EsoJZfyA6IBRBam7tJWYU_I4Izp_OoYEG07WZYYNzHI7NJOu8VUI1RCVNZkhnbRLCawlNIo-TAu37Vcxuct-c6XcjjLJOFOElWxQ4zzXrI-SS',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Botswana Official Registry"
}

botswana_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = botswana_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)
driver.set_page_load_timeout(120)

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str    

try:    
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_retries = 3
    for page_number in range(start, 30235):
        retries = 0
        while retries < max_retries:
            try:
                driver.get("https://www.cipa.co.bw/ng-cipa-master/ui/start/entitySearch")
                wait = WebDriverWait(driver, 10)
                search = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
                search.send_keys("0")
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.cat-btn.button.fill')))
                button.click()

                links = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH,'//div[@class="cat-box entity-search-result"]'))
                )

                for i, element in enumerate(links):
                    pagination_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'cat-pagination-pages'))
                    )
                    pagination_box = pagination_div.find_element(By.TAG_NAME, 'input')
                    pagination_box.clear()
                    pagination_box.send_keys(page_number)
                    pagination_box.send_keys(Keys.RETURN)

                    print(f"Page number: {page_number}")
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.XPATH,'//div[@class="cat-box entity-search-result"]'))
                    )
                    time.sleep(3)
                    name_btn = elements[i].find_element(By.CSS_SELECTOR, "span.simple")
                    name_ = name_btn.text
                    name_btn.click()

                    time.sleep(3)
                    link_data = {}
                    addresses_detail=[]
                    item={}
                    people_detail=[]
                    additional_detail=[]
                    filling_detail=[]
                    type_element = driver.find_elements(By.CLASS_NAME,'registration-type')
                    if len(type_element) > 0:
                        type_ = type_element[0].text
                    else:
                        type_ = ''
                    def get_key_value_pair(driver):
                        key_value_pair = {}
                        try:
                            dls = wait.until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cat-attribute-readonly-wrapper")))
                            for dl in dls:
                                if len(dl.find_elements(By.CSS_SELECTOR, "dt")) > 0:
                                    key = dl.find_element(By.CSS_SELECTOR, "dt").text
                                    value = dl.find_element(By.CSS_SELECTOR, "dd").text
                                    key_value_pair[key] = value
                        except Exception as e:
                            print(e)
                        return key_value_pair

                    def get_shareholding_information(driver):
                        additional_detail = []
                        data = []
                        table = driver.find_element(By.CLASS_NAME, 'table')
                        rows = table.find_elements(By.XPATH, '//tbody/tr')
                        for row in rows:
                            cells = row.find_elements(By.XPATH, './/td//fieldset//div//span[@class="value"]')
                            if len(cells) == 2:  # Ensure there are two cells (Number of Shares and Shareholder Name)
                                key_name = cells[0].text.strip()  # Strip any leading/trailing whitespace
                                value_number_of_shares = cells[1].text.strip()
                                data.append({'number of shares': key_name, 'name': value_number_of_shares})
                        if len(data) > 0:
                            additional_detail.append({
                                "type": "shareholding_information",
                                "data": data
                            })
                        return additional_detail

                    def extend_data(driver):
                        data={}
                        try:
                            company_name = driver.find_element(By.XPATH, '//dt[contains(text(), "Company Name")]/following-sibling::dd').text
                            registered_office_address = driver.find_element(By.XPATH, '//div[@class="cat-box" and @data-label="Registered Office Address"]//div[@class="cat-conditional-fields"]').text
                            representative_name=driver.find_element(By.XPATH, '//dt[contains(text(), "Representative Name")]/following-sibling::dd').text
                            rep_pos=driver.find_element(By.XPATH, '//dt[contains(text(), "Representative Postal Address")]/following-sibling::dd').text
                            postal_address = driver.find_element(By.XPATH, '//div[@class="cat-box" and @data-label="Postal Address"]//div[@class="cat-conditional-fields"]').text
                            appointment_date = driver.find_element(By.XPATH, '//dt[contains(text(), "Appointment Date")]/following-sibling::dd').text
                            data={
                                "company_name": company_name,
                                "registered_office_address": registered_office_address,
                                "representative_name":representative_name,
                                "representative_postal_address":rep_pos,
                                "postal_address": postal_address,
                                "appointment_date": format_date(appointment_date)
                            }
                        except:
                            pass
                        return data         
                    
                    name_element = wait.until( EC.presence_of_element_located((By.CLASS_NAME, "header-name")))
                    name = name_element.text if name_element is not None else ''
                    link_data["value"]=name
                    general = wait.until( EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'General Details')]")))
                    general_value=get_key_value_pair(driver)
                    link_data["general_value"]=general_value
                    if general_value.get('Business Activity') is not None and general_value.get('Business Activity') != "":
                        additional_detail.append({
                            'type': 'activities_information',
                            'data': [{
                                'name': general_value.get('Business Activity', ''),
                                'start_date': general_value.get('Date of Commencement of Business Activity', '')
                            }]
                        })

                    address = wait.until( EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Addresses')]")))
                    driver.execute_script("arguments[0].click();", address)
                    time.sleep(5)
                    address_key_value_pair = get_key_value_pair(driver)
                    data_= address_key_value_pair
                    if data_.get("Registered Office Address") is not None and data_.get("Registered Office Address") != "":
                        addresses_detail.append({
                            "type": "office_address",
                            "address": data_.get("Registered Office Address")
                        })
                    if data_.get("Postal Address") is not None and data_.get("Postal Address"):
                        addresses_detail.append({
                            "type": "postal_address",
                            "address": data_.get("Postal Address")
                        })
                    if data_.get("Principal Place of Business") is not None and data_.get("Principal Place of Business") != "":
                        addresses_detail.append({
                            "type": "general_address",
                            "address": data_.get("Principal Place of Business")
                        })

                    try:
                        proprietors_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Proprietors')]")))
                        driver.execute_script("arguments[0].click();", proprietors_element)
                        proprietors_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for index, proprietor_detail in enumerate(proprietors_detail):
                            driver.execute_script("arguments[0].click();", proprietor_detail)
                            names = driver.find_elements(By.XPATH, '//div[@class="cat-repeater-child-summary grid-x expanded"]')
                            name = names[index].find_element(By.XPATH, './/h4').text
                            proprietors_data = get_key_value_pair(driver)
                            people_detail.append({
                                "designation": "proprietor",
                                "name":name,
                                "nationality": proprietors_data.get("Nationality") if proprietors_data.get("Nationality") is not None else "",
                                "address": proprietors_data.get("Residential Address") if proprietors_data.get("Residential Address") is not None else "",
                                "postal_address": proprietors_data.get("Postal Address") if proprietors_data.get("Postal Address") is not None else "",
                                "appointement_date":proprietors_data.get("Appointment Date") if proprietors_data.get("Appointment Date") is not None else ""
                            })
                    except Exception as e:
                        pass

                    try:
                        members_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Members')]")))
                        driver.execute_script("arguments[0].click();", members_element)
                        members_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for index, member_detail in enumerate(members_detail):
                            driver.execute_script("arguments[0].click();", member_detail)
                            members_name = driver.find_elements(By.XPATH, '//div[@class="cat-repeater-child-summary grid-x expanded"]')
                            member_name = members_name[index].find_element(By.XPATH, './/h4').text
                            member_data = get_key_value_pair(driver)
                            if member_name is not None and member_name != "":
                                people_detail.append({
                                    "designation": "member",
                                    "name":member_name,
                                    "nationality": member_data.get("Nationality") if member_data.get("Nationality") is not None else "",
                                    "address": member_data.get("Residential Address") if member_data.get("Residential Address") is not None else "",
                                    "postal_address": member_data.get("Postal Address") if member_data.get("Postal Address") is not None else "",
                                    "appointement_date":member_data.get("Appointment Date") if member_data.get("Appointment Date") is not None else ""
                                })
                    except Exception as e:
                        pass
                        
                    try:
                        directors = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Directors')]")))
                        driver.execute_script("arguments[0].click();", directors)
                        directors_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for index, director_detail in enumerate(directors_detail):
                            driver.execute_script("arguments[0].click();", director_detail)
                            names = driver.find_elements(By.XPATH, '//div[@class="cat-repeater-child-summary grid-x expanded"]')
                            director_name = names[index].find_element(By.XPATH, './/h4').text
                            director_data = get_key_value_pair(driver)
                            meta_detail = {
                                "residential_address": director_data.get("Residential Address") if director_data.get("Residential Address") is not None else ""
                            }
                            if director_name is not None and director_name != "":
                                people_detail.append({
                                    "designation": "director",
                                    "name": director_name,
                                    "postal_address": director_data.get("Postal Address") if director_data.get("Postal Address") is not None else "",
                                    "appointment_date":format_date(director_data.get("Appointment Date")),
                                    "meta_detail": meta_detail,
                                    "nationality": director_data.get("Nationality") if director_data.get("Nationality") is not None else "",
                                })
                    except Exception as e:
                        pass

                    try:
                        secretaries = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Secretaries')]")))
                        driver.execute_script("arguments[0].click();", secretaries)
                        time.sleep(2)
                        secretaries_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for sec_detail in secretaries_detail:
                            time.sleep(2)
                            driver.execute_script("arguments[0].click();", sec_detail)
                            registered_office_address = driver.find_elements(By.XPATH, '//h3[contains(text(), "Registered Office Address")]/parent::div/following-sibling::div')
                            secretary_data = get_key_value_pair(driver)
                            if secretary_data.get("Company Name") is not None and secretary_data.get("Company Name") != "":
                                meta_detail = {
                                    "registered_office_address": registered_office_address[0].text if len(registered_office_address) > 0 else '',
                                    "representative_name": secretary_data.get("Representative Name") if secretary_data.get("Representative Name") is not None else "",
                                    "representative_postal_address": secretary_data.get("Representative Postal Address") if secretary_data.get("Representative Postal Address") is not None else "",
                                    "registration_number": secretary_data.get("UIN") if secretary_data.get("UIN") is not None else '',
                                }
                                people_detail.append({
                                    "designation": "secretary",
                                    "name": secretary_data.get("Company Name"),
                                    "nationality": secretary_data.get("Nationality") if secretary_data.get("Nationality") is not None else "",
                                    "address": secretary_data.get("Residential Address") if secretary_data.get("Residential Address") is not None else "",
                                    "postal_address": secretary_data.get("Postal Address") if secretary_data.get("Postal Address") is not None else "",
                                    "appointment_date": format_date(secretary_data.get("Appointment Date")),
                                    "meta_detail": meta_detail
                                })
                    except Exception as e:
                        pass

                    try:
                        auditors = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Auditors')]")))
                        driver.execute_script("arguments[0].click();", auditors)
                        auditors_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for index, auditor_detail in enumerate(auditors_detail):
                            driver.execute_script("arguments[0].click();", auditor_detail)
                            names = driver.find_elements(By.XPATH, '//div[@class="cat-repeater-child-summary grid-x expanded"]')
                            auditor_name = names[index].find_element(By.XPATH, './/h4').text
                            auditor_data = get_key_value_pair(driver)
                            if auditor_name is not None and auditor_name != '':
                                meta_detail = {
                                    "residential_address": auditor_data.get("Residential Address") if auditor_data.get("Residential Address") is not None else '',
                                    "nominee_shareholder": auditor_data.get("Nominee shareholder") if auditor_data.get("Nominee shareholder") is not None else ''
                                }
                                people_detail.append({
                                    "designation": "auditor",
                                    "name": auditor_name,
                                    "nationality": auditor_data.get("Nationality") if auditor_data.get("Nationality") is not None else '',
                                    "postal_address": auditor_data.get("Postal Address") if auditor_data.get("Postal Address") is not None else '',
                                    "meta_detail": meta_detail,
                                    "appointment_date": format_date(auditor_data.get("Appointment Date"))
                                })
                    except Exception as e:
                        pass

                    try:
                        shareholders = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Shareholders')]")))
                        driver.execute_script("arguments[0].click();", shareholders)
                        shareholders_detail = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="repeater-body"]//button[@aria-label="Show more"]')))
                        for index, shareholder_detail in enumerate(shareholders_detail):
                            driver.execute_script("arguments[0].click();", shareholder_detail)
                            shareholders_name = driver.find_elements(By.XPATH, '//div[@class="cat-repeater-child-summary grid-x expanded"]')
                            shareholder_name = shareholders_name[index].find_element(By.XPATH, './/h4').text
                            shareholder_data = get_key_value_pair(driver)
                            meta_detail = {
                                "residential_address": shareholder_data.get("Residential Address") if shareholder_data.get("Residential Address") is not None else "",
                                "nominee_shareholder": shareholder_data.get("Nominee shareholder") if shareholder_data.get("Nominee shareholder") is not None else ""
                            }
                            people_detail.append({
                                "designation": "shareholders",
                                "name": shareholder_name,
                                "nationality": shareholder_data.get("Nationality") if shareholder_data.get("Nationality") is not None else '',
                                "postal_address": shareholder_data.get("Postal Address") if shareholder_data.get("Postal Address") is not None else '',
                                "appointment_date": format_date(shareholder_data.get("Appointment Date"))
                            })
                            
                    except Exception as e:
                        pass

                    try:
                        share_allocations = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Share Allocations')]")))
                        driver.execute_script("arguments[0].click();", share_allocations)
                        time.sleep(5)
                        additional_detail = []
                        allo_type=driver.find_element(By.XPATH,"//dt[contains(text(), 'Share allocation type')]/following-sibling::dd").text
                        total_share=driver.find_element(By.XPATH,"//dt[contains(text(), 'Total number of shares')]/following-sibling::dd").text
                        additional_detail.extend(get_shareholding_information(driver))
                        if allo_type != "" or total_share != "":
                            additional_detail.append({
                                'type': 'shares_information',
                                'data': [{
                                    "allocation_type": allo_type,
                                    "total_number_of_shares": total_share,
                                }]   
                            })
                    except Exception as e:
                        pass

                    filling = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Filings')]")))
                    driver.execute_script("arguments[0].click();", filling)
                    elements =wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='grid-x flex-align-top pt']")))   
                    for element in elements:
                        name_element = element.find_element(By.XPATH, ".//button[@class='simple pn text-align-left cell auto mrs word-wrap']")
                        date_element = element.find_element(By.XPATH, ".//div[@class='cell large-4 pls text-size-medium']")
                        name = name_element.text
                        date = date_element.text.replace("Registered Date ", "")
                        filling_detail.append({
                            "title": name,
                            "date": format_date(date)
                        })

                    basic_info = link_data["general_value"]
                    item['name'] = name_
                    item['type'] = type_
                    item['registration_number'] = basic_info.get('UIN', '') if basic_info.get('UIN', '') is not None else ''
                    item['status'] = basic_info.get('Company Status', '') if basic_info.get('Company Status', '') is not None else ''
                    item['foreign_company'] = basic_info.get('Foreign Company', '') if basic_info.get('Foreign Company', '') is not None else ''
                    item['exempt'] = basic_info.get('Exempt', '') if basic_info.get('Exempt', '') is not None else ''
                    item['incorporation_date'] = format_date(basic_info.get('Incorporation Date'))
                    item['re_registration_date'] = basic_info.get('Re-Registration Date', '') if basic_info.get('Re-Registration Date', '') is not None else ''
                    item['have_own_constitution'] = basic_info.get('Have own constitution', '') if basic_info.get('Have own constitution', '') is not None else ''
                    item['annual_return_filing_month'] = basic_info.get('Annual Return Filing Month', '') if basic_info.get('Annual Return Filing Month', '') is not None else ''
                    item['annual_return_last_filed_on'] = basic_info.get('Annual Return last filed on', '') if basic_info.get('Annual Return last filed on', '') is not None else ''
                    item['renewal_filing_month'] = basic_info.get('Renewal Filing Month', '') if basic_info.get('Renewal Filing Month', '') is not None else ''
                    item['inactive_date'] = basic_info.get('The latest date against the last updated status') if basic_info.get('The latest date against the last updated status') is not None else ''
                    item["addresses_detail"]=addresses_detail
                    item["people_detail"]=people_detail
                    item["additional_detail"]=additional_detail
                    item["fillings_detail"]=filling_detail
                    OBJ =  botswana_crawler.prepare_data_object(item)
                    ENTITY_ID = botswana_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
                    NAME = OBJ['name'].replace("%","%%")
                    BIRTH_INCORPORATION_DATE = ""
                    ROW = botswana_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                    botswana_crawler.insert_record(ROW)
                    driver.back()
            except TimeoutException:
                print(f"Timeout exception occurred on page {page_number}. Retrying...")
                retries += 1
                continue
            break


    log_data = {"status": 'success',
                        "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    botswana_crawler.db_log(log_data)
    botswana_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    botswana_crawler.db_log(log_data)


