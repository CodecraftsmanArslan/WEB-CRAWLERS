"""Import required library"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import ssl
from dateutil import parser
from pyvirtualdisplay import Display

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'New Mexico Secretary of State Business Services Division',
    'COUNTRY': 'New Mexico',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch",
                      "Source Description": "Official online portal for the New Mexico Secretary of State Business Services Division that provides information related to entities registered in New Mexico."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "New Mexico CO Official Registry"
}

new_mexico_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

selenium_helper = new_mexico_crawler.get_selenium_helper()
request_helper = new_mexico_crawler.get_requests_helper()
start_page = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 1

response = request_helper.make_request(
    "https://proxy.webshare.io/api/v2/proxy/list/download/cwymlooolhnjbmymhtyzggjwlnhvudhahzxsfcuw/US/any/username/direct/-/")
data = response.text
lines = data.strip().split('\n')
proxy_list = [line.replace('\r', '') for line in lines]
URL = "https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch"


def initialize():
    for i in range(len(proxy_list)):
        PROXY_HOST = proxy_list[i].split(":")[0]
        PROXY_PORT = proxy_list[i].split(":")[1]
        PROXY_SERVER = f'http://{PROXY_HOST}:{PROXY_PORT}'
        print(PROXY_SERVER)
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-gpu')
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--dns-server=8.8.8.8")
        options.add_argument(f'--proxy-server={PROXY_SERVER}')
        options.add_argument(f'--window-size=1920,1080')
        NOPECHA_KEY0 = 'sub_1NdSf9CRwBwvt6ptQYIIto4Z'
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--no-zygote')
        options.add_argument('--log-level=3')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-breakpad')
        with open('ext.crx', 'wb') as f:
            f.write(requests.get('https://nopecha.com/f/ext.crx').content)
        options.add_extension('ext.crx')
        print('Open webdriver')
        print("Downloading NopeCHA crx extension file.")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(300)
        action = ActionChains(driver=driver)
        print("Setting subscription key")
        driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY0}")
        time.sleep(5)
        driver.get(URL)
        time.sleep(10)
        if len(driver.find_elements(By.XPATH, '//input[@id = "txtBusinessName"]')) > 0:
            break
        else:
            print(f"Proxy: {proxy_list[i]} did not work, trying next...")
            driver.quit()
            continue
    crawl(driver=driver, action=action)

# Search the website by entering the search parameteres and check if there is any data available for the given search query.


def crawl(driver, action):
    print("Website Opened!")
    find_solve_captcha(driver=driver)
    search_field = driver.find_element(
        By.XPATH, '//input[@id = "txtBusinessName"]')
    search_field.send_keys("*")
    time.sleep(1)
    search_button = driver.find_element(By.XPATH, '//input[@value="Search"]')
    search_button.click()
    time.sleep(10)
    skip_pages(driver=driver)
    total_pages = int(driver.find_element(
        By.XPATH, '//li[@class="pageinfo"]').text.split(":")[-1].split("of")[-1].strip())
    for i in range(start_page, total_pages):
        print(f"Scraping page number: {i}")
        no_of_companies = len(driver.find_elements(
            By.XPATH, '//table[@id = "xhtml_Businessesgrid"]//tr/td/a'))
        for number in range(no_of_companies):
            all_companies = driver.find_elements(
                By.XPATH, '//table[@id = "xhtml_Businessesgrid"]//tr/td/a')
            if all_companies[number].text:
                action.move_to_element(all_companies[number]).click().perform()
                print(f"Scraping data for company number {number + 1}")
                get_company_data(driver=driver, action=action)
                back_button = driver.find_element(
                    By.XPATH, '//input[@value="Back"]')
                action.scroll_to_element(back_button).move_to_element(
                    back_button).click().perform()
                time.sleep(3)
        time.sleep(5)
        page_field_ = driver.find_element(By.ID, 'txtCommonPageNo')
        page_field_.send_keys(i+1)
        time.sleep(2)
        page_field_.send_keys(Keys.RETURN)
        time.sleep(10)

# Format the date and replace "/" with "-"


def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

# check if there is any captcha while crawling the page and solves it.


def find_solve_captcha(driver):
    try:
        captcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
        if captcha_element:
            print("Captcha Found!")
            selenium_helper.wait_for_captcha_to_be_solved(driver)
        time.sleep(5)
    except:
        print("No captcha found!")

# Skip all the crawled pages when resuming the crawler.


def skip_pages(driver):
    if start_page > 1:
        print(f"Skipping to page number: {start_page}...")
        page_field = driver.find_element(By.ID, 'txtCommonPageNo')
        page_field.send_keys(start_page)
        time.sleep(2)
        page_field.send_keys(Keys.RETURN)
        time.sleep(2)
        print(f"{start_page - 1} pages skipped!")
    time.sleep(10)

# Scrape all the data if there is any available for the company and store it in Database.


def get_company_data(driver, action):
    time.sleep(2)
    expand_all = driver.find_elements(
        By.XPATH, '//div[@style="float: right;"]')
    for item in expand_all:
        action.scroll_to_element(item).move_to_element(item).click().perform()
        time.sleep(0.2)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    people_detail = []

    # Entity Details
    business_id = soup.find("td", string="Business ID#:")
    business_id = business_id.find_next_sibling().text.strip() if business_id else ""
    entity_name = soup.find("td", string="Entity Name:")
    entity_name = entity_name.find_next_sibling().text.strip().replace("\"",
                                                                       "") if entity_name else ""
    dba_name = soup.find("td", string="DBA Name:")
    dba_name = dba_name.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if dba_name else ""
    status_ = soup.find("td", string="Status:")
    status_ = status_.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if status_ else ""
    standing = soup.find("td", string="Standing:")
    standing = standing.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if standing else ""

    # Entity Type and State of Domicile
    entity_type = soup.find("td", string="Entity Type:")
    entity_type = entity_type.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if entity_type else ""
    state_of_incorp = soup.find(
        "td", string=re.compile("State of Incorporation:"))
    state_of_incorp = state_of_incorp.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if state_of_incorp else ""
    status_law_code = soup.find("td", string=re.compile("Statute Law Code:"))
    status_law_code = status_law_code.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if status_law_code else ""
    benefit_corporation = soup.find(
        "td", string=re.compile("Benefit Corporation:"))
    benefit_corporation = benefit_corporation.find_next_sibling().text.strip(
    ).replace("Not Applicable", "") if benefit_corporation else ""

    # Formation Dates
    date_of_incorp_nm = soup.find(
        "td", string=re.compile("Date of Incorporation in NM:"))
    date_of_incorp_nm = date_of_incorp_nm.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if date_of_incorp_nm else ""
    date_of_formation = soup.find("td", string=re.compile(
        "Date of Formation in State of Domicile:"))
    date_of_formation = date_of_formation.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if date_of_formation else ""
    date_of_registration_nm = soup.find(
        "td", string=re.compile("Date of Registration in NM:"))
    date_of_registration_nm = date_of_registration_nm.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if date_of_registration_nm else ""
    date_of_org_nm = soup.find(
        "td", string=re.compile("Date of Organization in NM:"))
    date_of_org_nm = date_of_org_nm.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if date_of_org_nm else ""
    date_of_authority = soup.find(
        "td", string=re.compile("Date of Authority in NM:"))
    date_of_authority = date_of_authority.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if date_of_authority else ""
    management_type = soup.find("td", string=re.compile("Management Type:"))
    management_type = management_type.find_next_sibling(
    ).text.strip().replace("N/A", "") if management_type else ""

    # Reporting Information
    report_due_date = soup.find("td", string=re.compile("Report Due Date:"))
    report_due_date = report_due_date.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if report_due_date else ""
    session_expiration = soup.find(
        "td", string=re.compile("Suspension Expiration Date:"))
    session_expiration = session_expiration.find_next_sibling().text.strip(
    ).replace("Not Applicable", "") if session_expiration else ""
    next_anual_meeting = soup.find(
        "td", string=re.compile("Next Annual Meeting Date:"))
    next_anual_meeting = next_anual_meeting.find_next_sibling().text.strip(
    ).replace("Not Applicable", "") if next_anual_meeting else ""

    # Period of Existence and Purpose and Character of Affairs
    period_of_duration = soup.find(
        "td", string=re.compile("Period of Duration:"))
    period_of_duration = period_of_duration.find_next_sibling().text.strip(
    ).replace("Not Applicable", "") if period_of_duration else ""
    business_purpose = soup.find("td", string=re.compile("Business Purpose:"))
    business_purpose = business_purpose.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if business_purpose else ""
    char_of_affairs = soup.find(
        "td", string=re.compile("Character Of Affairs:"))
    char_of_affairs = char_of_affairs.find_next_sibling().text.strip().replace(
        "Not Applicable", "") if char_of_affairs else ""
    outstanding_items = soup.find(
        "strong", string=re.compile("Outstanding Items"))
    outstanding_items = outstanding_items.parent.parent.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if outstanding_items else ""
    registered_agent = soup.find("b", string=re.compile("Registered Agent:"))
    registered_agent = registered_agent.parent.parent.find_next_sibling(
    ).text.strip() if registered_agent else ""
    liecence_ = soup.find("b", string=re.compile("License:"))
    liecence_ = liecence_.parent.parent.find_next_sibling(
    ).text.strip() if liecence_ else ""
    benefit_purpose = soup.find("td", string=re.compile("Benefit Purpose:"))
    benefit_purpose = benefit_purpose.find_next_sibling(
    ).text.strip() if benefit_purpose else ""

    if period_of_duration or business_purpose or char_of_affairs or benefit_purpose:
        poe_dict = {
            "type": "existence_and_purpose_information",
            "data": [
                    {
                        "duration_period": period_of_duration,
                        "purpose": business_purpose,
                        "character_affairs": char_of_affairs,
                        "benefit_purpose": benefit_purpose.replace("Not Applicable", "")
                    }
            ]
        }
    else:
        poe_dict = {}

    # Contact Information
    mailing_address = soup.find("span", string=re.compile("Mailing Address:"))
    mailing_address = mailing_address.parent.find_next_sibling(
    ).text.strip().replace("NONE", "") if mailing_address else ""

    princ_place_anywhere = soup.find(
        "span", string="Principal Place of Business Anywhere:")
    if princ_place_anywhere:
        princ_place_anywhere = princ_place_anywhere.parent.find_next_sibling().text.strip()
    else:
        princ_place_anywhere = soup.find("span", string=re.compile(
            "Principal Place of Business in New Mexico:"))
        princ_place_anywhere = princ_place_anywhere.parent.find_next_sibling(
        ).text.strip() if princ_place_anywhere else ""

    secon_princ_place = soup.find("span", string=re.compile(
        "Secondary Principal Place of Business Anywhere:"))
    if secon_princ_place:
        secon_princ_place = secon_princ_place.parent.find_next_sibling().text.strip()
    else:
        secon_princ_place = soup.find("span", string=re.compile(
            "Secondary Principal Place of Business in New Mexico:"))
        secon_princ_place = secon_princ_place.parent.find_next_sibling(
        ).text.strip() if secon_princ_place else ""

    princ_out_mexico = soup.find("span", string=re.compile(
        "Principal Office Outside of New Mexico:"))
    princ_out_mexico = princ_out_mexico.parent.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if princ_out_mexico else ""
    reg_office_state = soup.find("span", string=re.compile(
        "Registered Office in State of Incorporation:"))
    reg_office_state = reg_office_state.parent.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if reg_office_state else ""
    princ_place_domestic = soup.find("span", string=re.compile(
        "Principal Place of Business in Domestic State/ Country:"))
    princ_place_domestic = princ_place_domestic.parent.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if princ_place_domestic else ""
    princ_office_nm = soup.find("span", string=re.compile(
        "Principal Office Location in NM:"))
    princ_office_nm = princ_office_nm.parent.find_next_sibling(
    ).text.strip().replace("Not Applicable", "") if princ_office_nm else ""

    # Registered Agent Information
    agent_name = soup.find("td", string="Name:")
    agent_name = agent_name.find_next_sibling().text.strip() if agent_name else ""
    agent_address = soup.find("td", string=re.compile(
        "Geographical Location Address:"))
    agent_address = agent_address.find_next_sibling(
    ).text.strip() if agent_address else ""
    agent_physical_address = soup.find(
        "td", string=re.compile("Physical Address:"))
    agent_physical_address = agent_physical_address.find_next_sibling(
    ).text.strip() if agent_physical_address else ""
    agent_date_of_appointment = soup.find(
        "td", string=re.compile("Date of Appointment:"))
    agent_date_of_appointment = agent_date_of_appointment.find_next_sibling(
    ).text.strip() if agent_date_of_appointment else ""
    agent_mailing_address = soup.find(
        "td", string=re.compile("Mailing Address:"))
    agent_mailing_address = agent_mailing_address.find_next_sibling(
    ).text.strip().replace("NONE", "") if agent_mailing_address else ""
    agent_effective_date = soup.find(
        "td", string=re.compile("Effective Date of Resignation:"))
    agent_effective_date = agent_effective_date.find_next_sibling(
    ).text.strip().replace("NONE", "") if agent_effective_date else ""

    agent_dict = {
        "designation": "registered_agent",
        "name": agent_name,
        "meta_detail": {
            "geo_loc_address": agent_address,
            "resignation_date": format_date(agent_effective_date)
        },
        "address": agent_physical_address,
        "postal_address": agent_mailing_address,
        "appointment_date": format_date(agent_date_of_appointment)
    }
    people_detail.append(agent_dict)

    # Organizer Information
    organizer_table = soup.find(id="grid_organizerList")
    if organizer_table:
        org_all_rows = organizer_table.find_all("tr")
        for org_row in org_all_rows[1:]:
            org_cells = org_row.find_all("td")
            if org_cells[0].text.strip() != "No records to view.":
                org_title = org_cells[0].text.strip()
                org_name = org_cells[1].text.strip()
                org_address = org_cells[2].text.strip()
                org_dict = {
                    "designation": org_title,
                    "name": org_name,
                    "address": org_address
                }
                people_detail.append(org_dict)

    # Filing History
    filing_table = soup.find("table", id="xhtml_grid_FilingHistorySearch")
    if filing_table:
        filing_all_rows = filing_table.find_all("tr")
        all_filing_data = []
        for filling_row in filing_all_rows[1:]:
            filling_cell = filling_row.find_all("td")
            if filling_cell[0].text.strip() != "No records to view.":
                filling_date = filling_cell[0].text.strip()
                filing_type = filling_cell[1].text.strip().replace(
                    "\n", " ").replace("  ", "")
                fiscal_year_end_date = filling_cell[2].text.strip()
                post_mark = filling_cell[3].text.strip()
                survivor = filling_cell[4].text.strip()
                instrument_text = filling_cell[5].text.strip()
                process_date = filling_cell[6].text.strip()
                filing_number = filling_cell[7].text.strip()
                filing_dict = {
                    "date": format_date(filling_date),
                    "filing_type": filing_type,
                    "title": instrument_text.replace("\n", " ").replace("  ", ""),
                    "meta_detail": {
                        "fiscal_year_end_date": format_date(fiscal_year_end_date),
                        "post_mark": post_mark,
                        "entity": survivor,
                        "processed_date": format_date(process_date)
                    },
                    "filing_code": filing_number
                }
                all_filing_data.append(filing_dict)
    else:
        all_filing_data = []

    # Director Information
    director_table = soup.find("table", id="grid_DirectorList")
    if director_table:
        director_all_rows = director_table.find_all("tr")
        for director_row in director_all_rows[1:]:
            director_cell = director_row.find_all("td")
            if director_cell[0].text.strip() != "No records to view.":
                director_title = director_cell[0].text.strip()
                director_name = director_cell[1].text.strip()
                director_address = director_cell[2].text.strip().replace(
                    "\n", " ").replace("  ", "")
                director_dict = {
                    "designation": director_title,
                    "name": director_name,
                    "address": director_address
                }
                people_detail.append(director_dict)

    # Officer Information
    officer_table = soup.find("table", id="grid_OfficersList")
    if officer_table:
        officer_all_rows = officer_table.find_all("tr")
        for officer_row in officer_all_rows[1:]:
            officer_cell = officer_row.find_all("td")
            if officer_cell[0].text.strip() != "No records to view.":
                officer_title = officer_cell[0].text.strip()
                officer_name = officer_cell[1].text.strip()
                officer_address = officer_cell[2].text.strip().replace(
                    "\n", " ").replace("  ", "")
                officer_dict = {
                    "designation": officer_title,
                    "name": officer_name,
                    "address": officer_address
                }
                people_detail.append(officer_dict)

    # Manager Information
    manager_table = soup.find("table", id="grid_managerList")
    if manager_table:
        manager_all_rows = manager_table.find_all("tr")
        for manager_row in manager_all_rows[1:]:
            manager_cell = manager_row.find_all("td")
            if manager_cell[0].text.strip() != "No records to view.":
                manager_title = manager_cell[0].text.strip()
                manager_name = manager_cell[1].text.strip()
                manager_address = manager_cell[2].text.strip().replace(
                    "\n", " ").replace("  ", "")
                manager_dict = {
                    "designation": manager_title,
                    "name": manager_name,
                    "address": manager_address
                }
                people_detail.append(manager_dict)

    # Member Information
    member_table = soup.find("table", id="grid_memberList")
    if member_table:
        member_all_rows = member_table.find_all("tr")
        for member_row in member_all_rows[1:]:
            member_cell = member_row.find_all("td")
            if member_cell[0].text.strip() != "No records to view.":
                member_title = member_cell[0].text.strip()
                member_name = member_cell[1].text.strip()
                member_address = member_cell[2].text.strip().replace(
                    "\n", " ").replace("  ", "")
                member_dict = {
                    "designation": member_title,
                    "name": member_name,
                    "address": member_address
                }
                people_detail.append(member_dict)

    # Incorporator Information
    incorporator_table = soup.find("table", id="grid_IncorporatorList")
    if incorporator_table:
        incorporator_all_rows = incorporator_table.find_all("tr")
        for incorporator_row in incorporator_all_rows[1:]:
            incorporator_cell = incorporator_row.find_all("td")
            if incorporator_cell[0].text.strip() != "No records to view.":
                incorporator_title = incorporator_cell[0].text.strip()
                incorporator_name = incorporator_cell[1].text.strip()
                incorporator_address = incorporator_cell[2].text.strip().replace(
                    "\n", " ").replace("  ", "")
                incorporator_dict = {
                    "designation": incorporator_title,
                    "name": incorporator_name,
                    "address": incorporator_address
                }
                people_detail.append(incorporator_dict)

    # Name History
    name_history_button = driver.find_element(
        By.XPATH, '//input[@name="btnNameHistory"]')
    action.scroll_to_element(name_history_button).move_to_element(
        name_history_button).click().perform()
    time.sleep(2)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    previous_name_table = soup2.find("table", id="xhtml_grid_NameHistory")
    if previous_name_table:
        previous_name_all_rows = previous_name_table.find_all("tr")
        all_previous_name_data = []
        for previous_name_row in previous_name_all_rows[1:]:
            previous_name_cell = previous_name_row.find_all("td")
            previous_name_filing_number = previous_name_cell[0].text.strip()
            if "No records to view." in previous_name_filing_number:
                continue
            previous_name_old_name = previous_name_cell[1].text.strip()
            previous_name_dba = previous_name_cell[2].text.strip().replace(
                "\n", " ").replace("  ", "")
            pevious_name_new_name = previous_name_cell[3].text.strip()
            previous_name_new_dba = previous_name_cell[4].text.strip()
            previous_name_filing_date = previous_name_cell[5].text.strip()
            previous_name_dict = {
                "meta_detail": {
                    "filing_code": previous_name_filing_number,
                    "previous_dba_name": previous_name_dba,
                    "current_name": pevious_name_new_name,
                    "new_dba_name": previous_name_new_dba,
                    "date": format_date(previous_name_filing_date)
                },
                "name": previous_name_old_name
            }
            all_previous_name_data.append(previous_name_dict)
    else:
        all_previous_name_data = []

    close_button = driver.find_element(By.XPATH, '//input[@value="Close"]')
    action.scroll_to_element(close_button).move_to_element(
        close_button).click().perform()
    time.sleep(2)

    OBJ = {
        "registration_number": business_id,
        "status": status_,
        "name": entity_name.replace("\n", "").replace("%", "%%"),
        "standing": standing.replace("N/A", ""),
        "aliases": dba_name,
        "type": entity_type,
        "jurisdiction": state_of_incorp,
        "benefit_corporation": benefit_corporation,
        "state_law_code": status_law_code,
        "incorporation_date": format_date(date_of_incorp_nm),
        "registration_date": format_date(date_of_registration_nm),
        "additional_detail": [
            {
                "type": "incorporation_date_information",
                "data": [
                    {
                        "incorporation_date_in_new_mexico": format_date(date_of_incorp_nm),
                        "organization_date_in_new_mexico": format_date(date_of_org_nm),
                        "state_domicile_incorporation_date": format_date(date_of_formation),
                        "authority_incorporation_date": format_date(date_of_authority),
                        "registration_date_in_new_mexico": format_date(date_of_registration_nm),
                        "management_type": management_type
                    }
                ]
            },
            {
                "type": "reporting_information",
                "data": [
                    {
                        "report_due_date": format_date(report_due_date),
                        "suspension_expiry_date": format_date(session_expiration),
                        "annual_meeting_date": format_date(next_anual_meeting)
                    }
                ]
            },
            poe_dict,
        ],
        "addresses_detail": [
            {
                "type": "mailing_address",
                "address": mailing_address,
            },
            {
                "type": "principal_business_address",
                "address": princ_place_anywhere,
            },
            {
                "type": "secondary_principal_address",
                "address": secon_princ_place,
            },
            {
                "type": "outside_address",
                "address": princ_out_mexico
            },
            {
                "type": "registered_jurisdiction_office_address",
                "address": reg_office_state
            },
            {
                "type": "domestic_state_or_country_address",
                "address": princ_place_domestic
            },
            {
                "type": "principal_office_address",
                "address": princ_office_nm
            }
        ],
        "people_detail": people_detail,
        "fillings_detail": all_filing_data,
        "previous_names_detail": all_previous_name_data
    }

    if report_due_date == "" and session_expiration == "" and next_anual_meeting == "":
        del OBJ["additional_detail"][1]

    OBJ = new_mexico_crawler.prepare_data_object(OBJ)
    ENTITY_ID = new_mexico_crawler.generate_entity_id(
        OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = new_mexico_crawler.prepare_row_for_db(
        ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    new_mexico_crawler.insert_record(ROW)


try:
    initialize()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    new_mexico_crawler.db_log(log_data)
    new_mexico_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    new_mexico_crawler.db_log(log_data)
    display.stop()
