"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from pyvirtualdisplay import Display
import requests


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Nebraska Secretary of State, Business Services Division',
    'COUNTRY': 'Nebraska',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.nebraska.gov/sos/corp/corpsearch.cgi",
                      "Source Description": "The Business Services Division provides several important functions for the business community. Registrations are recorded for corporations, limited liability companies, limited partnerships, limited liability partnerships, trade names and trademarks. The division handles Uniform Commercial Code and other security interest records. The division also regulates notary public commissions and handles apostilles and authentications (documents going to other countries)."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.nebraska.gov/sos/corp/corpsearch.cgi'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Nebraska  Official Registry",
}


display = Display(visible=0, size=(800, 600))
display.start()


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0000000

def get_range(start_num):
    if start_num == 0:
        for i in range(100000000):
            yield f"{i:7d}"
        for i in range(1000000000, 2600000000):
            yield f"{i:10d}"

    else:
        if 0 < start_num < 100000000:
            for i in range(start_num, 100000000):
                yield f"{i:7d}"

        elif 1000000000 <= start_num < 2600000000:
            for i in range(start_num, 2600000000):
                yield f"{i:10d}"


        

def wait_for_captcha_to_be_solved(browser):
            time.sleep(5)
            if len(browser.find_elements(By.XPATH, '//iframe[@title="reCAPTCHA"]')) > 0:
                while True:
                    try:
                        iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                        browser.switch_to.frame(iframe_element)
                        wait = WebDriverWait(browser, 10000)
                        print('trying to resolve captcha')
                        wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'recaptcha-checkbox-checked')))
                        print("Captcha has been Solved")
                        # Switch back to the default content
                        browser.switch_to.default_content()
                        return browser
                    except:
                        print('captcha solution timeout error, retrying...') 

Nebraska_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = Nebraska_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=True)
driver.get("https://www.nebraska.gov/sos/corp/corpsearch.cgi")

