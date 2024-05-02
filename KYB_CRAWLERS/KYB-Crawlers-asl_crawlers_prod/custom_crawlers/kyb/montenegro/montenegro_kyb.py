"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'Central Register of Business Entities',
    'COUNTRY' : 'Montenegro',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "http://www.pretraga.crps.me/", 
                        "Source Description": "Registration of business entities in Montenegro is carried out in the Central Register of Business Entities.In order to improve the business environment, within the framework of the regulatory reform, a one-stop system for the registration of business entities was introduced."},
    'URL' : 'http://www.pretraga.crps.me/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Montenegro'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'http://www.pretraga.crps.me:8083/Home/TraziSubmit'

display = Display(visible=0,size=(800,600))
display.start()
montenegro_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  montenegro_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=True)

def get_next_sibling_td(soup, keyword):
    try:
        return soup.find('td', string=keyword).find_next_sibling('td').text.strip()
    except:
        return ""
    
def get_data(soup):
    item = {}
    additional_detail = []
    addresses_detail = []
    contacts_detail = []
    people_detail = []
    fillings_detail = []
    item['registration_number'] = get_next_sibling_td(soup, 'Registarski broj:')
    item['pib_number'] = get_next_sibling_td(soup, 'PIB/Matični broj:')
    item['change_number'] = get_next_sibling_td(soup, 'Broj promjene:')
    item['name'] = get_next_sibling_td(soup, 'Puni naziv:')
    item['aliases'] = get_next_sibling_td(soup, 'Skraćeni naziv:')
    item['type'] = get_next_sibling_td(soup, 'Oblik organizovanja:')
    activity_code = get_next_sibling_td(soup, 'Šifra djelatnosti:')
    detail = get_next_sibling_td(soup, 'Naziv djelatnosti:')
    additional_detail.append({
        'type': 'activities_info',
        'data': [{
            'activity_code': activity_code,
            'detail': detail
        }]
    })
    headquarters_address = get_next_sibling_td(soup, 'Adresa sjedišta:')
    addresses_detail.append({
        'type': 'headquarters',
        'address': headquarters_address
    })
    item['jurisdiction'] = get_next_sibling_td(soup, 'Mjesto sjedišta:')
    postal_address = get_next_sibling_td(soup, 'Adresa prijema službene pošte:')
    addresses_detail.append({
        'type': 'postal_address',
        'address': postal_address
    })
    item['mail_receipt_location'] = get_next_sibling_td(soup, 'Mjesto prijema službene pošte:')
    item['registration_date'] = get_next_sibling_td(soup, 'Datum osnivanja:').replace('.', '-')
    item['change_date'] = get_next_sibling_td(soup, 'Datum promjene:').replace('.', '-')
    web_address = get_next_sibling_td(soup, 'Web adresa:')
    email_address = get_next_sibling_td(soup, 'Email adresa:')
    phone_number = get_next_sibling_td(soup, 'Telefon:')
    item['status'] = get_next_sibling_td(soup, 'Status:')
    contacts_detail.append({'type': 'website', 'value': web_address})
    contacts_detail.append({'type': 'email', 'value': email_address})
    contacts_detail.append({'type': 'phone_number', 'value': phone_number})
    item['capital'] = get_next_sibling_td(soup, 'Ukupan kapital:')

    faces_in_society_tbl = soup.find('table', attrs={'id': 'tblLicaUDrustvu'})
    if faces_in_society_tbl is not None:
        tbody = faces_in_society_tbl.find('tbody')
        if tbody is not None:
            trs = tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                people_detail.append({
                    'name': f"{tds[0].text} {tds[1].text}",
                    'designation': tds[2].text,
                    'meta_detail': {
                        'responsibility': tds[3].text,
                        'shares': tds[4].text
                    }
                })

    parts_of_society = []
    parts_of_society_tlb = soup.find('table', attrs={'id': 'tblDjeloviDrustva'})
    if parts_of_society_tlb is not None:
        tbody = parts_of_society_tlb.find('tbody')
        if tbody is not None:
            trs = tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) >= 6:
                    parts_of_society.append({
                        'name': tds[0].text,
                        'address': tds[1].text,
                        'place': tds[2].text,
                        'jurisdiction': tds[3].text,
                        'activity': tds[4].text,
                        'representative': tds[5].text
                    })
            if len(parts_of_society) > 0:
                additional_detail.append({
                    'type': 'activity_in_society_info',
                    'data': parts_of_society
                })

    branch_offices = []
    branch_offices_tbl = soup.find('table', attrs={'id': 'tblPodruznice'})
    if branch_offices_tbl is not None:
        tbody = branch_offices_tbl.find('tbody')
        if tbody is not None:
            trs = tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) >= 6:
                    branch_offices.append({
                        'name': tds[0].text,
                        'address': tds[1].text,
                        'place': tds[2].text,
                        'jurisdiction': tds[3].text,
                        'activity': tds[4].text,
                        'representative': tds[5].text
                    })
            if len(branch_offices) > 0:
                additional_detail.append({
                    'type': 'branch_offices_info',
                    'data': branch_offices
                })

    if item['registration_number'] != "" and item['change_number'] != "":
        item['registration_document'] = f"http://www.pretraga.crps.me:8083/Home/GenerisiIzvod?REG_BROJ={item['registration_number']}&BROJ_PROMJENE={item['change_number']}&Param=0"

    additional_detail.append({
        'type': 'financial_records',
        'data': [{
            'url': 'https://eprijava.tax.gov.me/TaxisPortal'
        }]
    })

    item['additional_detail'] = additional_detail
    item['addresses_detail'] = addresses_detail
    item['contacts_detail'] = contacts_detail
    item['people_detail'] = people_detail
    item['fillings_detail'] = fillings_detail
    return item

def wait_for_captcha_to_be_solved(browser):
    while True:
        iframe_element = browser.find_element(By.XPATH, '//*[@id="frmPretraga"]//iframe[@title="reCAPTCHA"]')
        browser.switch_to.frame(iframe_element)
        time.sleep(3)
        if len(browser.find_elements(By.CLASS_NAME,"recaptcha-checkbox-checked")) > 0:
            browser.switch_to.default_content()
            print("Captcha has been Solved")
            return browser 
        browser.switch_to.default_content()

try:
    wait = WebDriverWait(driver, 20)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 10000000
    for reg_num in range(start, 59999999):
        print(f"Record No: {reg_num}")
        driver.get(BASE_URL)
        input_box = wait.until(EC.visibility_of_element_located((By.ID, 'REG_BR_brzo')))
        print("wait for captcha to be resolved")
        wait_for_captcha_to_be_solved(driver)
        input_box.clear()
        input_box.send_keys(reg_num)
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'submit')))
        submit_btn.click()
        try:
            record_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="myTable1"]/tbody/tr/td[1]/a')))
            record_btn.click()
        except:
            continue
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[1])
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = get_data(soup)
        ENTITY_ID = montenegro_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
        BIRTH_INCORPORATION_DATE = ''
        DATA = montenegro_crawler.prepare_data_object(data)
        ROW = montenegro_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
        montenegro_crawler.insert_record(ROW)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    montenegro_crawler.db_log(log_data)
    montenegro_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    montenegro_crawler.db_log(log_data)
display.stop()
