"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import re
import os
import json
import time
import shortuuid
import requests
from helpers.crawlers_helper_func import CrawlersFunctions
from dotenv import load_dotenv
from langdetect import detect
from bs4 import BeautifulSoup
import unicodedata
import datetime
import traceback
from helpers.logger import Logger

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME = ''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'
API_KEY_TRANSLATION = os.getenv("API_KEY_TRANSLATION")

arguments = sys.argv
PAGE_NUMBER = arguments[1] if len(arguments) > 1 else 120000


def get_cookies_and_token(url):
    res = requests.get(url, timeout=200)
    data = res.cookies.get_dict()
    cookies = ''
    for k in data:
        cookies += "{}={}; ".format(k, data[k])
    return cookies


def make_request(url, headers, timeout):
    max_retries = 10
    for retry in range(max_retries):
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout, verify=False)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except:
            time.sleep(20*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')

    print(f'Failed to make request after {max_retries} retries.')
    return None


def make_post_request(url, headers, payload, timeout):
    max_retries = 10
    for retry in range(max_retries):
        try:
            response = requests.post(
                url, headers=headers, data=payload, timeout=timeout, verify=False)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except:
            time.sleep(20*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')

    print(f'Failed to make request after {max_retries} retries.')
    return None


def get_listed_object(record, aliases):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @return dict
    '''
    # create data object dictionary containing all above dictionaries

    meta_detail = dict()
    meta_detail['capital'] = record[5]
    meta_detail['last_registration_number'] = record[6]
    meta_detail['industry_type'] = record[7]
    meta_detail['business_size'] = record[8]
    meta_detail['fiscal_year'] = record[9]
    meta_detail['industry_type_registered_document'] = record[13]
    meta_detail['industry_type_financial_document'] = record[14]
    meta_detail['aliases'] = aliases

    data_obj = {
        "name": record[0].replace("'", ""),
        "registration_number": record[1],
        "registration_date": record[4],
        "status": record[3],
        "type": record[2],
        "incorporation_date": "",
        "jurisdiction": "",
        "jurisdiction_code": "",
        "industries": "",
        "tax_number": "",
        "dissolution_date": "",
        "inactive_date": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.thailand.thailand_kyb",
        "country_name": "Thailand",
        "meta_detail": meta_detail,
        "addresses_detail": record[10],
        "contacts_detail": record[11],
        "people_detail": record[12],
        "additional_detail": record[15],
        "previous_names_detail": record[16]
    }

    return data_obj


def prepare_data(record, category, country, entity_type, type_, name_, url_, description_, aliases):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(
        f'{record[1]}-{url_}-thailand_kyb'))  # entity_id
    data_for_db.append(record[0].replace("'", ""))  # name
    data_for_db.append(json.dumps([]))  # dob
    data_for_db.append(json.dumps([category.title()]))  # category
    data_for_db.append(json.dumps([country.title()]))  # country
    data_for_db.append(entity_type.title())  # entity_type
    data_for_db.append(json.dumps([]))  # img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'", "''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record, aliases)))  # data
    data_for_db.append(json.dumps(source_details))  # source_details
    data_for_db.append(name_ + "-" + type_)  # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')
    return data_for_db


def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url

        PREFIX_URL = "https://datawarehouse.dbd.go.th{}"
        BASE_URL = "https://datawarehouse.dbd.go.th/searchJuristicInfo"
        API_URL = "https://datawarehouse.dbd.go.th/searchJuristicFilter"
        PROFILE_URL = "https://datawarehouse.dbd.go.th/profile/tab1/{}"
        INFORMATION_URL = "https://datawarehouse.dbd.go.th/profile/tab3/{}"
        CHANGE_URL = "https://datawarehouse.dbd.go.th/profile/tab4/{}"
        Financial_Summary_URL = "https://datawarehouse.dbd.go.th/profile/tab21/{}"
        Submission_History_URL = "https://datawarehouse.dbd.go.th/profile/tab23/{}"
        BalanceSheet_URL = "https://datawarehouse.dbd.go.th/balancesheet/year/{}/"

        data_cookies = get_cookies_and_token(SOURCE_URL)

        base_headers = {
            'Authority': 'datawarehouse.dbd.go.th',
            'Method': 'GET',
            'Path': '/searchJuristicInfo',
            'Scheme': 'https',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cookie': '',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        headers = {
            'Authority': 'datawarehouse.dbd.go.th',
            'Method': 'POST',
            'Path': '/searchJuristicFilter',
            'Scheme': 'https',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '',
            'Origin': 'https://datawarehouse.dbd.go.th',
            'Referer': 'https://datawarehouse.dbd.go.th/searchJuristicInfo',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        base_headers["Cookie"] = data_cookies
        headers["Cookie"] = data_cookies

        payload_FI_1 = {
            'body': 'yearFilter=2565&compareType=YEAR&compareBizSize=SAME&compareBizArea=TH&compareAvgType=MEDIAN&comparePage=balancesheet&module=JURISTIC'}
        payload = {'body': '_pvCodeList=1&_statCodeList=1&_jpTypeList=1&_businessSizeList=1&capAmtMin=&capAmtMax=&totalIncomeMin=&totalIncomeMax=&netProfitMin=&netProfitMax=&totalAssetMin=&totalAssetMax=&reportType=XLS&textSearch=&fromPage=%2Fcompany%2Fprofile&businessSizeCodeS=&businessSizeCodeM=&businessSizeCodeL=&exporterFlag=&exporterRegFlag=&filterType=block&textSearchFilter=&jpTypeCode0=&jpTypeCode2=&jpTypeCode3=&jpTypeCode5=&jpTypeCode7=&jpTypeCodeA=&jpTypeCode8=&jpTypeCode9=&jpStatusCode1=&jpStatusCode2=&jpStatusCode3=&jpStatusCode5=&jpStatusCode6=&jpStatusCode8=&jpStatusCode9=&jpStatusCodeD=&currentPage={}&maxSize=10&totalPage={}&orderBy=jpName&selectedType=&fType='}

        response = make_request(BASE_URL, base_headers, 200)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        total_page_match = re.search(
            r'\("#totalPage"\)\.val\((\d+)\);', str(response.text))
        if total_page_match:
            total_pages = total_page_match.group(1)
        else:
            total_pages = 1857599

        DATA = []
        page_number = int(PAGE_NUMBER)
        CHUNK = []
        while page_number <= int(total_pages):
            print("Page Number: ", page_number)

            response = make_post_request(
                API_URL, headers, payload['body'].format(page_number, total_pages), 120)
            if not response:
                continue
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

            people_detail = []

            page_number += 1
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")[1:]

                for row in rows:
                    company_link = row.get('data-href')
                    response = make_request(
                        PREFIX_URL.format(company_link), headers, 200)

                    additional_detail = []
                    addresses_detail = []
                    contacts_detail = []

                    match = re.search(r'\\profile\\\\tab1\\\\(.*?)";',
                                  str(response.content).replace("\/", "\\"))
                    if match:
                        company_id = match.group(1)
                    else:
                        continue

                    match = re.search(r'\\fin\\\\balancesheet\\\\(.*?)";',
                                    str(response.text).replace("\/", "\\"))
                    if match:
                        balance_sheet_id = match.group(1)

                    profile_response = make_request(
                        PROFILE_URL.format(company_id), headers, 120)
                    profile = BeautifulSoup(profile_response.text, 'html.parser')

                    juristic_name = profile.find(
                        'h3').get_text() if profile.find('h3') else ""
                    if ":" in juristic_name:
                        juristic_name = juristic_name.split(
                            ':')[1].replace("  ", "")

                    aliases = juristic_name
                    reg_no = profile.find('h4').get_text() if profile.find('h4') else ""
                    if ":" in reg_no:
                        reg_no = reg_no.split(':')[1].replace("  ", "") 
                        
                    registered_type, registered_status, registered_date, capital, last_reg_no = "", "", "", "", ""
                    industry_type, business_size, fiscal_year, capital, industry_type_reg_document, industry_type_fin_document  = "", "", "", "", "", ""  
                    company_data = profile.select("div.card-body div div")
                    for each in company_data:
                        if 'ประเภทนิติบุคคล' in str(each):
                            registered_type = each.find_next().text.replace(
                                "  ", "").replace("\n", "") if each.find_next() else ""
                        if 'สถานะนิติบุคคล' in str(each):
                            registered_status = unicodedata.normalize("NFC", each.find_next(
                            ).get_text().strip().replace("\n", "")) if each.find_next() else ""
                        if 'วันที่จดทะเบียนจัดตั้ง' in str(each):
                            registered_date = each.find_next().text.replace(
                                "  ", "").replace("\n", "") if each.find_next() else ""
                        if 'ทุนจดทะเบียน' in str(each):
                            capital = each.find_next().text.replace("  ", "").replace(
                                "\n", "") if each.find_next() else ""
                        if 'เลขทะเบียนเดิม' in str(each):
                            last_reg_no = each.find_next().text.replace(
                                "  ", "").replace("\n", "") if each.find_next() else ""
                        if 'กลุ่มธุรกิจ' in str(each):
                            industry_type = each.find_next().text.replace(
                                "  ", "").replace("\n", "") if each.find_next() else ""
                        if 'ขนาดธุรกิจ' in str(each):
                            business_size = each.find_next().text.replace(
                                "  ", "").replace("\n", "") if each.find_next() else ""
                        if 'ปีที่ส่งงบการเงิน' in str(each):
                            fiscal_year = unicodedata.normalize("NFC", each.find_next(
                            ).get_text().strip().replace("\n", "")) if each.find_next() else ""
                            if "(" in fiscal_year:
                                fiscal_year = fiscal_year.split(
                                    "(")[0].replace("\r", "")
                        if 'ที่ตั้งสำนักงานแห่งใหญ่' in str(each):
                            headquartor_location = each.find_next().text.replace(
                                " ", "").replace("\n", "") if each.find_next() else ""
                            addresses_detail.append({"meta_detail": {
                            }, "description": "", "address": headquartor_location, "type": "headquartor_location"})
                        if 'Website' in str(each):
                            website = each.find_next().text.strip() if each.find_next() else ""
                            if website != "-":
                                contacts_detail.append(
                                    {"type": "website", "value": website, "meta_detail": {}})

                    directors = profile.select(
                        "div.row > div:nth-child(2) > div > div > ol > li")
                    for director in directors:
                        people_detail.append({"name": director.text.strip(), "address": "", "postal_address": "", "designation": "director",
                                            "appointment_date": "", "termination_date": "", "nationality": "", "email": "", "phone_number": "", "fax_number": "",
                                            "social_link": [], "meta_detail": {}})
                    if profile.find("h5", string="ประเภทธุรกิจตอนจดทะเบียน"):
                        industry_type_reg_document = profile.find("h5", string="ประเภทธุรกิจตอนจดทะเบียน").find_next().find('div', string='ประเภทธุรกิจ').find_next(
                        ).text if profile.find("h5", string="ประเภทธุรกิจตอนจดทะเบียน").find_next().find('div', string='ประเภทธุรกิจ') else ""
                    if profile.find("h5", string="ประเภทธุรกิจที่ส่งงบการเงินปีล่าสุด"):
                        industry_type_fin_document = profile.find("h5", string="ประเภทธุรกิจที่ส่งงบการเงินปีล่าสุด").find_next().find('div', string='ประเภทธุรกิจ').find_next(
                        ).text if profile.find("h5", string="ประเภทธุรกิจที่ส่งงบการเงินปีล่าสุด").find_next().find('div', string='ประเภทธุรกิจ') else ""

                    financial_summary_response = make_request(
                        Financial_Summary_URL.format(company_id), headers, 120)
                    financial_summary_soup = BeautifulSoup(
                        financial_summary_response.content, 'html.parser')

                    financial_summary_name = financial_summary_soup.select_one(
                        "div.financial-item.item1 > h5").text if financial_summary_soup.select_one("div.financial-item.item1 > h5") else ""
                    total_revenue = financial_summary_soup.find("span", string="รายได้รวม : บาท").find_previous_sibling(
                    ).text if financial_summary_soup.find("span", string="รายได้รวม : บาท") else ""
                    net_profit = financial_summary_soup.find("span", string="กำไรสุทธิ : บาท").find_previous_sibling(
                    ).text if financial_summary_soup.find("span", string="รายได้รวม : บาท") else ""
                    median_total_income = financial_summary_soup.find("span", string="ค่ามัธยฐานของรายได้รวม : บาท").find_previous_sibling(
                    ).text if financial_summary_soup.find("span", string="รายได้รวม : บาท") else ""
                    median_net_profit = financial_summary_soup.find("span", string="ค่ามัธยฐานของกำไรสุทธิ : บาท").find_previous_sibling(
                    ).text if financial_summary_soup.find("span", string="รายได้รวม : บาท") else ""
                    financial_summary_detail = [{'name': financial_summary_name, 'total_revenue': total_revenue, 'net_profit': net_profit,
                                                'median_total_income': median_total_income, 'median_net_profit': median_net_profit}]
                    additional_detail.append(
                        {"type": "financial_summary", "data": financial_summary_detail})

                    '''This particular was written extract Financial Information, 
                    this particular code can be used to extract table if needed in future.'''
                #   Extracting Financial Information

                    # balance_sheet_headers = copy.deepcopy(headers)
                    # balance_sheet_headers['Path'] = "/balancesheet/year/{}".format(balance_sheet_id)
                    # balance_sheet_headers['Referer'] = "https://datawarehouse.dbd.go.th/company/profile/{}".format(balance_sheet_id)
                    # balancesheet_response = requests.post(BalanceSheet_URL.format(balance_sheet_id), data=payload_FI_1['body'], headers=balance_sheet_headers, timeout=60)
                    # soup_balance_sheet = BeautifulSoup(balancesheet_response.text, 'html.parser')

                    # financial_statements_1 = soup_balance_sheet.find("h5", string="งบแสดงฐานะการเงิน ข้อมูลปีงบการเงิน 2561 - 2565").find_next().find("table").find_all("tr")
                    # financial_statement_object = {"2561":{"amount":"","%change":""}, "2562":{"amount":"","%change":""},
                    #                               "2563":{"amount":"","%change":""}, "2564":{"amount":"","%change":""},
                    #                               "2565":{"amount":"","%change":""}}
                    # financial_information = dict()
                    # statement_keys = ["ลูกหนี้การค้าสุทธิ", "สินค้าคงเหลือ", "สินทรัพย์หมุนเวียน", "ที่ดิน อาคารและอุปกรณ์", "สินทรัพย์ไม่หมุนเวียน", "สินทรัพย์รวม", "หนี้สินหมุนเวียน"
                    #                   , "หนี้สินไม่หมุนเวียน", "หนี้สินรวม", "ส่วนของผู้ถือหุ้น", "หนี้สินรวมและส่วนของผู้ถือหุ้น"]

                    # for statements_ in financial_statements_1:
                    #     if statements_.find_all("td"):
                    #         for st_key in statement_keys:
                    #             if statements_.find("th", string=st_key):
                    #                 i = 0
                    #                 keys = statements_.find("th", string=st_key).find_next_siblings("td")
                    #                 financial_information[st_key)] = financial_statement_object
                    #                 for item_ in financial_information[st_key)]:
                    #                     financial_information[st_key)][item_]["amount"] = keys[i].text.strip()
                    #                     financial_information[st_key)][item_]["%change"] = keys[i+1].text.strip()
                    #                     i+=2
                    # additional_detail.append({"type":"financial_information", "data":[financial_information]})

                #   Extracting Submission History

                    submission_history_response = make_request(
                        Submission_History_URL.format(company_id), headers, 120)
                    submission_history_soup = BeautifulSoup(
                        submission_history_response.content, 'html.parser')

                    submisson_heading = submission_history_soup.find(
                        "h5", string="ประวัติการส่งงบการเงิน (ข้อมูลปีงบการเงิน 2561 - 2565)")
                    submisson_details = []
                    if submisson_heading:
                        submisson_table = submisson_heading.find_next().find("table")
                        if submisson_table:
                            submisson_data = submisson_table.find_all("tr")
                            for row in submisson_data:
                                if row.find_all("td"):
                                    columns = row.find_all("td")
                                    submisson_details.append({"fiscal_year": columns[0].text, "accounting_period": columns[1].text,
                                                            "submitted_date": columns[2].text, "auditor": columns[3].text})

                    additional_detail.append(
                        {"type": "submisson_history", "data": submisson_details})

                #   Extracting Investment by Nationality

                    information_response = make_request(
                        INFORMATION_URL.format(company_id), headers, 120)
                    information_soup = BeautifulSoup(
                        information_response.content, "html.parser")

                    thai_nationals = []
                    all_nationals = []
                    foreigners = []
                    information_heading = information_soup.find(
                        "h5", string="มูลค่าหุ้นและสัดส่วนการลงทุนจำแนกตามสัญชาติ  (ข้อมูลปี 2562-2566)")
                    if information_heading:
                        information_tables = information_heading.find_next().find_all("table")
                        thai_nationals = []
                        all_nationals = []
                        foreigners = []
                        for information_table in information_tables:
                            if "จำนวนหุ้น (หุ้น)" in str(information_table):
                                information_data = information_table.find_all("tr")
                                for row in information_data:
                                    if row.find("td"):
                                        if "ไทย" in str(row):
                                            columns = row.find_all("td")
                                            thai_nationals.append({"Number of shares": columns[2].text,
                                                                "Investment Amount in Baht": columns[3].text, "Investment Proportion": columns[4].text})
                                        if "รวมทุกสัญชาติ" in str(row):
                                            columns = row.find_all("td")
                                            all_nationals.append({"Number of shares": columns[2].text,
                                                                "Investment Amount in Baht": columns[3].text, "Investment Proportion": columns[4].text})
                                        if "ชาวต่างชาติ" in str(row):
                                            columns = row.find_all("td")
                                            foreigners.append({"Number of shares": columns[2].text,
                                                            "Investment Amount in Baht": columns[3].text, "Investment Proportion": columns[4].text})

                        if thai_nationals:
                            additional_detail.append(
                                {"type": "investment_by_thai_nationality", "data": thai_nationals})
                        if all_nationals:
                            additional_detail.append(
                                {"type": "investment_by_all_nationality", "data": all_nationals})
                        if foreigners:
                            additional_detail.append(
                                {"type": "investment_by_foreigners", "data": foreigners})

                #   Extracting Previous Name Details

                    change_response = make_request(
                        CHANGE_URL.format(company_id), headers, 120)
                    change_soup = BeautifulSoup(
                        change_response.content, 'html.parser')

                    previous_name_heading = change_soup.find(
                        "h5", string="ประวัติการเปลี่ยนชื่อนิติบุคคล")
                    if previous_name_heading:
                        previous_name_table = previous_name_heading.find_next().find("table")
                        previous_name_details = []
                        if previous_name_table:
                            previous_name_data = previous_name_table.find_all("tr")
                            for row in previous_name_data:
                                if row.find_all("td"):
                                    columns = row.find_all("td")
                                    previous_name_details.append({"name": columns[2].text, "update_date": columns[1].text,
                                                                "meta_detail": {"status": columns[0].text}})

                #   Extacting History of Change of Registered Capital

                    history_change_heading = change_soup.find(
                        "h5", string="ประวัติการเปลี่ยนแปลงทุนจดทะเบียน")
                    if history_change_heading:
                        history_change_table = history_change_heading.find_next().find("table")
                        history_change_details = []
                        if history_change_table:
                            history_change_data = history_change_table.find_all(
                                "tr")
                            for row in history_change_data:
                                if row.find_all("td"):
                                    columns = row.find_all("td")
                                    history_change_details.append({"status": columns[0].text, "update_date": columns[1].text,
                                                                "registered_capital_(BAHT)": columns[2].text})

                            additional_detail.append(
                                {"type": "history_of_change_of_registered_capital", "data": history_change_details})

                    record = [juristic_name, reg_no, registered_type, registered_status, registered_date, capital, last_reg_no, industry_type,
                            business_size, fiscal_year, addresses_detail, contacts_detail, people_detail, industry_type_reg_document, industry_type_fin_document,
                            additional_detail, previous_name_details]

                    DATA.append(record)
                        
                    record_for_db = prepare_data(
                        record, category, country, entity_type, source_type, name, url, description, aliases)
                    query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)

                    print("Stored record.")
                    crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e, tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'", "''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Thailand
    '''
    countries = "Thailand"
    entity_type = "Company/Organization"
    category = "Official Registry"
    name = "Department of Business Development"
    description = "This is a website run by the Department of Business Development (DBD) in Thailand. It serves as a data warehouse for businesses registered with the Thai government, providing a platform for searching and accessing information about companies registered with the DBD. The website allows users to search for businesses by name, registration number, or keywords, and provides access to a variety of information about the business, including its status, registration details, address, and other related information."
    source_type = "HTML"
    url = "https://datawarehouse.dbd.go.th/index"

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                              category, url, name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
