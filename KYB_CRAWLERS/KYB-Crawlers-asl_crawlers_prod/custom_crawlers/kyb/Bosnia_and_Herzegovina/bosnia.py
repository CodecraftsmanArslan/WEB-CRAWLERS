import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import ssl
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from CustomCrawler import CustomCrawler
import requests
import string
from selenium.common.exceptions import TimeoutException


meta_data = {
    'SOURCE': 'Federal Ministry of Justice and Judicial Commission - Register of Business Entities',
    'COUNTRY': 'Bosnia and Herzegovina',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://bizreg.pravosudje.ba/pls/apex/f?p=186:20:14599042763943::NO::P20_SEKCIJA_TIP,P20_POMOC:PRETRAGA,FALSE",
                      "Source Description": "The electronic court registers contain information on all business/legal entities that are required to register by the Laws on Registration of Business Entities (a business company or an enterprise established for the purpose of economic activity, a cooperative or a cooperative association or any other legal entity performing an economic activity established in accordance with the specific laws of both entities and District Brčko with the aim of generating profit); since the moment those electronic registers were introduced in the registration courts. "},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://bizreg.pravosudje.ba/pls/apex/f?p=186:20:14599042763943::NO::P20_SEKCIJA_TIP,P20_POMOC:PRETRAGA,FALSE'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bosnia and Herzegovina Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


Bosnia_and_Herzegovina_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = Bosnia_and_Herzegovina_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True)

driver.get("https://bizreg.pravosudje.ba/pls/apex/f?p=186:20:14599042763943::NO::P20_SEKCIJA_TIP,P20_POMOC:PRETRAGA,FALSE")


characters = string.ascii_lowercase + string.digits
arguments = sys.argv
start_char = arguments[1] if len(arguments) > 1 else characters[0]


