"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from dateutil import parser
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv
URL = "https://www.lbr.lu/"

meta_data = {
    'SOURCE': 'LUXEMBOURG BUSINESS REGISTERS',
    'COUNTRY': 'Luxembourg',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.lbr.lu/",
                      "Source Description": "The LUXEMBOURG BUSINESS REGISTERS (hereafter “LBR”) economic interest group (eig) updates their database in order to grant public access to information about physical persons and entities which are subject to registration with regards to the legislation concerning the Trade and Companies Register (RCS) and those relating to the beneficial ownership of entities covered by the law applicable to the Register of Beneficial Owners (RBE)."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.lbr.lu/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Luxembourg Official Registry" 
}

luxembourg_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = luxembourg_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)

all_alphabets = ["B", "A", "E", "F", "K"]
start_alphabet = ARGUMENT[1].capitalize() if len(ARGUMENT) > 1 else all_alphabets[0]

continue_loop = True

driver.get(URL)
time.sleep(5)
print("Website Opened!!")

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def login(search_query):
    buy_button = driver.find_element(By.XPATH, '//a[text()="Order a company profile"]')
    buy_button.click()
    time.sleep(2)
    try:
        search_company_button = driver.find_element(By.XPATH, '//a[contains(@href, "companyconsultation")]')
        search_company_button.click()
        time.sleep(3)
        search_field = driver.find_element(By.ID, 'rcsNumber')
        search_field.send_keys(search_query)
        search_field.send_keys(Keys.RETURN)
    except:
        anon_login_button = driver.find_element(By.XPATH, '//span[text()="Anonymous user"]')
        action.move_to_element(anon_login_button).click().perform()
        time.sleep(5)
        question = driver.find_element(By.XPATH, '//label[@for="captcha.result.uu"]').text.strip()
        answer = input(f"{question}: ")
        answer_field = driver.find_element(By.XPATH, '//input[@name="captcha.result.uu"]')
        answer_field.send_keys(answer)
        agree_button = driver.find_element(By.ID, 'acceptCIEcheckboxID')
        agree_button.click()
        time.sleep(1)
        continue_button = driver.find_element(By.XPATH, '//button[text()="Continue "]')
        continue_button.click()
        tnc_button = driver.find_element(By.XPATH, '//input[@name="conditionsversioncheck"]')
        tnc_button.click()
        time.sleep(10)
        search_company_button = driver.find_element(By.XPATH, '//a[contains(@href, "companyconsultation")]')
        search_company_button.click()
        time.sleep(3)
        search_field = driver.find_element(By.ID, 'rcsNumber')
        search_field.send_keys(search_query)
        search_field.send_keys(Keys.RETURN)
        time.sleep(5)

def crawl(start_number, end_number):
    access_button = driver.find_element(By.XPATH, '//div[@class="registerselection"]/ul//a')
    access_button.click()
    time.sleep(3)
    search_company_button = driver.find_element(By.XPATH, '//a[contains(@href, "companyconsultation")]')
    search_company_button.click()
    time.sleep(3)
    for alphabet in all_alphabets[all_alphabets.index(start_alphabet):]:
        for i in range(start_number, end_number):
            search_query = alphabet + str(i)
            search_field = driver.find_element(By.ID, 'rcsNumber')
            search_field.clear()
            search_field.send_keys(search_query)
            search_field.send_keys(Keys.RETURN)
            time.sleep(3)
            if "Your search did not lead to any results. Please modify your search criteria." in driver.page_source:
                print(f"No record found for: {search_query}")
                time.sleep(3)
                continue
            get_data(reg_num=search_query)
            search_again_button = driver.find_element(By.XPATH, '//a[text()="Search for an RCS file"]')
            search_again_button.click()
            time.sleep(3)
        start_number = 0

