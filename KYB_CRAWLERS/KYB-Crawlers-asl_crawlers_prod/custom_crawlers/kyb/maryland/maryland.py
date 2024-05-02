"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains



meta_data = {
    'SOURCE' :'Department of Assessments and Taxation',
    'COUNTRY' : 'Maryland',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://egov.maryland.gov/BusinessExpress/EntitySearch", 
                        "Source Description": "The Maryla​​​nd Department of Assessments and Taxation is a custome​r-focused agency that works to ensure the property is accurately​ assessed, business records are appropriately​maintained, and necessary tax-related information is conveyed to state agencies and local jurisdictions. The Department's responsibilities can generally be split into three main areas: Business Services, Real Property Valuation, and Property Tax Credits."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://egov.maryland.gov/BusinessExpress/EntitySearch'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Maryland Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

maryland_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = maryland_crawler.get_selenium_helper()
request_helper = maryland_crawler.get_requests_helper()

driver = selenium_helper.create_driver(headless=True, Nopecha=True)
action = ActionChains(driver=driver)

driver.get('https://egov.maryland.gov/BusinessExpress/EntitySearch')
time.sleep(3)
DATA_SIZE = len(driver.page_source)

def wait_for_captcha_to_be_solved(browser):
    try:
        iframe_element = browser.find_element(By.XPATH, '//iframe[@title="recaptcha challenge expires in two minutes"]')
        browser.switch_to.frame(iframe_element)
        time.sleep(1)
        captcha_element = driver.find_element(By.ID, "rc-imageselect")
        captcha_not_solved = True
        if captcha_element:
            print("Captcha Found!")
            print('trying to resolve captcha...')
        while captcha_element and captcha_not_solved:
            captcha_element_ = driver.find_element(By.ID, "rc-imageselect")
            if captcha_element_:
                print("Still Trying...")
                time.sleep(3)
            else:
                captcha_not_solved = False
            browser.switch_to.default_content()
            print("Captcha has been Solved!")
            time.sleep(2)
        else:
            print("No Captcha Found")
            browser.switch_to.default_content()
    except Exception as e:
        browser.switch_to.default_content()
        print("Captcha not found.")

alphabets = ["W", "F", "T", "M", "Z", "D", "T", "L"]

if len(ARGUMENT) > 1:
    start_letter = ARGUMENT[1]
else:
    start_letter = alphabets[0]

if len(ARGUMENT) > 2:
    start_alph_number = int(ARGUMENT[2])
else:
    start_alph_number = 0

if len(ARGUMENT) > 3:
    start_number = int(ARGUMENT[3])
else:
    start_number = 0

def crawl():
    for letter in alphabets:
        if len(ARGUMENT) > 1:
            if letter != ARGUMENT[1]:
                continue
        for i in range(start_alph_number, 3):
            for numb in range(start_number, 10000000):
                number = str(numb).zfill(7)
                s_number = letter + str(i) + str(number)
                print(s_number)
                search_number =  driver.find_element(By.ID, 'BusinessName')
                search_number.send_keys(s_number)
                time.sleep(1)

                search_type = driver.find_element(By.XPATH,'//input[@value="DepartmentId"]')
                action.move_to_element(search_type).click().perform()

                search_button = driver.find_element(By.XPATH, '//button[@id="searchBus1"]')
                driver.execute_script("arguments[0].click();", search_button)

                time.sleep(10)

                wait_for_captcha_to_be_solved(driver)

                try:
                    company_link = driver.find_element(By.XPATH, '//td[@data-title="Business Name"]/a')
                    driver.execute_script("arguments[0].click();", company_link)
                    time.sleep(5)
                except NoSuchElementException:
                    print(f"No record found for: {s_number}.")
                    driver.get('https://egov.maryland.gov/BusinessExpress/EntitySearch')
                    time.sleep(5)
                    continue

                wait_for_captcha_to_be_solved(driver)

                driver.switch_to.window(driver.window_handles[1])  

                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')

                name_number = soup.find('div',class_ = 'legendStyle').get_text(strip=True)
                name_numbers = name_number.split(':')
                NAME = name_numbers[0].strip()
                REGISTRANTION_NUMBER = name_numbers[1].strip()
                form_items = soup.find_all(class_='fp_formItem')
                data_dict = {}
                for item in form_items:
                    label = item.find(class_='fp_formItemLabel')
                    data = item.find(class_='fp_formItemData')
                    if label and data:
                        label_text = label.strong.get_text(strip=True)
                        data_text = data.get_text(strip=True)
                        data_dict[label_text] = data_text

                # Get all filing history
                filing = driver.find_element(By.XPATH,'/html/body/div[3]/section/div[2]/div/ul/li[2]')
                filing.click()
                time.sleep(2)

                filliings_detail = []
                filling_table = driver.find_element(By.ID,'tblFilingHistory')
                filling_rows = filling_table.find_elements(By.TAG_NAME,'tr')
                for filing_row in filling_rows[2:]:
                    filing_cells = filing_row.find_elements(By.TAG_NAME,'td')
                    title = filing_cells[0].text.strip()
                    try:
                        file_url = filing_cells[0].find_element(By.TAG_NAME,'a').get_attribute('href')
                    except:
                        file_url = ""
                    date = filing_cells[1].text.strip()
                    film = filing_cells[2].text.strip()
                    folio = filing_cells[3].text.strip()
                    filliings_dict = {
                        "title":title,
                        "file_url":file_url,
                        "date":date.split(" ")[0].replace('/','-'),
                        "meta_detail":{
                        "film":film,
                        "folio":folio
                        }
                    }
                    filliings_detail.append(filliings_dict)

                pattern = r"([A-Z ]+)(\d+.*)"

                people_detail = []
                try:
                    if data_dict.get('Resident Agent:',''):
                        matches = re.match(pattern, data_dict.get('Resident Agent:',''))
                        if matches:
                            designation = 'registered_agent'
                            name = matches.group(1)
                            address = matches.group(2)
                            people_dict = {
                                    "designation":designation,
                                    "name":name,
                                    "address":address.strip()
                                    }
                            people_detail.append(people_dict)

                    if data_dict.get('Owner:',''):
                        new_pattern_ = r"([A-Z ]+)(\d+.*)"
                        matches_ = re.match(new_pattern_, data_dict.get('Owner:',''))
                        if matches_:
                            designation_ = 'owner'
                            name_ = matches_.group(1)
                            address_ = matches_.group(2)
                            people_dict_ = {
                                    "designation":designation_,
                                    "name":name_,
                                    "address":address_.strip()
                                    }
                            people_detail.append(people_dict_)

                except Exception as e:
                    people_detail = []

                mailing_addresses = ""
                #get annual reports
                try:
                    annual_report = driver.find_element(By.XPATH,'/html/body/div[3]/section/div[2]/div/ul/li[3]')
                    annual_report.click()
                    time.sleep(5)
                    try:
                        mailing_address = driver.find_element(By.XPATH,'/html/body/div[3]/section/div[2]/div/span/div[1]/div[4]/div/div[1]/div[2]').text.strip() 
                        mailing_addresses = mailing_address.split("\n")[2]+' '+mailing_address.split("\n")[-1]
                    except:
                        mailing_addresses = ""
                    
                    annual_table = driver.find_element(By.ID,'tblPersProperty1')
                    # driver.execute_script("arguments[0].scrollIntoView();", annual_table)
                    annual_rows = annual_table.find_elements(By.TAG_NAME,'tr')
                    for annual_row in annual_rows[1:]:
                        annual_cells = annual_row.find_elements(By.TAG_NAME,'td')
                        year = annual_cells[0].text.strip()
                        date_field = annual_cells[1].text.strip()
                        extension = annual_cells[2].text.strip()
                        penalty_amount = annual_cells[3].text.strip()
                        penalty_clearing_date = annual_cells[4].text.strip()
                        annual_dict = {
                            "year":year,
                            "date":date_field.replace('/','-'),
                            "meta_detail":{
                                "extension":extension,
                                "penalty_amount":penalty_amount,
                                "penalty_clearing_date":penalty_clearing_date
                            }
                        }
                        filliings_detail.append(annual_dict) 
                    
                    
                    personal_table = driver.find_element(By.ID,'tblPersProperty2')
                    personal_rows = personal_table.find_elements(By.TAG_NAME,'tr')
                    for personal_row in personal_rows[1:]:
                        personal_cells = personal_row.find_elements(By.TAG_NAME,'td')
                        year_ = personal_cells[0].text.strip()
                        county_base = personal_cells[1].text.strip()
                        town_base = personal_cells[2].text.strip()
                        date_ = personal_cells[3].text.strip()
                        personal_dict = {
                            "year":year_,
                            "date":date_.replace('/','-'),
                            "meta_detail":{
                                "county_base":county_base,
                                "town_base":town_base
                            }
                        }
                        filliings_detail.append(personal_dict)
                except Exception as e:
                    personal_dict = {}
                    annual_dict = {}
                    filliings_detail.append(annual_dict)
                    filliings_detail.append(personal_dict)


                new_pattern = r'^(.*?)\s?(\d+\s[A-Z]+[A-Z\s]+\d{5})$'
                location_match = re.match(new_pattern, data_dict.get('Location:',''))
                location = ""
                try:
                    if location_match:
                        location = location_match.group(2)
                except:
                    location = ""

                OBJ = {
                    "name":NAME,
                    "registration_number":REGISTRANTION_NUMBER,
                    "addresses_detail":[
                        {
                            "type":'principal_office_address',
                            "address":data_dict.get('Principal Office:','')
                        },
                        {
                            "type":'general_address',
                            "address":location.strip()
                        },
                        {
                            "type":"mailing_address",
                            "address":mailing_addresses
                        }
                    ],
                    "registration_date":data_dict.get('Date of Formation/ Registration:','').replace('/',"-"),
                    "type":data_dict.get('Business Type:',''),
                    "status":data_dict.get('Status:',''),
                    "standing":data_dict.get('Good Standing:',''),
                    "industries":data_dict.get('Business Code:',''),
                    "jurisdiction_code":data_dict.get('State of Formation:',''),
                    "structure_status":data_dict.get('Stock Status:','').replace('N/A',""),
                    "close_status":data_dict.get('Close Status:','').replace('N/A',""),
                    "expiration_date":data_dict.get('Expiration Date:',"").replace('/',"-"),
                    "people_detail":people_detail,
                    "fillings_detail":filliings_detail,
                }

                OBJ = maryland_crawler.prepare_data_object(OBJ)
                ENTITY_ID = maryland_crawler.generate_entity_id(OBJ['registration_number'],OBJ['name'])
                BIRTH_INCORPORATION_DATE = ''
                ROW = maryland_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
                maryland_crawler.insert_record(ROW)

                driver.close()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
                driver.get('https://egov.maryland.gov/BusinessExpress/EntitySearch')
                time.sleep(5)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    maryland_crawler.db_log(log_data)
    maryland_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    maryland_crawler.db_log(log_data)