file_numbers = get_range(start_num)
try:
    for file_number in file_numbers:
        
        click_on_button=driver.find_element(By.XPATH, '//input[@value="num_search"]')
        click_on_button.click()

        time.sleep(5)
        name_input=driver.find_element(By.CSS_SELECTOR,'input[id="acct-num"]')
        name_input.clear() 
        name_input.send_keys(str(file_number)) 
        print("enter_input", file_number)



        wait_for_captcha_to_be_solved(driver)

        perfom_action=driver.find_element(By.CSS_SELECTOR,'button[id="submit"]')
        perfom_action.click()
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            addresses_detail = []  # Changed this to a list for multiple address types
            people_detail = []
            announcements_detail=[] 
            fillings_detail=[]
            additional_detail=[]    # Changed this to a list for multiple people details
            def extract_address(soup, title):
                address_title = soup.find('div', class_='bold', string=title)
                if address_title:
                    address_div = address_title.find_parent()
                    address_elements = address_div.find_all(['br', 'p'])
                    address_text = ""

                            # Include the text before the first line (if available)
                    preceding_text = address_title.find_next_sibling(text=True)
                    if preceding_text:
                        address_text += preceding_text.strip() + "\n"

                    for element in address_elements:
                        sibling_text = element.find_next_sibling(text=True)
                        if sibling_text is not None:
                            address_text += sibling_text.strip() + "\n"

                    return address_text.strip()
                return None

            def extract_details(soup):
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) < 2:
                        continue  # Skip tables with fewer than two rows

                    header_cells = rows[0].find_all(['th', 'td'])
                    header_texts = [cell.get_text(strip=True) for cell in header_cells]

                    if 'Document' in header_texts and 'Date Filed' in header_texts :
                        # This table appears to be for document details
                        for row in rows[1:]:
                            columns = row.find_all(['th', 'td'])
                            document_name = columns[1].get_text(strip=True)
                            date_filed = columns[2].get_text(strip=True)
                            fillings_detail.append({'date': date_filed,'title': document_name})
                    elif 'Corporation Position' in header_texts and 'Name' in header_texts and 'Address' in header_texts:
                        # This table appears to be for corporation position details
                        for row in rows[1:]:
                            columns = row.find_all(['th', 'td'])
                            corporation_position = columns[0].get_text(strip=True)
                            Name = re.sub(r'\s+', ' ', columns[1].get_text(strip=True))
                            Address = columns[2].get_text(strip=True)
                            people_detail.append({'designation': corporation_position, "name": Name, "address": Address})
                            
                    elif 'Account Number' in header_texts and 'Name' in header_texts and 'Type' in header_texts and 'Status' in header_texts:
                        # This table appears to be for corporation position details
                        for row in rows[1:]:
                            columns = row.find_all(['th', 'td'])
                            Account_Number = columns[0].get_text(strip=True)
                            Name = columns[1].get_text(strip=True)
                            Type = columns[2].get_text(strip=True)
                            Status = columns[3].get_text(strip=True)
                            if Account_Number: 
                                additional_detail.append({
                                    'type': "associated_entities_info",
                                    'data': [
                                        {
                                            'registration_number': Account_Number,
                                            'name': Name,
                                            'type': Type,
                                            'status': Status
                                        }
                                    ]
                                    })

                return fillings_detail, people_detail , additional_detail

            organization_name=''
            organization_name = soup.find('h4')
            if organization_name:
                organization_name_value=organization_name.text.strip()


            account_Number = soup.find('div', string="SOS Account Number")
            if account_Number:
                account_Number_text = account_Number.find_next_sibling(string=True).strip()  

            status_element = soup.find('div', string="Status")
            if status_element:
                status_text = status_element.find_next_sibling(string=True).strip()


            contact_address_text = extract_address(soup, 'Contact')

            nature_of_business = soup.find('div', string="Nature of Business")
            nature_of_business_text = nature_of_business.find_next_sibling(tstringext=True) if nature_of_business else ""

            entity_type = soup.find('div', string="Entity Type")
            entity_type_text = entity_type.find_next_sibling(string=True).strip() if entity_type else ""

            date_filed = soup.find('div', string="Date Filed")
            date_filed_text = date_filed.find_next_sibling(string=True).strip() if date_filed else ""


            expiration = soup.find('div', string="Expiration Date")
            expiration_text = expiration.find_next_sibling(string=True).strip() if expiration else ""


            next_report_due_date = soup.find('div', string="Next Report Due Date")
            next_report_due_date_text = next_report_due_date.find_next_sibling(string=True).strip() if next_report_due_date else ""

            description = soup.find('div', string="Professional Action")
            description_text = description.find_next_sibling(string=True).strip() if description else ""
            if description_text:
                announcements_detail.append({
                    'description':description
                })

            nonprofit_type = soup.find('div', string="Nonprofit Type")
            nonprofit_type_element = nonprofit_type.find_next_sibling(string=True).strip() if nonprofit_type else ""

            members = soup.find('div', string="Has Members")
            members_element = members.find_next_sibling(string=True).strip() if members else ""


            principal_address_text = extract_address(soup, 'Principal Office Address')
            if principal_address_text:
                addresses_detail.append({
                    "type": "principal_address",
                    "address":principal_address_text.replace("\n","")

                })


            registered_address_text = extract_address(soup, 'Registered Agent and Office Address')
            if registered_address_text:
                    address_lines = registered_address_text.split('\n')
                    name = address_lines[0]
                    address_lines = address_lines[1:]  # Remove the name from the address lines

                    people_detail.append({
                        "designation": "registered_agent",
                        "name": name.strip(),
                        "address": ' '.join(address_lines).replace("\n", " ").strip()
                    })
                

            designated_address_text = extract_address(soup, 'Designated Office Address')
            if designated_address_text:
                addresses_detail.append({
                    "type": "designated_address",
                    "address":designated_address_text.replace("\n","")

                })

            contact_address_text = extract_address(soup, 'Contact')
            if contact_address_text:
                people_detail.append({
                    "designation": "contact_person",
                    "address":contact_address_text.replace("\n","")

                })
                

            fillings_detail, people_detail ,additional_detail = extract_details(soup)

            OBJ = {
                "name": organization_name_value,
                "registration_number": account_Number_text,
                "status": status_text,
                "nature_of_business": nature_of_business_text,
                "type": entity_type_text,
                "expiration_date":expiration_text,
                "date_filed": date_filed_text,
                "next_report_due_date": next_report_due_date_text,
                "non_profit_type":nonprofit_type_element,
                "has_members":members_element,
                "announcements_detail":announcements_detail,
                "fillings_detail": fillings_detail,
                "addresses_detail":addresses_detail,
                "people_detail": people_detail,
                "additional_detail":additional_detail
            }
            OBJ =  Nebraska_crawler.prepare_data_object(OBJ)
            ENTITY_ID = Nebraska_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = ""
            ROW = Nebraska_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            Nebraska_crawler.insert_record(ROW)
        except:
            print("data not found")


        time.sleep(2)
        id_search=driver.find_element(By.CSS_SELECTOR,'li[id="newSearchNav"]')
        id_search.click()

    Nebraska_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Nebraska_crawler.db_log(log_data)
 

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Nebraska_crawler.db_log(log_data)

display.stop()