def get_data(reg_num):
    print(f"Scraping data for: {reg_num}")
    if "Log onto the website to access the filing list." in driver.page_source:
        login(search_query=reg_num)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_filings_detail = []
    addresses_detail = []
    archieved_details = []
    nace_details = []

    registration_number = reg_num
    try:
        company_name = soup.find("div", class_="withInfoOut").find("h1").text.split("\n")[0].strip()
    except:
        company_name = ""
    company_status = soup.find("div", class_="withInfoOut").find("h1").text.replace(registration_number, "").replace(company_name, "").replace(",", "").strip() if soup.find("div", class_="withInfoOut").find("h1") else ""
    aliases = soup.find("b", string="Trade name(s)") if soup.find("b", string="Trade name(s)") else ""
    aliases = str(aliases.parent).replace("<br/>", "--").replace("<b>Trade name(s)</b>", "").replace('<li class="clearLeft">', "").replace("</li>", "").replace("\n", "").strip().split("--")[1:]
    aliases = [name.strip().replace("&amp;", "") for name in aliases]
    all_other_names = []

    if len(aliases) > 1:
        for other_name in aliases:
            aliases_dict = {
                "name": other_name
            }
            all_other_names.append(aliases_dict)
    else:
        aliases = aliases[0]

    abridged = soup.find("b", string="Abridged")
    abridged = abridged.next_sibling.next_sibling.text.strip() if abridged else ""
    address = soup.find("b", string="Registered office")
    address = address.next_sibling.next_sibling.text.strip() if address else ""
    if address:
        address_dict = {
            "type": "registered_address",
            "address": address
        }
        addresses_detail.append(address_dict)
    registration_date = soup.find("b", string="Registration date")
    if registration_date:
        registration_date = registration_date.next_sibling.next_sibling.text.strip()
        registration_date = format_date(registration_date)
    else:
        registration_date = ""
    deletion_filing_date = soup.find("b", string="Deletion filing date")
    if deletion_filing_date:
        deletion_filing_date = deletion_filing_date.next_sibling.next_sibling.text.strip()
        deletion_filing_date = format_date(deletion_filing_date)
    else:
        deletion_filing_date = ""
    company_type = soup.find("b", string="Legal form")
    company_type = company_type.next_sibling.next_sibling.text.strip() if company_type else ""
    domicile_status = soup.find("b", string="Disclosure of the domiciliation agreement")
    domicile_status = domicile_status.next_sibling.next_sibling.text.strip() if domicile_status else ""
    nace_data = soup.find("i", string="Information updated monthly")
    nace_data = nace_data.parent.next_sibling.next_sibling.text.strip() if nace_data else ""
    if nace_data:
        nace_code = nace_data.split(" ")[0]
        nace_decription = nace_data.replace(nace_code, "").strip()
        nace_dict = {
            "nace_code": nace_code,
            "description": nace_decription
        }
        nace_details.append(nace_dict)

    filing_table_div = soup.find("div", id="TAB1")
    if filing_table_div:
        filing_table = soup.find("div", id="TAB1").find("tbody")
        filing_rows = filing_table.find_all("tr")
        filing_check = filing_rows[0].find("td").text
        if filing_check != "No filings":
            if len(filing_rows) > 0:
                for filing_row in filing_rows:
                    filing_data = filing_row.find_all("td")
                    filing_number = filing_data[0].text.strip()
                    filing_date = filing_data[1].text.strip()
                    filing_type = filing_data[2].text.strip()
                    filing_detail = filing_data[3].text.strip()
                    try:
                        filing_url = filing_data[4].find("img", {"title":"View document"}).get("onclick").split("('")[-1].replace("');", "").strip()
                    except:
                        filing_url = ''
                    filing_dict = {
                        "filing_code": filing_number,
                        "date": format_date(filing_date),
                        "filing_type": filing_type.replace("   ", "").replace("\n", "").replace("\t", ""),
                        "file_url": filing_url,
                        "description": filing_detail.replace("-", "")
                    }
                    all_filings_detail.append(filing_dict)

    publication_table_div = soup.find("div", id="TAB3")
    if publication_table_div:
        publication_table = soup.find("div", id="TAB3").find("tbody")
        publication_rows = publication_table.find_all("tr")
        publication_check = publication_rows[0].find("td").text
        if publication_check != "No publications":
            if len(publication_rows) > 0:
                for publication_row in publication_rows:
                    publication_data = publication_row.find_all("td")
                    publication_number = publication_data[0].text.strip()
                    publication_date = publication_data[1].text.strip()
                    publication_type = publication_data[2].text.strip()
                    publication_detail = publication_data[3].text.strip()
                    if publication_data[4].text != "By filing mention":
                        publication_url = publication_data[4].find("img", {"title":"See the publication"}).get("onclick").split("('")[-1].replace("');", "").strip()
                    else:
                        publication_url = ""
                    publication_dict = {
                        "filing_code": publication_number,
                        "date": format_date(publication_date),
                        "filing_type": publication_type.replace("   ", ""),
                        "file_url": publication_url,
                        "description": publication_detail.replace("-", "")
                    }
                    all_filings_detail.append(publication_dict)

    archieved_table_div = soup.find("div", id="TAB2")
    if archieved_table_div:
        archieved_table = soup.find("div", id="TAB2").find("tbody")
        archieved_rows = archieved_table.find_all("tr")
        if len(archieved_rows) > 0:
            for archieved_row in archieved_rows:
                archieved_data = archieved_row.find_all("td")
                type_of_archieve = archieved_data[0].text.strip()
                archieved_date = archieved_data[1].text.strip()
                no_of_documents = archieved_data[2].text.strip()
                try:
                    archieved_url = archieved_data[3].find("img", {"title":"View document"}).get("onclick").split("('")[-1].replace("');", "").strip()
                except:
                    archieved_url = ''
                archieved_dict = {
                    "date": format_date(archieved_date),
                    "filing_type": type_of_archieve.replace("   ", ""),
                    "file_url": archieved_url,
                    "meta_detail": {
                        "total_documents": no_of_documents
                    }
                }
                archieved_details.append(archieved_dict)

    OBJ = {
        "name": company_name.replace("\"", ""),
        "status": company_status,
        "registration_number": registration_number,
        "aliases": aliases,
        "addresses_detail": addresses_detail,
        "registration_date": registration_date,
        "type": company_type,
        "additional_detail": [
            {
                "type": "nace_code_info",
                "data": nace_details
            },
            {
                "type": "archived_files_info",
                "data": archieved_details
            },
            {
                "type": "other_names",
                "data": all_other_names
            }
        ],
        "fillings_detail": all_filings_detail,
        "file_deletion_date": deletion_filing_date,
        "domicile_status": domicile_status,
        "abridged": abridged
    }

    if len(aliases) > 1:
        del OBJ["aliases"]
    else:
        del OBJ["additional_detail"][3]

    OBJ = luxembourg_crawler.prepare_data_object(OBJ)
    ENTITY_ID = luxembourg_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = luxembourg_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    luxembourg_crawler.insert_record(ROW) 

try:
    start_number = int(ARGUMENT[2]) if len(ARGUMENT) > 2 else 0
    end_number = int(ARGUMENT[3]) if len(ARGUMENT) > 3 else 1000000
    crawl(start_number=start_number, end_number= end_number)
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    luxembourg_crawler.db_log(log_data)
    luxembourg_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    luxembourg_crawler.db_log(log_data)
    