try:
    character_not_found = True
    for char in characters:
        if char != start_char and character_not_found:
            continue
        else:
            character_not_found = False
        for radio in range(4):
            radio_button = driver.find_element(By.ID, 'P20_PARAMETAR_RADIO')
            click_on = radio_button.find_elements(
                By.XPATH, "//input[@name='p_v04']")
            if 0 <= radio < len(click_on):
                click_on[radio].click()
                search = driver.find_element(
                    By.XPATH, '//input[@name="p_t05"]')

                text_to_send = "__" + char
                search.send_keys(text_to_send)
                print("Sent to input field:", text_to_send)
                submit_value = driver.find_element(
                    By.XPATH, "//a[contains(text(), 'SEARCH')]")
                submit_value.click()
                time.sleep(10)
                while True:
                    for column_num in range(5):
                        table = driver.find_element(
                            By.XPATH, "//table[@class='t15standardalternatingrowcolors']")
                        headers = table.find_elements(By.TAG_NAME, "th")

                        if 0 <= column_num < len(headers):
                            headers[column_num].click()
                            page_number = 1
                            no_of_links = len(driver.find_elements(
                                By.XPATH, '//table[@class="t15standardalternatingrowcolors"]//a[starts-with(@href, "f?p")]'))
                            for i in range(no_of_links):
                                item = {}
                                additional_detail = []
                                people_detail = []
                                data = []
                                links = driver.find_elements(
                                    By.XPATH, '//table[@class="t15standardalternatingrowcolors"]//a[starts-with(@href, "f?p")]')
                                href = links[i].get_attribute("href")
                                if href is not None:
                                    url = href
                                    driver.get(url)
                                    soup = BeautifulSoup(
                                        driver.page_source, "html.parser")
                                    try:
                                        registration_number = soup.select_one(
                                            'td:-soup-contains("Registration Number") + td').get_text(strip=True)
                                        general_name = soup.select_one(
                                            'td:-soup-contains("Name") + td').get_text(strip=True).replace("\"", "")
                                        abbreviation = soup.select_one(
                                            'td:-soup-contains("Abbreviation") + td').get_text(strip=True)
                                        address = soup.select_one(
                                            'td:-soup-contains("Address") + td').get_text(strip=True)
                                        legal_form = soup.select_one(
                                            'td:-soup-contains("Legal form of organization") + td').get_text(strip=True)
                                        status = soup.select_one(
                                            'td:-soup-contains("Status (Bankruptcy – YES/NO)") + td').get_text(strip=True)
                                        unique_identification_number = soup.select_one(
                                            'td:-soup-contains("Unique Identification Number") + td').get_text(strip=True)
                                        customs_number = soup.select_one(
                                            'td:-soup-contains("Customs Number") + td').get_text(strip=True)

                                        foreign = driver.find_element(
                                            By.XPATH, '//a[text()="Foreign trade"]')
                                        foreign.click()
                                        soup_foreign = BeautifulSoup(
                                            driver.page_source, "html.parser")
                                        authorised_for_foreign_trade_element = soup_foreign.find(
                                            "td", string="Authorised for foreign trade")
                                        # Extract text from the following sibling <td> element
                                        authorised_for_foreign_trade = authorised_for_foreign_trade_element.find_next(
                                            "td").text if authorised_for_foreign_trade_element else None
                                        additional_detail.append(
                                            {
                                                "type": "foreign_trade_info",
                                                "data": [
                                                    {
                                                        "authorized_for_foreign_trade": authorised_for_foreign_trade

                                                    }
                                                ]

                                            }
                                        )

                                        time.sleep(5)
                                        Notes = driver.find_element(
                                            By.XPATH, '//a[text()="Notes"]')
                                        Notes.click()
                                        soup_Notes = BeautifulSoup(
                                            driver.page_source, "html.parser")
                                        datum_element = soup_Notes.find(
                                            "td", string="Datum")
                                        sadrzaj_element = soup_Notes.find(
                                            "td", string="Sadržaj")
                                        # Extract text from the following sibling <td> elements
                                        if datum_element and sadrzaj_element:
                                            datum = datum_element.find_next(
                                                "td").text
                                            sadrzaj = sadrzaj_element.find_next(
                                                "td").text
                                            additional_detail.append(
                                                {
                                                    "type": "Notes",
                                                    "data": [
                                                        {
                                                            "date": datum,
                                                            "description": sadrzaj

                                                        }
                                                    ]

                                                }
                                            )

                                        Founders = driver.find_element(
                                            By.XPATH, '//a[text()="Founders"]')
                                        Founders.click()
                                        soup_Founders = BeautifulSoup(
                                            driver.page_source, "html.parser")
                                        name_element = soup_Founders.find(
                                            "td", string="Ime osnivača")
                                        capital_contracted_element = soup_Founders.find(
                                            "td", string="Kapital [ugovoreni]")
                                        capital_paid_in_element = soup_Founders.find(
                                            "td", string="Kapital [uplaćeni]")
                                        shares_element = soup_Founders.find(
                                            "td", string="Dionice [broj]")
                                        # Extract text from the following sibling <td> elements
                                        name = name_element.find_next(
                                            "td").text if name_element else ""
                                        capital_contracted = capital_contracted_element.find_next(
                                            "td").text if capital_contracted_element else ""
                                        capital_paid_in = capital_paid_in_element.find_next(
                                            "td").text if capital_paid_in_element else ""
                                        shares = shares_element.find_next(
                                            "td").text if shares_element else ""
                                        if name_element is not None:
                                            people_detail.append({
                                                "designation": "founder",
                                                "name": name,
                                                'meta_detail': {
                                                    "capital_contracted": capital_contracted,
                                                    "capital_paid_in": capital_paid_in,
                                                },

                                                "shares": shares
                                            })

                                        Activities = driver.find_element(
                                            By.XPATH, '//a[text()="Activities"]')
                                        Activities.click()
                                        soup_activities = BeautifulSoup(
                                            driver.page_source, "html.parser")
                                        tables = soup_activities.find_all(
                                            "table", class_="vertical2")

                                        for table in tables:
                                            activity = table.find(
                                                "td", string="Activity")
                                            activity_code = table.find(
                                                "td", string="Activity code")
                                            if activity and activity_code:
                                                activity_text = activity.find_next(
                                                    "td").text
                                                activity_code_text = activity_code.find_next(
                                                    "td").text
                                                data.append({
                                                            "activity": activity_text,
                                                            "activity code": activity_code_text,
                                                            })

                                        additional_detail.append({
                                            "type": "business_activity_info",
                                            "data": data
                                        })

                                        time.sleep(5)

                                        founder_participation_in_capita = []
                                        unique_names = set()

                                        Capital = driver.find_element(
                                            By.XPATH, '//a[text()="Capital"]')
                                        Capital.click()
                                        soup_capital = BeautifulSoup(
                                            driver.page_source, "html.parser")
                                        table1_data = {}
                                        founder_participation_in_capita = []
                                        table1 = soup_capital.find(
                                            'div', {'class': 'grupa', 'id': 'R15692922872141724'})
                                        if table1:
                                            capital_elements = table1.find_all(
                                                'td', class_='L')
                                            for element in capital_elements:
                                                key = element.get_text(
                                                    strip=True)
                                                value = element.find_next(
                                                    'td').get_text(strip=True)
                                                table1_data[key] = value

                                            # Check if there is any data in table1_data
                                            if any(table1_data.values()):
                                                founder_participation_in_capita.append({
                                                    "capital": table1_data.get("Capital (total)", ''),
                                                    "capital_in_money": table1_data.get("Capital (in money)", ''),
                                                    "capital_in_rights": table1_data.get("Capital (in rights)", ''),
                                                    "capital_in_assets": table1_data.get("Capital (in assets)", '')
                                                })

                                        table2 = soup_capital.find(
                                            'div', {'id': 'report_15702916208158707_catch'})
                                        if table2:
                                            # Find all tables within the selected div
                                            tables = table2.find_all('table')
                                            for table in tables:
                                                rows = table.find_all('tr')
                                                info = {}
                                                for row in rows:
                                                    cells = row.find_all('td')
                                                    if len(cells) == 2:
                                                        key = cells[0].text.strip(
                                                        )
                                                        value = cells[1].text.strip(
                                                        )
                                                        info[key] = value

                                                # Check if there is any data in info
                                                if info and any(info.values()):
                                                    name = info.get(
                                                        "Founder (Basic data)", '')

                                                    if name not in unique_names:
                                                        founder_participation_in_capita.append({
                                                            "name": name,
                                                            "capital": info.get("Capital (total)", ''),
                                                            "capital_in_money": info.get("Capital (in money)", ''),
                                                            "capital_in_rights": info.get("Capital (in rights)", ''),
                                                            "capital_in_assets": info.get("Capital (in assets)", ''),
                                                        })
                                                        unique_names.add(name)

                                        if founder_participation_in_capita:
                                            additional_detail.append({
                                                "type": "founder_participation_in_capital",
                                                'data': founder_participation_in_capita
                                            })

                                        OBJ = {
                                            "registration_number": registration_number,
                                            "name": general_name,
                                            "type": legal_form,
                                            "abbreviation": abbreviation,
                                            "status": status,
                                            "unique_id": unique_identification_number,
                                            "cutoms_number": customs_number,
                                            "addresses_detail": [
                                                {
                                                    "type": "general_address",
                                                    "address": address

                                                }
                                            ],
                                            "additional_detail": additional_detail,
                                            "people_detail": people_detail

                                        }
                                        OBJ = Bosnia_and_Herzegovina_crawler.prepare_data_object(
                                            OBJ)
                                        ENTITY_ID = Bosnia_and_Herzegovina_crawler.generate_entity_id(
                                            company_name=OBJ['name'], reg_number=OBJ['registration_number'])
                                        NAME = OBJ['name'].replace("%", "%%")
                                        BIRTH_INCORPORATION_DATE = ""
                                        ROW = Bosnia_and_Herzegovina_crawler.prepare_row_for_db(
                                            ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                                        Bosnia_and_Herzegovina_crawler.insert_record(
                                            ROW)
                                    except:
                                        print("Data is empty")

                                    try:
                                        search_result = driver.find_element(
                                            By.XPATH, '//a[text()="Results of Basic Search"]')
                                        search_result.click()
                                    except:
                                        search_result = driver.find_element(
                                            By.XPATH, '//a[text()="Nazad"]')
                                        search_result.click()

                    try:
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//td//a[text()="Naprijed"]')))
                        next_button.click()

                    except TimeoutException:
                        print("No 'Next Page' link found. Exiting the loop.")
                        break

                basic_search = driver.find_element(
                    By.XPATH, '//a[text()="Basic Search"]')
                basic_search.click()

        Bosnia_and_Herzegovina_crawler.end_crawler()
        log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
        Bosnia_and_Herzegovina_crawler.db_log(log_data)


except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    Bosnia_and_Herzegovina_crawler.db_log(log_data)
