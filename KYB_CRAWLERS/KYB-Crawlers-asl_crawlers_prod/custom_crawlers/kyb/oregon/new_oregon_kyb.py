"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import json, pytesseract
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from selenium.common.exceptions import TimeoutException
import base64
from PIL import Image
import pytesseract
import io
from io import BytesIO
import nopecha 
import undetected_chromedriver as uc 

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

nopecha.api_key = ENV.get('NOPECHA_KEY')

meta_data = {
    'SOURCE' :'Oregon Secretary of State, Corporation Division',
    'COUNTRY' : 'Oregon',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://egov.sos.state.or.us/br/pkg_web_name_srch_inq.login", 
                        "Source Description": "The dataset includes information on active and inactive businesses registered with the Oregon Secretary of State's Corporation Division. It includes the business name, registry number, registration date, and whether the business is active or inactive."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://egov.sos.state.or.us/br/pkg_web_name_srch_inq.login'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Oregon",
}

display = Display(visible=0,size=(800,600))
display.start()
oregon_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
# selenium_helper = oregon_crawler.get_selenium_helper()
# driver = selenium_helper.create_driver(headless=False,Nopecha=False)
request_helper = oregon_crawler.get_requests_helper()
driver = uc.Chrome(version_main = 114, headless=False) 


def identify_captcha(browser):
    while True:
        time.sleep(10)
        if len(browser.find_elements(By.TAG_NAME, "audio")) > 0:
            img_element = driver.find_element(By.XPATH, '//img[@alt="Red dot"]')
            src_attribute = img_element.get_attribute("src")
            captch_text = base64_to_text(src_attribute)
            text_field = browser.find_element(By.ID, "ans")
            text_field.send_keys(captch_text)
            submit_button = browser.find_element(By.ID, "jar")
            submit_button.click()
        else:
            break

def base64_to_text(base64_image):
    base64_data = base64_image.split(",")[1]
    try:
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        image.save('captcha.png')
        with open('captcha.png', 'rb') as image_file:
            image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')

        captcha_text = nopecha.Recognition.solve(
            type='textcaptcha',
            image_urls=[image_64_encode],
        )  
        print("Captcha text: ", captcha_text)
        return captcha_text
    except Exception as e:
        print(f"Error: {e}")


# def get_image_text(url):
#     response = request_helper.make_request(url)
#     image = Image.open(BytesIO(response.content))
#     text = pytesseract.image_to_string(image)
#     return text


def store_registry_ids():
    DATA = []
    i = 100000
    j = 0
    while True:
        api_url = f"https://data.oregon.gov/api/id/tckn-sxa6.json?$select=`registry_number`,`business_name`,`entity_type`,`registry_date`,`associated_name_type`,`first_name`,`middle_name`,`last_name`,`suffix`,`not_of_record_entity`,`entity_of_record_reg_number`,`entity_of_record_name`,`address`,`address_continued`,`city`,`state`,`zip`,`jurisdiction`,`business_details`&$order=`:id`+ASC&$limit={i}&$offset={j}"
        response = request_helper.make_request(api_url, timeout=120)
        json_data = json.loads(response.text)
        if len(json_data) == 0:
            break
        registry_numbers = [item["registry_number"] for item in json_data]
        DATA.extend(registry_numbers)
        print('Record inserted into data: ', len(DATA))
        j += 100000
    with open('registry_numbers.json', 'w') as file:
        json.dump(DATA, file)
    print('Total records: ', len(DATA))


def get_registry_ids():
    with open('registry_numbers.json', 'r') as file:
        loaded_data = json.load(file)
    # Remove duplicates
    unique_list = list(set(loaded_data))
    unique_list = list(map(str, unique_list))
    return unique_list


def find_next_td_text(soup, text):
    td = soup.find('td', string=text)
    if td:
        next_td = td.find_next('td')
        if next_td:
            return next_td.get_text(strip=True)
    return ""


def get_table_data(soup, keyword):
    td_element = soup.find('td', string=lambda text: keyword in text if text is not None else "")
    if td_element:
        table = td_element.find_parent('table')
        if table is not None:
            data_list = []
            headers = [header.text.strip() for header in table.find_all('td', bgcolor="#7a7a7a")]
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                values = [cell.text.strip() for cell in cells]
                anchor = cells[0].find('a')
                if anchor:
                    href = anchor['href']
                    values[0] = href
                data_dict = dict(zip(headers, values))
                data_list.append(data_dict)
        return data_list
    return []

def get_tables_row_data(table):
    data = {}  # Initialize an empty dictionary
    current_key = None
    td_elements = table.find_all('td')
    for td in td_elements:
        if 'bgcolor="#7a7a7a"' in str(td):
            current_key = td.text.strip()
        else:
            if current_key:
                if current_key in data:
                    # If current_key already exists in data, append the value with a comma
                    data[current_key] += ', ' + td.text.strip()
                else:
                    # If current_key doesn't exist, create a new entry in data
                    data[current_key] = td.text.strip()
    return data

