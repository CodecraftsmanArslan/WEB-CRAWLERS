"""Import required library"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from multiprocessing import Process, freeze_support
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from CustomCrawler import CustomCrawler
from pyvirtualdisplay import Display
from datetime import datetime
import traceback
import sys
import time
import os
import traceback
import time
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from load_env.load_env import ENV

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENTS = sys.argv
FILE_PATH = os.path.dirname(os.getcwd()) + "/italy"

meta_data = {
    'SOURCE': 'Italian Business Register',
    'COUNTRY': 'Italy',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://italianbusinessregister.it/en/home",
                      "Source Description": "The Italian Business Register is a public register which, as already provided for within the Civil Code, has been fully implemented since 1996, by the Law in relation to the reorganisation of the Chambers of Commerce and with the subsequent Implementing Regulation."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://italianbusinessregister.it/en/home'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Italy Official Registry",
}

italy_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

display = Display(visible=0, size=(800, 600))
display.start()

selenium_helper = italy_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(
    headless=False, Nopecha=True, timeout=120, proxy=True)
action = ActionChains(driver=driver)
wait = WebDriverWait(driver, 30)

alphabets = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
             "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "."
             "0","1","2","3","4","5","6","7","8","9", "10","12"]

#Detects if there is any captcha at the begening of search
def find_and_solve_start_captcha():
    if len(driver.find_elements(By.XPATH, '//iframe[@title="recaptcha challenge expires in two minutes"]')) > 0:
        check_iframe = driver.find_element(
            By.XPATH, '//iframe[@title="recaptcha challenge expires in two minutes"]')
        driver.switch_to.frame(check_iframe)
        check = driver.find_element(
            By.XPATH, '//body').get_attribute("style")
        if check:
            print("Start Captcha Found!")
            while True:
                try:
                   WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//li/a[contains(text(), "Next")]')))
                   print("Start Captcha Solved!!")
                   return True
                except TimeoutException:
                   print("Still trying to solve start captcha...")
                   time.sleep(10)
                   continue
        else:
            print("Start Captcha not found!")
            driver.switch_to.default_content()
            return False
        

# It will see if there is any captcha, if yes, it will call another function to solve it.
def find_captcha():
    if len(driver.find_elements(By.XPATH, '//iframe[@title="recaptcha challenge expires in two minutes"]')) > 0:
        check_iframe = driver.find_element(
            By.XPATH, '//iframe[@title="recaptcha challenge expires in two minutes"]')
        driver.switch_to.frame(check_iframe)
        check = driver.find_element(
            By.XPATH, '//body').get_attribute("style")
        if check:
            print("Captcha Found!")
            driver.switch_to.default_content()
            iframe_element = driver.find_element(
                By.XPATH, '//iframe[@title="reCAPTCHA"]')
            driver.switch_to.frame(iframe_element)
            solve_captcha()
            return True
        else:
            print("Captcha not found!!")
            driver.switch_to.default_content()
            return False

# It solves the captcha by going in the iframe.
def solve_captcha():
    try:
        captcha_not_solved = True
        captcha_element_classes = driver.find_element(
            By.XPATH, '//span[@role="checkbox"]')
        captcha_element_classes = captcha_element_classes.get_attribute(
            "class")
        if "recaptcha-checkbox-checked" not in captcha_element_classes:
            print('trying to resolve captcha...')
            max_retries = 0
            while captcha_not_solved and max_retries < 10:
                time.sleep(5)
                captcha_element_classes = driver.find_element(
                    By.XPATH, '//span[@role="checkbox"]').get_attribute("class")
                if "recaptcha-checkbox-checked" not in captcha_element_classes:
                    print("Still Trying...")
                    max_retries += 1
                    time.sleep(12)
                    continue
                else:
                    captcha_not_solved = False
            if max_retries == 10 or "CAPTCHA check failed." in driver.page_source:
                print("Stuck on still trying!")
                driver.refresh()
                time.sleep(1)
                print("Refreshing the page")
                find_captcha()
        driver.switch_to.default_content()
        print("Captcha has been Solved!")
        time.sleep(2)
    except Exception as e:
        driver.switch_to.default_content()
        print("Captcha not found.")


# Check if the data is not crawled, it opens the data URL, scrape the data and store it in Database.
def get_data(company_links, pg_no, let):
    with open(f"{FILE_PATH}/crawled_records.txt", "a") as crawled_records:
        crawled_records.write(
            f"Scraping page number {pg_no} of letter {let}\n")
    for url in company_links:
        driver.get(url=url)
        time.sleep(2)
        try:
            name_ = driver.find_element(
                By.XPATH, '//*[@id="p_p_id_risultatiricercaimprese_WAR_ricercaPIportlet_"]/div/div/div[2]/div[2]/div[1]/div[1]/div[2]').text.strip()
        except NoSuchElementException:
            name_ = ""
        try:
            address_ = driver.find_element(
                By.XPATH, '//*[@id="p_p_id_risultatiricercaimprese_WAR_ricercaPIportlet_"]/div/div/div[2]/div[2]/div[1]/div[2]/div[2]').text.replace("Show map", "").strip()
        except NoSuchElementException:
            address_ = ""
        try:
            type_ = driver.find_element(
                By.XPATH, '//*[@id="p_p_id_risultatiricercaimprese_WAR_ricercaPIportlet_"]/div/div/div[2]/div[2]/div[1]/div[4]/div[2]').text.strip()
        except NoSuchElementException:
            type_ = ""
        try:
            show_button = driver.find_element(
                By.XPATH, '//a/b[contains(text(), "Show")]')
            show_button.click()
            time.sleep(2)
            email_ = driver.find_element(
                By.XPATH, '//div/div[@id = "myTab"]').text.strip()
        except NoSuchElementException:
            email_ = ""

        OBJ = {
            "name": name_.replace('"/', '').replace("%", "%%"),
            "type": type_.replace("%", "%%"),
            "addresses_detail": [
                {
                    "type": "general_address",
                    "address": address_.replace("%", "%%")
                }
            ],
            "contacts_detail": [
                {
                    "type": "email",
                    "value": email_.replace("%", "%%")
                }
            ]
        }

        OBJ = italy_crawler.prepare_data_object(OBJ)
        ENTITY_ID = italy_crawler.generate_entity_id(OBJ)
        BIRTH_INCORPORATION_DATE = ''
        ROW = italy_crawler.prepare_row_for_db(
            ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
        italy_crawler.insert_record(ROW)

    try:
        close_button = driver.find_element(
            By.XPATH, '//div/button[contains(text(), "Close")]')
        close_button.click()
        time.sleep(2)
        back_button = driver.find_element(
            By.XPATH, '//div[@class = "span12"]/span/a')
        back_button.click()
        time.sleep(2)
    except:
        back_button = driver.find_element(
            By.XPATH, '//div[@class = "span12"]/span/a')
        wait.until(EC.element_to_be_clickable(back_button))
        back_button.click()
        time.sleep(2)

# After 250 pages a different type of captcha had to be solved. So this functions solves that captcha and proceed to next page.
def internal_captcha():
    check = find_captcha()
    if check == True:
        captcha_button = driver.find_element(
            By.CLASS_NAME, 'btn-captcha')
        driver.execute_script(
            "arguments[0].click();", captcha_button)
        time.sleep(3)
        return True
    else:
        print("No internal captcha!!")
        return False


# If the crawler is resumed, it will skip all the pages already crawled.
def skip_pages():
    start_number = int(ARGUMENTS[3]) if len(ARGUMENTS) > 3 else 1
    if start_number != 1:
        for i in range(start_number-1):
            try:
                time.sleep(3)
                print("Skipping page number: ", i+1)
                next_button = driver.find_element(
                    By.XPATH, '//li/a[contains(text(), "Next")]')
                href_ = next_button.get_attribute("href")
                if href_ != "javascript:;":
                    driver.execute_script(
                        "arguments[0].click();", next_button)
                else:
                    captcha_report = internal_captcha()
                    if captcha_report != False:
                        time.sleep(5)
                        next_button = driver.find_element(
                            By.XPATH, '//li/a[contains(text(), "Next")]')
                        driver.execute_script(
                            "arguments[0].click();", next_button)
                    else:
                        break
            except WebDriverException:
                break
    page_count = start_number
    time.sleep(5)
    return page_count

# The default page show 10 records per page, this will change it to 75 records per page.
def increase_page_size():
    try:
        time.sleep(3)
        records_per_page = driver.find_element(
            By.XPATH, '//div[@class="lfr-pagination-delta-selector"]//a')
        records_per_page.click()
        time.sleep(2)
        seventy_five_records_per_page = driver.find_element(
            By.XPATH, '//ul[@role="menu"]/li[6]')
        seventy_five_records_per_page.click()
    except:
        driver.refresh()
        time.sleep(5)
        records_per_page = driver.find_element(
            By.XPATH, '//div[@class="lfr-pagination-delta-selector"]//a')
        records_per_page.click()
        time.sleep(2)
        seventy_five_records_per_page = driver.find_element(
            By.XPATH, '//ul[@role="menu"]/li[6]')
        seventy_five_records_per_page.click()


# opens up the official website and opens the search page, then skip to the page number passed as argument (Resume page).
def crawl(letters):
    skip_page_flag = True
    for letter in letters[alphabets.index(start_letter):alphabets.index(end_letter)]:
        driver.get("https://italianbusinessregister.it/en/home")
        time.sleep(2)
        print("Website Opened.")
        if len(driver.find_elements(By.ID, 'didomi-notice-agree-button')) > 0:
            agree_button = driver.find_element(
                By.ID, 'didomi-notice-agree-button')
            agree_button.click()
            time.sleep(2)
        search_field = driver.find_element(By.ID, 'inputSearchField')
        search_field.send_keys(letter)
        search_button = driver.find_element(By.ID, 'btnSearchHomePage')
        search_button.click()
        time.sleep(3)
        print("Search Initiated.")
        find_and_solve_start_captcha()
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH, '//li/a[contains(text(), "Next")]')))
        check = driver.find_elements(
            By.XPATH, '//a[@class="dropdown-toggle direction-down max-display-items-15 btn"]')[1].get_attribute("title")
        if check != "75 Items per page":
            increase_page_size()
            print("Now showing 75 records per pgae.")
        time.sleep(5)
        page_number = skip_pages() if skip_page_flag else 1
        skip_page_flag = False
        stale_check = internal_captcha()
        if stale_check == True:
            print("Refreshing the page to Avoid Stale Exception...")
            driver.refresh()
            time.sleep(2)

        while True:
            print(f"Scraping page number {page_number} of letter {letter}")
            check = driver.find_elements(
                By.XPATH, '//a[@class="dropdown-toggle direction-down max-display-items-15 btn"]')[1].get_attribute("title")
            if check != "75 Items per page":
                increase_page_size()
                print("Now showing 75 records per pgae.")
            time.sleep(5)
            stale_check = internal_captcha()
            if stale_check == True:
                print("Refreshing the page to Avoid Stale Exception...")
                driver.refresh()
                time.sleep(2)
            list_of_companies = driver.find_elements(
                By.XPATH, '//table//tr/td//a[1]')
            company_urls = []
            for n in list_of_companies:
                company_urls.append(n.get_attribute("href"))
            time.sleep(1)
            get_data(company_links=company_urls, pg_no=page_number, let=letter)
            time.sleep(3)
            next_button = driver.find_element(
                By.XPATH, '//li/a[contains(text(), "Next")]')
            href_ = next_button.get_attribute("href")
            if href_ != "javascript:;":
                driver.execute_script("arguments[0].click();", next_button)
                page_number += 1
            else:
                captcha_report = internal_captcha()
                if captcha_report != False:
                    time.sleep(5)
                    next_button = driver.find_element(
                        By.XPATH, '//li/a[contains(text(), "Next")]')
                    driver.execute_script(
                        "arguments[0].click();", next_button)
                    page_number += 1
                else:
                    print("Initiating search for next letter (If any)...")
                    break


try:
    start_letter = ARGUMENTS[1] if len(ARGUMENTS) > 1 else alphabets[0]
    end_letter = ARGUMENTS[2] if len(ARGUMENTS) > 2 else alphabets[-1]

    crawl(alphabets)
    log_data = {"status": 'success',
                "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    italy_crawler.db_log(log_data)
    italy_crawler.end_crawler()
    display.stop()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": 'fail',
                "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    italy_crawler.db_log(log_data)
    display.stop()
