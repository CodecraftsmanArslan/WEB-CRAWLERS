"""Import required library"""
import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
import ssl
import time
from helpers.load_env import ENV
from random import randint
from dateutil import parser
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENTS = sys.argv
TIMEOUT = 10

meta_data = {
    'SOURCE' :'Corporate and Business Registration Department (CBRD)',
    'COUNTRY' : 'Mauritius',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://onlinesearch.mns.mu/", 
                        "Source Description": "The Corporate and Business Registration Department (CBRD) of Mauritius is a government agency responsible for the registration and administration of businesses and corporate entities in Mauritius. It operates under the Ministry of Financial Services and Good Governance."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://onlinesearch.mns.mu/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Mauritius Company Official Registry"
}

mauritius_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = mauritius_crawler.get_selenium_helper()
request_helper = mauritius_crawler.get_requests_helper()

start_number = int(ARGUMENTS[1]) if len(ARGUMENTS) >1 else 16
end_number = 200

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

# proxy_host = "185.48.55.61"
# proxy_port = "6537"

def random_number():
    r_numb = randint(1, 3)
    return r_numb

def crawl(start_number):
    options = Options()
    # options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
    driver = uc.Chrome(options=options)
    driver.get('https://onlinesearch.mns.mu/')
    time.sleep(5)
    for i in range(start_number, end_number):
        random_query = randint(start_number, end_number)
        with open("crawled_record_co.txt", "r") as crawled_records:
            file_contents = crawled_records.read()
            if str(random_query) in file_contents:
                continue
            else:
                with open("crawled_record_co.txt", "a") as crawled_records:
                    crawled_records.write(str(random_query) + "\n")
        search_query = "c" + str(random_query)
        search_field = driver.find_element(By.ID, 'company-partnership-text-field')
        search_field.send_keys(search_query)
        time.sleep(random_number())
        file_radio = driver.find_element(By.ID, 'fileNo')
        file_radio.click()
        time.sleep(random_number())
        search_button = driver.find_element(By.XPATH, '//button[text()=" Search "]')
        search_button.click()
        try:
            error_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="ERROR"]')))
            if error_box:
                print("Bot Detected!!!")
                driver.quit()
                time.sleep(random_number())
                crawl(start_number)
        except:
            try:
                try:
                    cookie_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[text()=" Accept "]')))
                except:
                    cookie_button = ""
                if cookie_button:
                    cookie_button = driver.find_element(By.XPATH, '//button[text()=" Accept "]')
                    cookie_button.click()
                data_view_button = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '//fa-icon[@title="View"]')))
                data_view_button.click()
                time.sleep(random_number())
                WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, 'cdk-accordion-child-1')))
                print(f"Scraping data for {search_query}...")
                time.sleep(random_number())
                get_data(driver=driver)
                time.sleep(random_number())
            except:
                print(f"No record found for {search_query}.")
                driver.refresh()
                time.sleep(random_number())
                continue

