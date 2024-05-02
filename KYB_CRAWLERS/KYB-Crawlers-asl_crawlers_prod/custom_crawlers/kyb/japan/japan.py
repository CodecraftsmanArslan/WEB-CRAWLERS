"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import math
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
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

meta_data = {
    'SOURCE': 'National Tax Agency (NTA)',
    'COUNTRY': 'Japan',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.houjin-bangou.nta.go.jp/kensaku-kekka.html",
                      "Source Description": "The National Tax Agency (NTA) in Japan is responsible for managing the corporate number system and its implementation. The corporate number is a unique identifier assigned to companies and organizations for administrative and tax purposes. "},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.houjin-bangou.nta.go.jp/kensaku-kekka.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Japan Official Registry" 
}

japan_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0,size=(800,600))
display.start()

URL = "https://www.houjin-bangou.nta.go.jp/kensaku-kekka.html"
selenium_helper = japan_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=False, timeout=300)
action = ActionChains(driver=driver)

with open("post_codes.csv") as df:
    data = df.readlines()

def skip_pages():
    if len(ARGUMENT) > 2:
        print(f"Skipping to page No: {ARGUMENT[2]}")
        for i in range(int(ARGUMENT[2]) - 1):
            try:
                next_page_element = driver.find_element(By.CLASS_NAME, "next")
                anchor_tag = next_page_element.find_element(By.TAG_NAME, "a")
                action.scroll_to_element(anchor_tag).move_to_element(anchor_tag).click().perform()
                time.sleep(3)
                print(f"Page no: {i+1} skipped")
            except NoSuchElementException:
                print(f"Next page button not found!")
                continue

def crawl():
    driver.get(url=URL)
    time.sleep(15)
    search_by_id_button = driver.find_element(By.XPATH, '//label[text()="郵便番号で検索"]')
    search_by_id_button.click()
    flag = True
    for post_code in data[1:]:
        code = int(post_code.replace("\n", "").strip())
        if len(ARGUMENT) > 1:
            if code != int(ARGUMENT[1]) and flag:
                continue
            else:
                flag = False
        search_field = driver.find_element(By.ID, 'zip_num')
        search_field.send_keys(code)
        search_field.send_keys(Keys.RETURN)
        time.sleep(5)
        if len(ARGUMENT) > 1:
            if code == int(ARGUMENT[1]):
                skip_pages()
        get_data(code=code)

def get_data(code):
        
    total_results = driver.find_element(By.XPATH, '//p[@class="srhResult"]/strong').text
    if int(total_results) % 10 == 0:
        no_of_pages = math.floor(int(total_results)/10)
    else:
        no_of_pages = math.floor(int(total_results)/10) + 1

    if len(ARGUMENT) > 2 and code == int(ARGUMENT[1]):
        page_number = int(ARGUMENT[2])
    else:
        page_number = 1

    for i in range(no_of_pages - page_number + 1):

        if len(ARGUMENT) > 1:
            print(f"Scrapping page number: {page_number} for postal code: {code}")
        else:
            print(f"Scrapping page number: {page_number} for postal code: {code}")

        all_companies = len(driver.find_elements(By.XPATH, '//a[text()="履歴等"]'))

        for index in range(all_companies):
            all_companies = driver.find_elements(By.XPATH, '//a[text()="履歴等"]')
            the_company = all_companies[index]
            action.scroll_to_element(the_company).move_to_element(the_company).click().perform()
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            registration_number = soup.find("dt", string="法人番号")
            registration_number = registration_number.find_next_sibling().text if registration_number else ""
            name_ = soup.find("dt", string="商号又は名称")
            name_ = name_.find_next_sibling().text if name_ is not None else ""
            aliases = soup.find("dt", string="商号又は名称（フリガナ）")
            aliases = aliases.find_next_sibling().text if aliases is not None else ""
            address = soup.find("dt", string="本店又は主たる事務所の所在地")
            address = address.find_next_sibling().text if address is not None else ""
            registration_date = soup.find("span", string="法人番号指定年月日")
            registration_date = registration_date.find_next_sibling().text if registration_date is not None else ""
            update_date = soup.find("dt", string="最終更新年月日")
            update_date = update_date.find_next_sibling().text if update_date is not None else ""

            old_data = []

            try:
                history_div = soup.find("ol", class_="corpHistory1")
                div_data = history_div.find_all("dd")
                for item in div_data:
                    date_of_occurance = item.find("span", string="事由発生年月日")
                    date_of_occurance = date_of_occurance.find_next_sibling().text if date_of_occurance is not None else ""
                    reason_for_change = item.find("span", string="変更の事由")
                    reason_for_change = reason_for_change.find_next_sibling().text if reason_for_change is not None else ""
                    old_name = item.find("span", string="旧情報")
                    old_name = old_name.find_next_sibling().text.replace(" ", "").replace("\n", " ").strip() if old_name is not None else ""

                    the_dict = {
                        "date": date_of_occurance,
                        "reason_for_change": reason_for_change,
                        "old_name": old_name
                    }

                    if date_of_occurance or reason_for_change or old_name:
                        old_data.append(the_dict)

            except:
                old_data = []

            OBJ = {
                "registration_number": registration_number,
                "name": name_,
                "aliases": aliases,
                "registration_date": registration_date,
                "update_date": update_date,
                "additional_detail": [
                    {
                        "type": "change_history_information",
                        "data": old_data
                    }
                ],
                "addresses_detail": [
                    {
                        "type": "general_address",
                        "address": address
                    }
                ]
            }

            OBJ = japan_crawler.prepare_data_object(OBJ)
            ENTITY_ID = japan_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
            BIRTH_INCORPORATION_DATE = ''
            ROW = japan_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
            japan_crawler.insert_record(ROW)

            driver.back()
            time.sleep(2)
            try:
                test_company = driver.find_element(By.XPATH, '//a[text()="履歴等"]').text
            except:
                driver.back()
                time.sleep(2)

        time.sleep(2)
        try:
            page_number += 1
            next_page_element = driver.find_element(By.CLASS_NAME, "next")
            anchor_tag = next_page_element.find_element(By.TAG_NAME, "a")
            action.scroll_to_element(anchor_tag).move_to_element(anchor_tag).click().perform()
            time.sleep(5)
        except NoSuchElementException:
            print("No more pages")
            break

    driver.get(url=URL)
    time.sleep(2)
    search_by_id_button = driver.find_element(By.XPATH, '//label[text()="郵便番号で検索"]')
    search_by_id_button.click()

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    japan_crawler.db_log(log_data)
    japan_crawler.end_crawler()
    display.stop()


except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    japan_crawler.db_log(log_data)
    display.stop()