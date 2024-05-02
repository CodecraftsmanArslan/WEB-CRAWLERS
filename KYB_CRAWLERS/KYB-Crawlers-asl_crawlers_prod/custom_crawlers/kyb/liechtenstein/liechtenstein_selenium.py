"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import ssl
from pyvirtualdisplay import Display
from dateutil import parser

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'Handelsregister des Fürstentums',
    'COUNTRY': 'Liechtenstein',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.oera.li/cr-portal/suche/suche.xhtml",
                      "Source Description": "The Commercial Register of the Principality of Liechtenstein is a governmental registry that records all companies and business entities registered in Liechtenstein. It serves the purpose of documenting and providing transparency regarding economic activities in the country. The Commercial Register contains information such as company names, legal forms, registered offices, directors, and shareholdings of the registered entities, which are made publicly accessible."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.oera.li/cr-portal/suche/suche.xhtml'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Liechtenstein Official Registry" 
}

liechtenstein_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

selenium_helper = liechtenstein_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)

alphabets = ['__a', '__b', '__c', '__d', '__e', '__f', '__g', '__h', '__i', '__j', '__k', '__l', '__m', '__n', '__o', '__p', '__q', '__r', '__s', '__t', '__u', '__v', '__w', '__x', '__y', '__z', 'Vaduz', 'Schaan', 'Triesen', 'Balzers', 'Eschen', 'Mauren', 'Triesenberg', 'Ruggell', 'Gamprin', 'Planken', 'Schellenberg']
municipalites = ['Vaduz', 'Schaan', 'Triesen', 'Balzers', 'Eschen', 'Mauren', 'Triesenberg', 'Ruggell', 'Gamprin', 'Planken', 'Schellenberg']

start_page = 1

if len(ARGUMENT) > 1:
    start_page = int(ARGUMENT[1])
else:
    start_page = start_page

if len(ARGUMENT) > 2:
    start_alphabet = ARGUMENT[2]
else:
    start_alphabet = alphabets[0]

if len(ARGUMENT) > 3:
    start_municipality = ARGUMENT[3]
else:
    start_municipality = municipalites[0]

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def skip_pages():
    if start_page > 1:
        print("Skipping pages...")
        next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next Page"]')
        for i in range(start_page - 1):
            action.scroll_to_element(next_button).move_to_element(next_button).click().perform()
            time.sleep(5)
            print(f"Page no: {i+1} Skipped")


def crawl(alphabet, municipality):
    driver.get('https://www.oera.li/cr-portal/suche/suche.xhtml')
    time.sleep(2)
    try:
        cookie_button = driver.find_element(By.ID, 'j_idt182')
        cookie_button.click()
    except:
        pass        
    reset_button = driver.find_element(By.ID, 'idSucheForm:j_idt145')
    action.move_to_element(reset_button).click().perform()
    time.sleep(5)
    input_element = driver.find_element(By.ID, "idSucheForm:idFirma")
    input_element.send_keys(alphabet)
    drop_down_element = driver.find_element(By.CLASS_NAME, "ui-accordion-header")
    drop_down_element.click()
    time.sleep(3)
    search_element = driver.find_element(By.ID, "idSucheForm:panel:idSitz_input")
    search_element.send_keys(municipality, Keys.PAGE_DOWN, Keys.PAGE_DOWN)
    time.sleep(3)
    li_element = driver.find_element(By.CLASS_NAME, "ui-autocomplete-item")
    li_element.click()
    time.sleep(3)
    search_element.send_keys(Keys.PAGE_DOWN, Keys.PAGE_DOWN)
    time.sleep(1)
    check1 = driver.find_element(By.XPATH, '//*[@id="idSucheForm:panel:j_idt135"]/div[2]')
    action.move_to_element(check1).click().perform()
    check2 = driver.find_element(By.XPATH, '//*[@id="idSucheForm:panel:j_idt136"]/div[2]')
    action.move_to_element(check2).click().perform()
    check3 = driver.find_element(By.XPATH, '//*[@id="idSucheForm:panel:j_idt137"]/div[2]')
    action.move_to_element(check3).click().perform()
    check4 = driver.find_element(By.XPATH, '//*[@id="idSucheForm:panel:j_idt138"]/div[2]')
    action.move_to_element(check4).click().perform()
    time.sleep(1)
    search_button = driver.find_element(By.ID, 'idSucheForm:j_idt143')
    action.move_to_element(search_button).click().perform()
    time.sleep(5)
    skip_pages()
    time.sleep(2)
    get_data(start_page=start_page, alphabet=alphabet, municipality=municipality)