def get_data(driver):

    soup = BeautifulSoup(driver.page_source, "html.parser")

    people_details = []
    company_detail_table = soup.find(id="cdk-accordion-child-1")
    file_no = company_detail_table.find("label", string="File No.:")
    file_no = file_no.find_next_sibling().text.strip() if file_no is not None else ""
    name = company_detail_table.find("label", string="Name:")
    name = name.find_next_sibling().text.strip().replace("\n", " ").replace("  ", "") if name is not None else ""
    category = company_detail_table.find("label", string="Category:")
    category = category.find_next_sibling().text.strip() if category is not None else ""
    type_ = company_detail_table.find("label", string="Type:")
    type_ = type_.find_next_sibling().text.strip() if type_ is not None else ""
    office_address = company_detail_table.find("label", string="Registered Office Address:")
    office_address = office_address.find_next_sibling().text.replace("\n", " ").replace("  ", "").strip() if office_address is not None else ""
    registration_date = company_detail_table.find("label", string="Date Incorporated/Registered:")
    if registration_date:
        registration_date = registration_date.find_next_sibling().text.strip()
        registration_date = format_date(registration_date)
    else:
        registration_date = ""

    nature = company_detail_table.find("label", string="Nature:")
    nature = nature.find_next_sibling().text.strip() if nature is not None else ""
    sub_category = company_detail_table.find("label", string="Sub-category:")
    sub_category = sub_category.find_next_sibling().text.strip() if sub_category is not None else ""
    status = company_detail_table.find("label", string="Status:")
    status = status.find_next_sibling().text.strip() if status is not None else ""
    inactive_date = company_detail_table.find("label", string="Defunct Date:")
    if inactive_date:
        inactive_date = inactive_date.find_next_sibling().text.strip() if inactive_date is not None else ""
        inactive_date = format_date(inactive_date)
    else:
        inactive_date = ""

    business_detail_table = soup.find(id="cdk-accordion-child-2")
    bdt_body = business_detail_table.find("tbody")
    bdt_rows = bdt_body.find_all("tr")
    bdt_check = bdt_body.find("tr").find("h4").text.strip() if bdt_body.find("tr").find("h4") is not None else ""
    all_business_data = []
    if len(bdt_rows) > 0 and "No result to display" not in bdt_check:
        for bdt_row in bdt_rows:
            business_registration_number = bdt_row.find("td", {"data-column":"Business Registration No."})
            business_registration_number= business_registration_number.text.strip() if business_registration_number is not None else ""
            business_name = bdt_row.find("td", {"data-column":"Business Name"})
            business_name = business_name.text.strip().replace(".", "") if business_name is not None else ""
            nature_of_business = bdt_row.find("td", {"data-column":"Nature of Business"})
            nature_of_business= nature_of_business.text.strip().replace("\n", " ").replace("  ", "").strip() if nature_of_business is not None else ""
            business_address = bdt_row.find("td", {"data-column":"Business Address"})
            business_address = business_address.text.strip().replace("\n", " ").replace("  ", "") if business_address is not None else ""
            bdt_dict = {
                "registration_number": business_registration_number,
                "name": business_name,
                "nature_of_business": nature_of_business,
                "business_address": business_address
            }
            all_business_data.append(bdt_dict)

        
    share_detail_table = soup.find(id="cdk-accordion-child-3")
    sdt_body = share_detail_table.find("tbody")
    sdt_rows = sdt_body.find_all("tr")
    sdt_check = sdt_body.find("tr").find("h4").text.strip() if sdt_body.find("tr").find("h4") is not None else ""
    all_share_data = []
    if len(sdt_rows) > 0 and "No result to display" not in sdt_check:
        for sdt_row in sdt_rows:
            type_of_shares = sdt_row.find("td", {"data-column":"Type of Shares"}).text.strip().replace("\n", "").replace("  ", "")
            no_of_shares = sdt_row.find("td", {"data-column":"No. of Shares"}).text.strip()
            share_currency = sdt_row.find("td", {"data-column":"Currency"}).text.strip()
            share_capital = sdt_row.find("td", {"data-column":"Stated Capital"}).text.strip()
            amount_unpaid = sdt_row.find("td", {"data-column":"Amount Unpaid"}).text.strip()
            par_value = sdt_row.find("td", {"data-column":"Par Value"}).text.strip()   
            sdt_dict = {
                "share_type": type_of_shares,
                "number_of_shares": no_of_shares,
                "currency": share_currency,
                "capital": share_capital,
                "amount_unpaid": amount_unpaid,
                "par_value": par_value
            }
            all_share_data.append(sdt_dict)

    office_bearer_table = soup.find(id="cdk-accordion-child-5")
    obt_body = office_bearer_table.find("tbody")
    obt_rows = obt_body.find_all("tr")
    obt_check = obt_body.find("tr").find("h4").text.strip() if obt_body.find("tr").find("h4") is not None else ""
    if len(obt_rows) > 0 and "No result to display" not in obt_check:
        for obt_row in obt_rows:
            bearer_position = obt_row.find("td", {"data-column":"Position"}).text.strip()
            bearer_name = obt_row.find("td", {"data-column":"Name"}).text.replace("\n", " ").replace("  ", "").strip()
            bearer_address = obt_row.find("td", {"data-column":"Address"}).text.strip().replace("\n", " ").replace("  ", "")
            bearer_appointed_date = obt_row.find("td", {"data-column":"Appointed Date"}).text.strip()
            
            obt_dict = {
                "designation": bearer_position,
                "name": bearer_name,
                "address": bearer_address,
                "appointment_date": format_date(bearer_appointed_date)
            }
            people_details.append(obt_dict)

    share_holders_table = soup.find(id="cdk-accordion-child-6")
    sht_body = share_holders_table.find("tbody")
    sht_rows = sht_body.find_all("tr")
    sht_check = sht_body.find("tr").find("h4").text.strip() if sht_body.find("tr").find("h4") is not None else ""
    all_shareholder_data = []
    if len(sht_rows) > 0 and "No result to display" not in sht_check:
        for sht_row in sht_rows:
            shareholder_name = sht_row.find("td", {"data-column":"Name"}).text.strip().replace("\n", " ").replace("  ", "")
            sh_number_of_shares = sht_row.find("td", {"data-column":"No. of Shares"}).text.strip()
            sh_type_of_shares = sht_row.find("td", {"data-column":"Type of Shares"}).text.strip().replace("\n", "").replace("  ", "")
            sh_currency = sht_row.find("td", {"data-column":"Currency"}).text.strip()
            sht_dict = {
                "name": shareholder_name,
                "number_of_shares": sh_number_of_shares,
                "type_of_shares": sh_type_of_shares,
                "currency": sh_currency
            }
            all_shareholder_data.append(sht_dict)
    
    annual_return_table = soup.find(id="cdk-accordion-child-7")
    art_body = annual_return_table.find("tbody")
    art_rows = art_body.find_all("tr")
    art_check = art_body.find("tr").find("h4").text.strip() if art_body.find("tr").find("h4") is not None else ""
    fillings_detail = []
    if len(art_rows) > 0 and "No result to display" not in art_check:
        for art_row in art_rows:
            art_return_date = art_row.find("td", {"data-column":"Date of Return"}).text.strip()
            art_meeting_date = art_row.find("td", {"data-column":"Date of Meeting"}).text.strip()
            art_filled_date = art_row.find("td", {"data-column":"Date Filed"}).text.strip()
            art_dict = {
                "date": format_date(art_filled_date),
                "meta_detail": {
                     "return_date": format_date(art_return_date),
                     "meeting_date": format_date(art_meeting_date),
                }
            }
            fillings_detail.append(art_dict)
    
    winding_up_table = soup.find(id="cdk-accordion-child-16")
    wut_body = winding_up_table.find("tbody")
    wut_rows = wut_body.find_all("tr")
    wut_check = wut_body.find("tr").find("h4").text.strip() if wut_body.find("tr").find("h4") is not None else ""
    winding_up_details = []
    if len(wut_rows) > 0 and "No result to display" not in wut_check:
        for wut_row in wut_rows:
            winding_type = wut_row.find("td", {"data-column":"Type"}).text.strip().replace("\n", " ").replace("  ", "")
            wut_start_date = wut_row.find("td", {"data-column":"Start Date"}).text.strip()
            wut_end_date = wut_row.find("td", {"data-column":"End Date"}).text.strip()
            wut_winding_status = wut_row.find("td", {"data-column":"Status"}).text.strip()
            wut_dict = {
                "winding_type": winding_type,
                "start_date": format_date(wut_start_date),
                "end_date": format_date(wut_end_date),
                "winding_status": wut_winding_status
            }
            winding_up_details.append(wut_dict)

    liquidators_table = soup.find(id="cdk-accordion-child-11")
    liq_name = liquidators_table.find("label", string="Name:")
    liq_name = liq_name.find_next_sibling().text.strip() if liq_name is not None else ""
    liq_address = liquidators_table.find("label", string="Address:")
    liq_address = liq_address.find_next_sibling().text.strip() if liq_address is not None else ""
    liq_appointed_date = liquidators_table.find("label", string="Appointed Date:")
    liq_appointed_date = liq_appointed_date.find_next_sibling().text.strip() if liq_appointed_date is not None else ""
    liq_dict = {
        "designation": "liquidator",
        "name": liq_name,
        "address": liq_address,
        "appointment_date": format_date(liq_appointed_date)
    }
    if liq_name:
        people_details.append(liq_dict)

    receivers_table = soup.find(id="cdk-accordion-child-12")
    rec_name = receivers_table.find("label", string="Name:").find_next_sibling().text.strip()
    rec_address = receivers_table.find("label", string="Address:").find_next_sibling().text.strip()
    rec_appointed_date = receivers_table.find("label", string="Appointed Date:").find_next_sibling().text.strip()
    rec_dict = {
        "designation": "receiver",
        "name": rec_name,
        "address": rec_address,
        "appointment_date": format_date(rec_appointed_date)
    }
    if rec_name:
        people_details.append(rec_dict)

    admin_table = soup.find(id="cdk-accordion-child-13")
    admin_name = admin_table.find("label", string="Name:").find_next_sibling().text.strip()
    admin_address = admin_table.find("label", string="Address:").find_next_sibling().text.strip()
    admin_appointed_date = admin_table.find("label", string="Appointed Date:").find_next_sibling().text.strip()
    admin_dict = {
        "designation": "administrator",
        "name": admin_name,
        "address": admin_address,
        "appointment_date": format_date(admin_appointed_date)
    }
    if admin_name:
        people_details.append(admin_dict)


    charges_table = soup.find(id="cdk-accordion-child-14")
    charges_body = charges_table.find("tbody")
    charges_rows = charges_body.find_all("tr")
    charges_check = charges_body.find("tr").find("h4").text.strip() if charges_body.find("tr").find("h4") is not None else ""
    charges_details = []
    if len(charges_rows) > 0 and "No result to display" not in charges_check:
        for charges_row in charges_rows:
            charges_volume = charges_row.find("td", {"data-column":"Volume"}).text.strip()
            charges_amount = charges_row.find("td", {"data-column":"Amount"}).text.strip()
            charges_property = charges_row.find("td", {"data-column":"Property"}).text.strip()
            charges_date_charged = charges_row.find("td", {"data-column":"Date Charged"}).text.strip()
            charges_nature_of_charge = charges_row.find("td", {"data-column":"Nature of Charge"}).text.strip()
            charges_date_filled = charges_row.find("td", {"data-column":"Date Filed"}).text.strip()
            charges_currency = charges_row.find("td", {"data-column":"Currency"}).text.strip()
            charges_dict = {
                "volume": charges_volume,
                "amount": charges_amount,
                "property": charges_property,
                "date_charged": format_date(charges_date_charged),
                "nature_of_charge": charges_nature_of_charge,
                "date": format_date(charges_date_filled),
                "currency": charges_currency
            }
            charges_details.append(charges_dict)

    financial_statement_table = soup.find(id="cdk-accordion-child-9")
    financial_year_ended = financial_statement_table.find("label", string="Financial Year Ended:")
    if financial_year_ended:
        financial_year_ended = financial_year_ended.find_next_sibling().text.strip()
        financial_year_ended = format_date(financial_year_ended)
    fs_approval_date = financial_statement_table.find("label", string="Date Approved:")
    if fs_approval_date:
        fs_approval_date = fs_approval_date.find_next_sibling().text.strip()
        fs_approval_date = format_date(fs_approval_date)
    fs_currency_type = financial_statement_table.find("label", string="Currency:")
    fs_currency_type = fs_currency_type.find_next_sibling().text.strip() if fs_currency_type is not None else ""
    fs_unit = financial_statement_table.find("label", string="Unit:")
    fs_unit = fs_unit.find_next_sibling().text.strip() if fs_unit is not None else ""
    fs_turnover = financial_statement_table.find("th", string="Turnover")
    fs_turnover = fs_turnover.find_next_sibling().text.strip() if fs_turnover is not None else ""
    fs_cos = financial_statement_table.find("th", string="Less cost of Sales")
    fs_cos = fs_cos.find_next_sibling().text.strip() if fs_cos is not None else ""
    fs_gprofit = financial_statement_table.find("th", string="Gross Profit")
    fs_gprofit = fs_gprofit.find_next_sibling().text.strip() if fs_gprofit is not None else ""
    fs_other_income = financial_statement_table.find("th", string="Other Income")
    fs_other_income = fs_other_income.find_next_sibling().text.strip() if fs_other_income is not None else ""
    fs_distribution_cost = financial_statement_table.find("th", string=re.compile("Less distribution Costs"))
    fs_distribution_cost = fs_distribution_cost.find_next_sibling().text.strip() if fs_distribution_cost is not None else ""
    fs_admin_cost = financial_statement_table.select_one("#cdk-accordion-child-9 > div > table > tbody > tr:nth-child(6) > td").text.strip()
    fs_other_expenses = financial_statement_table.select_one("#cdk-accordion-child-9 > div > table > tbody > tr:nth-child(7) > td").text.strip()
    fs_finance_cost = financial_statement_table.select_one("#cdk-accordion-child-9 > div > table > tbody > tr:nth-child(8) > td").text.strip()
    fs_pbt = financial_statement_table.find("th", string=re.compile("Profit/Loss Before Tax"))
    fs_pbt = fs_pbt.find_next_sibling().text.strip() if fs_pbt is not None else ""
    fs_tax = financial_statement_table.find("th", string=re.compile("Tax Expense"))
    fs_tax = fs_tax.find_next_sibling().text.strip() if fs_tax is not None else ""
    fs_pat = financial_statement_table.find("th", string=re.compile("Profit/Loss for the period"))
    fs_pat = fs_pat.find_next_sibling().text.strip() if fs_pat is not None else ""
    total_fs_data = []
    fs_dict = {
        "financial_year_ended": financial_year_ended,
        "approval_date": fs_approval_date,
        "currency_type": fs_currency_type,
        "unit": fs_unit,
        "turnover": fs_turnover,
        "cost_of_sale": fs_cos,
        "gross_profit": fs_gprofit,
        "other_income": fs_other_income,
        "distribution_cost": fs_distribution_cost,
        "administration_cost": fs_admin_cost,
        "other_expenses": fs_other_expenses,
        "finance_cost": fs_finance_cost,
        "profit_loss_before_tax": fs_pbt,
        "tax_expense": fs_tax,
        "profit_loss_for_the_period": fs_pat
    }
    if fs_pat != '0':
        total_fs_data.append(fs_dict)
    else:
        total_fs_data = ""

    bs_table = soup.find(id="cdk-accordion-child-10")
    fs_ppe = bs_table.find("th", string=re.compile("Prop, Plant & Equip."))
    fs_ppe = fs_ppe.find_next_sibling().text.strip() if fs_ppe is not None else ""
    fs_investment_prop = bs_table.find("th", string=re.compile("Invest. Properties"))
    fs_investment_prop = fs_investment_prop.find_next_sibling().text.strip() if fs_investment_prop is not None else ""
    fs_intangible_assets = bs_table.find("th", string=re.compile("Intangible Assets"))
    fs_intangible_assets = fs_intangible_assets.find_next_sibling().text.strip() if fs_intangible_assets is not None else ""
    fs_sub_inv = bs_table.find("th", string=re.compile("Invest in Subsidiaries"))
    fs_sub_inv = fs_sub_inv.find_next_sibling().text.strip() if fs_sub_inv is not None else ""
    fs_other_inv = bs_table.find("th", string=re.compile("Other Investments"))
    fs_other_inv = fs_other_inv.find_next_sibling().text.strip() if fs_other_inv is not None else ""
    fs_bio_assets = bs_table.find("th", string=re.compile("Biological Assets"))
    fs_bio_assets = fs_bio_assets.find_next_sibling().text.strip() if fs_bio_assets is not None else ""
    fs_other_assets = bs_table.find_all("th", string=re.compile("Others"))[0]
    fs_other_assets = fs_other_assets.find_next_sibling().text.strip() if fs_other_assets is not None else ""
    fs_total_nca = bs_table.find_all("th", string=re.compile("Total"))[0]
    fs_total_nca = fs_total_nca.find_next_sibling().text.strip() if fs_total_nca is not None else ""
    nca_data = []
    nca_dict = {
        "prop_plant_equip": fs_ppe,
        "invest_properties": fs_investment_prop,
        "intangible_asset": fs_intangible_assets,
        "invest_in_subsidiaries": fs_sub_inv,
        "other_investment": fs_other_inv,
        "biological_assets": fs_bio_assets,
        "others": fs_other_assets,
        "total": fs_total_nca
    }
    if fs_total_nca != '0':
        nca_data.append(nca_dict)
    else:
        nca_data = ""
    

    ca_inventory = bs_table.find("th", string=re.compile("Inventories"))
    ca_inventory = ca_inventory.find_next_sibling().text.strip() if ca_inventory is not None else ""
    ca_trade_rec = bs_table.find("th", string=re.compile("Trade & Other recv."))
    ca_trade_rec = ca_trade_rec.find_next_sibling().text.strip() if ca_trade_rec is not None else ""
    ca_cash_casheq = bs_table.find("th", string=re.compile("Cash & cash eqiv."))
    ca_cash_casheq = ca_cash_casheq.find_next_sibling().text.strip() if ca_cash_casheq is not None else ""
    ca_other_assets = bs_table.find_all("th", string=("Others"))[1]
    ca_other_assets = ca_other_assets.find_next_sibling().text.strip() if ca_other_assets is not None else ""
    ca_total_ca = bs_table.find_all("th", string=("Total"))[1]
    ca_total_ca = ca_total_ca.find_next_sibling().text.strip() if ca_total_ca is not None else ""
    ca_total_assets = bs_table.find("th", string=re.compile("Total Assets"))
    ca_total_assets = ca_total_assets.find_next_sibling().text.strip() if ca_total_assets is not None else ""
    ca_data = []
    ca_dict = {
        "inventories": ca_inventory,
        "trade_and_other_receivables": ca_trade_rec,
        "cash_and_cash_eq": ca_cash_casheq,
        "others": ca_other_assets,
        "total": ca_total_ca,
        "total_assets": ca_total_assets
    }
    if ca_total_assets != "0":
        ca_data.append(ca_dict)
    else:
        ca_data = ""

    equity_share_cap = bs_table.find("th", string=re.compile("Share Capital"))
    equity_share_cap = equity_share_cap.find_next_sibling().text.strip() if equity_share_cap is not None else ""
    equity_other_res = bs_table.find("th", string=re.compile("Other reserves"))
    equity_other_res = equity_other_res.find_next_sibling().text.strip() if equity_other_res is not None else ""
    equity_retain_earning = bs_table.find("th", string=re.compile("Retained Earnings"))
    equity_retain_earning = equity_retain_earning.find_next_sibling().text.strip() if equity_retain_earning is not None else ""
    other_equity = bs_table.find_all("th", string=("Others"))[2]
    other_equity = other_equity.find_next_sibling().text.strip() if other_equity is not None else ""
    equity_total = bs_table.find_all("th", string=("Total"))[2]
    equity_total = equity_total.find_next_sibling().text.strip() if equity_total is not None else ""
    equity_data = []
    equity_dict = {
        "share_capital": equity_share_cap,
        "other_reserves": equity_other_res,
        "retained_earnings": equity_retain_earning,
        "others": other_equity,
        "total": equity_total
    }
    if equity_total != "0":
        equity_data.append(equity_dict)
    else:
        equity_data = ""

    ncl_long_term_borrowing = bs_table.find("th", string=re.compile("Long term Borrowings"))
    ncl_long_term_borrowing = ncl_long_term_borrowing.find_next_sibling().text.strip() if ncl_long_term_borrowing is not None else ""
    ncl_deffered_tax = bs_table.find("th", string=re.compile("Deferred Tax"))
    ncl_deffered_tax = ncl_deffered_tax.find_next_sibling().text.strip() if ncl_deffered_tax is not None else ""
    ncl_long_term_provisions = bs_table.find("th", string=re.compile("Long term Provisions"))
    ncl_long_term_provisions = ncl_long_term_provisions.find_next_sibling().text.strip() if ncl_long_term_provisions is not None else ""
    ncl_other = bs_table.find_all("th", string=("Others"))[3]
    ncl_other = ncl_other.find_next_sibling().text.strip() if ncl_other is not None else ""
    ncl_total = bs_table.find_all("th", string=("Total"))[3]
    ncl_total = ncl_total.find_next_sibling().text.strip() if ncl_total is not None else ""
    ncl_data = []
    ncl_dict = {
        "long_term_borrowings": ncl_long_term_borrowing,
        "deffered_tax": ncl_deffered_tax,
        "long_term_provisions": ncl_long_term_provisions,
        "others": ncl_other,
        "total": ncl_total
    }
    if ncl_total != "0":
        ncl_data.append(ncl_dict)
    else:
        ncl_data = ""

    cl_trade_pay = bs_table.find("th", string=re.compile("Trade and other Payables"))
    cl_trade_pay = cl_trade_pay.find_next_sibling().text.strip() if cl_trade_pay is not None else ""
    cl_short_term = bs_table.find("th", string=re.compile("Short Term Borrowings"))
    cl_short_term = cl_short_term.find_next_sibling().text.strip() if cl_short_term is not None else ""
    cl_current_tax_payable = bs_table.find("th", string=re.compile("Current Tax payable"))
    cl_current_tax_payable = cl_current_tax_payable.find_next_sibling().text.strip() if cl_current_tax_payable is not None else ""
    cl_short_term_prov = bs_table.find("th", string=re.compile("Short Term Provisions"))
    cl_short_term_prov = cl_short_term_prov.find_next_sibling().text.strip() if cl_short_term_prov is not None else ""
    cl_others = bs_table.find_all("th", string=("Others"))[4]
    cl_others = cl_others.find_next_sibling().text.strip() if cl_others is not None else ""
    cl_total_cl = bs_table.find("th", string=re.compile("Total Current Liabilities"))
    cl_total_cl = cl_total_cl.find_next_sibling().text.strip() if cl_total_cl is not None else ""
    cl_total_liab = bs_table.find("th", string=re.compile("Total Liabilities"))
    cl_total_liab = cl_total_liab.find_next_sibling().text.strip() if cl_total_liab is not None else ""
    cl_total_equity_liab = bs_table.find("th", string=re.compile("Total Equity & liabilities"))
    cl_total_equity_liab = cl_total_equity_liab.find_next_sibling().text.strip() if cl_total_equity_liab is not None else ""
    cl_data = []
    cl_dict = {
        "trade_and_other_payables": cl_trade_pay,
        "short_term_borrowings": cl_short_term,
        "current_tax_payable": cl_current_tax_payable,
        "short_term_provisions": cl_short_term_prov,
        "others": cl_others,
        "total_current_liabilities": cl_total_cl,
        "total_liabilities": cl_total_liab,
        "total_equity_and_liabilities": cl_total_equity_liab
    }
    if cl_total_equity_liab != "0":
        cl_data.append(cl_dict)
    else:
        cl_data = ""

    objections_table = soup.find(id="cdk-accordion-child-17")
    objections_body = objections_table.find("tbody")
    objections_rows = objections_body.find_all("tr")
    objections_check = objections_body.find("tr").find("h4").text.strip() if objections_body.find("tr").find("h4") is not None else ""
    objection_details = []
    if len(objections_rows) > 0 and "No result to display" not in objections_check:
        for objections_row in objections_rows:
            objection_date = objections_row.find("td", {"data-column":"Objection Date"}).text.strip()
            objector =  objections_row.find("td", {"data-column":"Objector"}).text.strip()
            objections_dict = {
                "date": objection_date,
                "objector": objector
            }
            objection_details.append(objections_dict)


    OBJ = {
        "registration_number": file_no,
        "name": name,
        "category": category,
        "type": type_,
        "registration_date": registration_date,
        "nature": nature,
        "sub_category": sub_category,
        "status": status,
        "inactive_date": inactive_date,
        "addresses_detail": [
            {
                "type": "office_address",
                "address": office_address
            }
        ],
        "additional_detail": [
            {
                "type": "shares_information",
                "data": all_share_data
            },
            {
                "type": "shareholder_information",
                "data": all_shareholder_data
            },
            {
                "type": "winding_up_information",
                "data": winding_up_details
            },
            {
                "type": "charges_information",
                "data": charges_details
            },
            {
                "type": "branches_and_other_offices",
                "data": all_business_data
            },
            {
                "type": "profit_and_loss_information",
                "data": total_fs_data
            },
            {
                "type": "non_current_asset_information",
                "data": nca_data
            },
            {
                "type": "current_asset_information",
                "data": ca_data
            },
            {
                "type": "equity_and_liabilities_information",
                "data": equity_data
            },
            {
                "type": "non_current_liabilities_information",
                "data": ncl_data
            },
            {
                "type": "current_liabilities_information",
                "data": cl_data
            },
            {
                "type": "objections_information",
                "data": objection_details
            }
        ],
        "people_detail": people_details,
        "fillings_detail": fillings_detail,
    }

    OBJ = mauritius_crawler.prepare_data_object(OBJ)
    ENTITY_ID = mauritius_crawler.generate_entity_id(OBJ["registration_number"], OBJ["name"])
    BIRTH_INCORPORATION_DATE = ''
    ROW = mauritius_crawler.prepare_row_for_db(ENTITY_ID, OBJ.get("name"), BIRTH_INCORPORATION_DATE, OBJ)
    mauritius_crawler.insert_record(ROW)

    time.sleep(3)
    popup_close_button = driver.find_element(By.CLASS_NAME, 'dialog-close-button')
    popup_close_button.click()
    time.sleep(3)
    driver.refresh()
    time.sleep(5)

try:
    crawl(start_number)
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    mauritius_crawler.db_log(log_data)
    mauritius_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}
    mauritius_crawler.db_log(log_data)