"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from datetime import datetime
from pyvirtualdisplay import Display
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
arguments = sys.argv

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
wait = WebDriverWait(driver, 10)

# It will see if there is any captcha and then solve it.


def find_solve_captcha(browser):
    try:
        iframe_element = browser.find_element(
            By.XPATH, '//iframe[@title="reCAPTCHA"]')
        browser.switch_to.frame(iframe_element)
        time.sleep(1)
        captcha_not_solved = True
        captcha_element_classes = driver.find_element(
            By.XPATH, '//span[@role="checkbox"]')
        captcha_element_classes = captcha_element_classes.get_attribute(
            "class")
        if "recaptcha-checkbox-checked" not in captcha_element_classes:
            print("Captcha Found!")
            print('trying to resolve captcha...')
            while captcha_not_solved:
                captcha_element_classes = driver.find_element(
                    By.XPATH, '//span[@role="checkbox"]').get_attribute("class")
                if "recaptcha-checkbox-checked" not in captcha_element_classes:
                    print("Still Trying...")
                    time.sleep(3)
                    continue
                else:
                    captcha_not_solved = False
        else:
            print("No Captcha Found")
            browser.switch_to.default_content()

        browser.switch_to.default_content()
        print("Captcha has been Solved!")
        time.sleep(2)
    except Exception as e:
        browser.switch_to.default_content()
        print("Captcha not found.")

# Check if the data is not crawled, it opens the data URL, scrape the data and store it in Database.


def get_data(company_links):
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

        print(OBJ)

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

# If the crawler is resumed, it will skip all the pages already crawled.


def skip_pages():
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
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
                    try:
                        internal_captcha()
                    except:
                        next_page = driver.find_element(
                            By.XPATH, '//li/a[contains(text(), "Next")]')
                        driver.execute_script(
                            "arguments[0].click();", next_page)
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    page_count = start_number
    time.sleep(5)
    return page_count

# # After 250 pages a different type of captcha had to be solved. So this functions solves that captcha and proceed to next page.


def internal_captcha():
    captcha_element = driver.find_element(
        By.CLASS_NAME, "g-recaptcha")
    if captcha_element:
        print("Captcha Found!")
        find_solve_captcha(driver)
        captcha_button = driver.find_element(
            By.CLASS_NAME, 'btn-captcha')
        driver.execute_script(
            "arguments[0].click();", captcha_button)
        next_button = driver.find_element(
            By.XPATH, '//li/a[contains(text(), "Next")]')
        driver.execute_script(
            "arguments[0].click();", next_button)

# opens up the official website and opens the search page, then skip to the page number passed as argument (Resume page) and call the get_data function to store the data in database.


def crawl():
    driver.get("https://italianbusinessregister.it/en/home")
    time.sleep(2)
    agree_button = driver.find_element(By.ID, 'didomi-notice-agree-button')
    agree_button.click()
    time.sleep(2)
    search_field = driver.find_element(By.ID, 'inputSearchField')
    search_field.send_keys("A")
    search_button = driver.find_element(By.ID, 'btnSearchHomePage')
    search_button.click()
    find_solve_captcha(browser=driver)

    WebDriverWait(driver, 120).until(EC.presence_of_element_located(
        (By.XPATH, '//li/a[contains(text(), "Next")]')))

    no_of_pages = int(driver.find_element(
        By.XPATH, '//span[@class = "risTot"]').text.replace(".", ""))

    page_number = skip_pages()

    for i in range(page_number, no_of_pages):
        print(f"Scraping page number {i} of letter A")
        list_of_companies = driver.find_elements(
            By.XPATH, '//*[@id="p_p_id_risultatiricercaimprese_WAR_ricercaPIportlet_"]/div/div/div/div/div/div/div[3]/div/table/tbody/tr/td/div/a[1]')
        company_urls = []
        for n in list_of_companies:
            company_urls.append(n.get_attribute("href"))
        time.sleep(1)
        get_data(company_links=company_urls)
        time.sleep(3)
        try:
            next_button = driver.find_element(
                By.XPATH, '//li/a[contains(text(), "Next")]')
            href_ = next_button.get_attribute("href")
            if href_ != "javascript:;":
                driver.execute_script("arguments[0].click();", next_button)
            else:
                try:
                    internal_captcha()
                except:
                    next_page = driver.find_element(
                        By.XPATH, '//li/a[contains(text(), "Next")]')
                    driver.execute_script(
                        "arguments[0].click();", next_page)
        except:
            next_page = driver.find_element(
                By.XPATH, '//li/a[contains(text(), "Next")]')
            driver.execute_script("arguments[0].click();", next_page)
        time.sleep(2)


try:
    crawl()
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