def get_data(start_page, alphabet, municipality):
    have_next_page = True
    while have_next_page:
        print(f"Scrapping data from page no: {start_page} of alphabet: {alphabet} for municipality: {municipality}")
        all_companies = driver.find_elements(By.XPATH, '//button[@title="Auszug anzeigen"]')
        for company in all_companies:
            action.scroll_to_element(company).move_to_element(company).click().perform()
            link_not_openened = True
            while link_not_openened:
                    time.sleep(5)
                    site_url = driver.current_url
                    if "uid=" in site_url:
                        link_not_openened = False
                    else:
                        action.scroll_to_element(company).click().perform()

            soup = BeautifulSoup(driver.page_source, "html.parser")

            data = soup.find("div", id="Titel")
            
            
            company_name = driver.find_element(By.CLASS_NAME, 'firmaTitle').text if len(driver.find_elements(By.CLASS_NAME, 'firmaTitle')) > 0 else ""
            if company_name == "":
                driver.back()
                time.sleep(2)
                continue

            entity_type = soup.find("span", class_="firmaTitle").parent.find_next_sibling() if soup.find("span", class_="firmaTitle") is not None else ""
            entity_type_text = entity_type.text if entity_type != "" else ""
            try:
                if data:
                    div = data.find_all("span")[4].text
                    registration_date = format_date(div)
            except IndexError:
                try:
                    if data:
                        div = data.find_all("span")[3].text
                        registration_date = format_date(div)
                except:
                    registration_date = ""

            municipality_ = entity_type.nextSibling.nextSibling.text if entity_type.nextSibling.nextSibling is not None else ""
            registration_number = driver.current_url.split("uid=")[-1]

            data = {}

            table1 = soup.find_all('table', class_ = 'table')[2]
            head = table1.find("thead").text.strip().split("\n")[-1].strip()
            if "Zustelladresse" in head:
                table2 = soup.find_all('table',class_ = 'table')[3]
                try:
                    table3 = soup.find_all('table',class_ = 'table')[4]
                except:
                    table3 = soup.find_all('table',class_ = 'table')[3]

                table1_rows = table1.find_all('tr')
                for table_row in table1_rows[1:]:
                    table_cells = table_row.find_all('td')
                    ei_num = table_cells[0].text.strip()
                    address = table_cells[2].text.strip()
                    data['ei_num'] = ei_num
                    data['address'] = address
            else:
                data['ei_num'] = ""
                data['address'] = ""
                table2 = soup.find_all('table',class_ = 'table')[2]
                try:
                    table3 = soup.find_all('table',class_ = 'table')[3]
                except:
                    table3 = soup.find_all('table',class_ = 'table')[2]

            additional_data = []
            table2_rows = table2.find_all('tr')
            for table_row2 in table2_rows[1:]:
                table2_cells = table_row2.find_all('td')
                ref = table2_cells[0].text.strip()
                try:
                    tr_nr = table2_cells[1].text.strip()
                except:
                    tr_nr = ""
                try:
                    tr_datum = table2_cells[2].text.strip().replace(".","-")
                except:
                    tr_datum = ""
                if ref or tr_nr or tr_datum:
                    data_dict = {
                        "reference_number":ref,
                        "daily_register_number":tr_nr,
                        "daily_register_date":tr_datum
                    }

                    if "(Auslassung) (Report)  (Omissione) (Transfer)" not in data_dict['daily_register_date']:
                        additional_data.append(data_dict)

            table3_rows = table3.find_all('tr')
            for table_row3 in table3_rows[1:]:
                table3_cells = table_row3.find_all('td')
                ref_ = table3_cells[0].text.strip()
                try:
                    tr_nr_ = table3_cells[1].text.strip()
                except:
                    tr_nr_ = ""
                try:
                    tr_datum_ = table3_cells[2].text.strip().replace(".","-")
                except:
                    tr_datum_ = ""
                if ref_ or tr_nr_ or tr_datum_:
                    data_dict_ = {
                        "reference_number":ref_,
                        "daily_register_number":tr_nr_,
                        "daily_register_date": tr_datum_
                    }
                    if "(Auslassung) (Report)  (Omissione) (Transfer)" not in data_dict_['daily_register_date']:
                        additional_data.append(data_dict_)

            OBJ = {
                "name": company_name,
                "type": entity_type_text,
                "registration_number": registration_number,
                "registration_date": registration_date,
                "municipality": municipality_,
                "addresses_detail":[
                    {
                        "type":"general_address",
                        "address": data['address'],
                        "meta_detail":{
                            "reference_number":data['ei_num']
                        }
                    }
                ], 
                "additional_detail":[
                        {
                            "type": "daily_register_information",
                            "data": additional_data
                        }
                ], 
            }

            OBJ = liechtenstein_crawler.prepare_data_object(OBJ)
            ENTITY_ID = liechtenstein_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
            BIRTH_INCORPORATION_DATE = ''
            ROW = liechtenstein_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
            liechtenstein_crawler.insert_record(ROW)
            driver.back()
            time.sleep(3)

        start_page += 1
        timeout = 5

        next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next Page"]')
        next_button_class = next_button.get_attribute("class")
        if "ui-state-disabled" in next_button_class:
            have_next_page = False
        else:
            action.scroll_to_element(next_button).move_to_element(next_button).click().perform()
            time.sleep(5)

    
try:
    for alphabet in alphabets:
        if start_alphabet != alphabet:
            continue
        for municipality in municipalites:
            if start_municipality != municipality:
                continue
            crawl(alphabet=alphabet, municipality=municipality)

    liechtenstein_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    liechtenstein_crawler.db_log(log_data)
    display.stop()
    driver.close()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    liechtenstein_crawler.db_log(log_data)
    display.stop()
    driver.close()     