# def get_tables_data(table):
#     data_dict = []
#     current_key = None
#     td_elements = table.find_all('td')
#     for td in td_elements:
#         if 'bgcolor="#7a7a7a"' in str(td):
#             current_key = td.text.strip()
#         else:
#             if current_key:
#                 data.append({current_key: td.text.strip()})
#     return data

def get_all_tables(soup):
    tables = []
    target_texts = ["Type", "Name", "Addr 1", "Addr 2", "CSZ", "Of Record"]
    all_tables = soup.find_all('table')
    for table in all_tables:
        td_elements = table.find_all('td')
        td_texts = [td.get_text(strip=True) for td in td_elements]
        if any(text in target_texts for text in td_texts):
            tables.append(table)
    return tables

def get_page_data(soup):
    
    arr = []
    key_values = {}
    for table in get_all_tables(soup):
        res = get_tables_row_data(table)
        for key, value in res.items():
            if 'Type' == key and len(key_values) > 0:
                arr.append(key_values)
                key_values = {}
            key_values[key] = value
    if key_values:
        arr.append(key_values)

    result = {}
    additional_detail = []
    previous_names_detail = []
    fillings_detail = []
    people_detail = []
    addresses_detail = []
    for item in get_table_data(soup, 'Business Entity Name'):
        meta_detail = {
            'type': item.get('Name Type'),
            'status': item.get('Name Status'),
            'start_date':item.get('Start Date'),
            'end_date': item.get('End Date')
        }
        meta_detail = {k: v for k, v in meta_detail.items() if v}
        previous_names_detail.append({
            'name': item.get('Business Entity Name'),
            'meta_detail': meta_detail
        })
    for item in get_table_data(soup, 'Image Available'):
        meta_detail = {
            "transaction_date": item.get("Transaction Date"),
            "effective_date": item.get("Effective Date"),
            "status": item.get("Status"),
            "name/agent_change": item.get("Name/Agent Change"),
            "dissolved_by": item.get("Dissolved By")
        }
        meta_detail = {k: v for k, v in meta_detail.items() if v}
        fillings_detail.append({
            "file_url": item.get("Image Available"),
            "title": item.get("Action"),
            "meta_detail": meta_detail
        })

    counties_filing_information = get_table_data(soup, 'Counties Filed')
    if counties_filing_information is not None:
        counties_filing_information = [item for item in counties_filing_information if item['Counties Filed'] != '' and item['Counties Filed'] is not None]
        if len(counties_filing_information) == 3:
            counties_filed = ''
            counties_not_filed = ''
            counties_filed = counties_filing_information[0]['Counties Filed']
            if 'Counties Not Filed' in counties_filing_information[1]['Counties Filed']:
                counties_not_filed = counties_filing_information[2]['Counties Filed']
            if counties_filed != "":
                additional_detail.append({
                    "type": "counties_filing_information",
                    "data": [{
                        "counties_filed": counties_filed,
                        "counties_not_filed": counties_not_filed
                    }]
                })
    basic_info = get_table_data(soup, 'Registry Nbr')
    if len(basic_info) > 0:
        result["registration_number"] = basic_info[0].get('Registry Nbr')
        result["type"] = basic_info[0].get('Entity Type')
        result["status"] = basic_info[0].get('Entity Status')
        result["jurisdiction"] = basic_info[0].get('Jurisdiction')
        result["registartion_date"] = basic_info[0].get('Registry Date')
        result["renewal_date"] = basic_info[0].get('Next Renewal Date')
        result["renewal_due"] = basic_info[0].get('Renewal Due?')

    for obj in arr:
        if 'Principal Source of Business' in obj.get('Type') or 'PRINCIPAL PLACE OF BUSINESS' in obj.get('Type'):
            principle_address = f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}"
            if principle_address.replace(",", "").replace(" ", "") != "":
                addresses_detail.append({
                    "type": "principal_address",
                    "address": principle_address.replace(", , ", ",")
                })
        elif 'MAILING ADDRESS' in obj.get('Type'):
            mailing_address = f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}"
            if mailing_address.replace(",", "").replace(" ", ""):
                addresses_detail.append({
                    "type": "mailing_address",
                    "address": mailing_address.replace(", , ", ",")
                })
        elif 'REGISTERED AGENT' in obj.get('Type'):
            meta_detail = {
                "start_date": obj.get('Start Date'),
                "resign_date": obj.get('Resign Date'),
                'number': obj.get('Of Record').split(", ")[0] if 'Of Record' in obj and ',' in obj.get('Of Record') and len(obj.get('Of Record').split(", ")) > 1 else ""
            }
            meta_detail = {k: v for k, v in meta_detail.items() if v}
            name = obj.get('Of Record').split(", ")[1] if 'Of Record' in obj and ',' in obj.get('Of Record') and len(obj.get('Of Record').split(", ")) > 1 else ""
            people_detail.append({
                "name": name if name != "" else obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                "designation": "registered_agent",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            }) 
        elif 'PRESIDENT' in obj.get('Type'):
            meta_detail = {
                "resign_date": obj.get('Resign Date')
            }
            meta_detail = {k: v for k, v in meta_detail.items() if v}
            people_detail.append({
                "name": obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                "designation": "president",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            }) 
        elif 'SECRETARY' in obj.get('Type'):
            meta_detail = {
                "resign_date": obj.get('Resign Date')
            }
            meta_detail = {k: v for k, v in meta_detail.items() if v}
            people_detail.append({
                "name": obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                "designation": "secretary",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            }) 
        elif 'AUTHORIZED REPRESENTATIVE' in obj.get('Type') or 'AGT / REGISTERED AGENT' in obj.get('Type'):
            meta_detail = {
                "start_date": obj.get('Start Date'),
                "resign_date": obj.get('Resign Date')
            }
            meta_detail = {k: v for k, v in meta_detail.items() if v}
            representative_address = f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}"
            if representative_address.replace(",", "").replace(" ", "") != "":
                people_detail.append({
                    "name": obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                    "designation": "representative",
                    "address": representative_address.replace(", ,", ""),
                    "meta_detail": meta_detail
                })
        elif 'REGISTRANT' in obj.get('Type'):
            number = obj.get('Of Record').split(", ")[0] if 'Of Record' in obj and ',' in obj.get('Of Record') and len(obj.get('Of Record').split(", ")) > 1 else ""
            meta_detail = {
                'number': number,
                'number_url': f"https://egov.sos.state.or.us/br/pkg_web_name_srch_inq.do_name_srch?p_name=&p_regist_nbr={number}&p_srch=PHASE1&p_print=FALSE&p_entity_status=ACTINA"
            } if number != "" else {}
            registrant_name = obj.get('Of Record').split(", ")[1] if 'Of Record' in obj and ',' in obj.get('Of Record') and len(obj.get('Of Record').split(", ")) > 1 else ""
            people_detail.append({
                "name": registrant_name if registrant_name != "" else obj.get("Name").replace(", ,", ""),
                "designation": "registrant",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            })
        elif 'MANAGER' in obj.get('Type'):
            meta_detail = {
                "resign_date": obj.get('Resign Date')
            }
            people_detail.append({
                "name": obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                "designation": "manager",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            }) 
        elif 'MEMBER' in obj.get('Type'):
            meta_detail = {
                "resign_date": obj.get('Resign Date')
            }
            people_detail.append({
                "name": obj.get('Name').replace(", ,", "") if obj.get('Name') is not None else "",
                "designation": "member",
                "address": f"{obj.get('Addr 1')} {obj.get('Addr 2')}  {obj.get('CSZ')} {obj.get('Country')}",
                "meta_detail": meta_detail
            })

    result["name"] = find_next_td_text(soup, 'Entity Name')
    result["foreign_name"] = find_next_td_text(soup, 'Foreign Name')
    result["non_profit_type"] = find_next_td_text(soup, 'Non Profit Type')
    result["affidavit"] = find_next_td_text(soup, 'Affidavit?')
    result["additional_detail"] = additional_detail
    result["previous_names_detail"] = previous_names_detail
    result["fillings_detail"] = fillings_detail
    result["addresses_detail"] = addresses_detail
    result["people_detail"] = people_detail
    return result
try:   
    start = sys.argv[1] if len(sys.argv) > 1 else ''
    if len(sys.argv) == 0:
        store_registry_ids()
    registry_numbers = get_registry_ids()
    flag = True
    for num in registry_numbers:
        if start != '' and num != start and flag:
            continue
        else:
            flag = False
        print("Record No:", num)
        url = f"https://egov.sos.state.or.us/br/pkg_web_name_srch_inq.do_name_srch?p_name=&p_regist_nbr={num}&p_srch=PHASE1&p_print=FALSE&p_entity_status=ACTINA"
        for attempt in range(10):  
            try:      
                driver.get(url)
                identify_captcha(driver)
                html_content = driver.page_source
                DATA_SIZE = len(html_content)
                soup = BeautifulSoup(html_content, "html.parser")
                data = get_page_data(soup)
                ENTITY_ID = oregon_crawler.generate_entity_id(company_name=data.get("name"), reg_number=data.get("registration_number"))
                BIRTH_INCORPORATION_DATE = ''
                DATA = oregon_crawler.prepare_data_object(data)
                ROW = oregon_crawler.prepare_row_for_db(ENTITY_ID, data.get("name"), BIRTH_INCORPORATION_DATE, DATA)
                oregon_crawler.insert_record(ROW)
                driver.delete_all_cookies()
                break
            except:
                print("Page not loaded, try again")

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    oregon_crawler.db_log(log_data)
    oregon_crawler.end_crawler()
    display.stop()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    oregon_crawler.db_log(log_data)
