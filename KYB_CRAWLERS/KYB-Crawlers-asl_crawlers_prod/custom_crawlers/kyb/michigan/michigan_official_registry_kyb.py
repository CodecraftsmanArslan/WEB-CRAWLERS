import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import random
import os
import json
import shortuuid
from urllib.parse import urlparse, parse_qs
import requests
import time
from helpers.crawlers_helper_func import CrawlersFunctions
from requests.exceptions import RequestException
from helpers.logger import Logger
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langdetect import detect
import datetime
import traceback
"""Import required libraries"""

from proxies_list import PROXIES

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

arguments = sys.argv
REG_NUMBER = int(arguments[1]) if len(arguments) > 1 else 800000001

max_retries = 3
def make_request(url, headers, timeout):
    for retry in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=600)
            response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
            return response
        except RequestException as e:
            time.sleep(10*60)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')
            print(f'Error: {e}')
    
    print(f'Failed to make request after {max_retries} retries.')
    return None

def get_listed_object(record, entity_type, category_, countries):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @param countries
    @param category_
    @param entity_type
    @return dict
    '''

    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['previous_registration_number'] = str(record[3])
    meta_detail['term'] = str(record[7].replace("'", "''"))
    filling_detail = None
    if record[-2]:
        filling_detail = record[-2]

    people_detail = {
        "name": str(record[8].replace("'", "''")),
        "address": str(record[9]).replace("'", "''") + ' ' + str(record[10]).replace("'", "''") + ' ' + str(
            record[11]).replace("'", "''") + ' ' + str(record[12]).replace("'", "''") + ' ' + str(record[13]).replace("'",
                                                                                                                      "''"),
        "postal_address": ' '.join([
            str(record[14]).replace("'", "''"),
            str(record[15]).replace("'", "''"),
            str(record[16]).replace("'", "''"),
            str(record[17]).replace("'", "''"),
            str(record[18]).replace("'", "''")
        ]).strip(),
        "designation": "registered agent",
        

    }

    if record[-1]:
        people_detail2 = record[-1]

    if record[21] and record[22]:
        previous_names_detail = {
            "name": str(record[21].replace("'", "''")),
            "update_date": str(record[22]),
            
        }

    additional_detail = [
        {
            "type": "act_information",
            "data":
                [
                    {
                        "act_formed_under": str(record[19].replace("'", "''")),
                        "acts_subject_to": str(record[20].replace("'", "''")),
                    }
                ]
        },
        {
            "type": "share_information",
            "data":
                [
                    {
                        "authorized_shares": str(record[23]),
                        "shares_attributable_to_michigan": str(record[24].replace("'", "''")),
                    }
                ]
        }
    ]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": str(record[1]).replace("'", ""),
        "status": "",
        "incorporation_date": str(record[4].replace("/", "-")),
        "industries": str(record[5].replace("'", "''")),
        "registration_number": str(record[0]),
        "registration_date": "",
        "dissolution_date": str(record[6].replace("/", "-")),
        "type": record[2].replace("'", "''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.michigan.michigan_official_registry_kyb",
        "country_name": "Michigan",
        "company_fetched_data_status": "",
        "additional_detail": additional_detail,
        "meta_detail": meta_detail
    }
    # Add non-empty dictionaries to the data_obj
    if filling_detail:
        data_obj["fillings_detail"] = filling_detail

    if people_detail:
        data_obj["people_detail"] = [people_detail]

    people_detail2 = None
    if people_detail2:
        data_obj["people_detail"].extend(people_detail2)

    previous_names_detail = None
    if previous_names_detail:
        data_obj["previous_names_detail"] = [previous_names_detail]
    return data_obj


def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
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
    data_for_db.append(shortuuid.uuid(shortuuid.uuid(
        f'{record[0]}-{url_}-michigan_official_registry_kyb')))  # entity_id
    data_for_db.append(record[1].replace("'", "''"))  # name
    data_for_db.append(json.dumps([]))  # dob
    data_for_db.append(json.dumps([category.title()]))  # category
    data_for_db.append(json.dumps([country.title()]))  # country
    data_for_db.append(entity_type.title())  # entity_type
    data_for_db.append(json.dumps([]))  # img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'", "''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(
        record, entity_type, category, country)))  # data
    data_for_db.append(json.dumps(source_details))  # source_details
    data_for_db.append(name_ + "-" + type_)  # source
    data_for_db.append(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_for_db.append(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
        global SOURCE_URL,driver, CONTENT_TYPE, STATUS_CODE
        SOURCE_URL = url
        for proxy in PROXIES:
                host, port, username, password = proxy.split(':')
                proxies = {
                    'http': f'http://{username}:{password}@{host}:{port}',
                    'https': f'http://{username}:{password}@{host}:{port}',
                }
                try:
                    response = requests.get("https://cofs.lara.state.mi.us/SearchApi/Search/Search", stream=True, headers={
                        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=600,  verify=False, proxies=proxies)
                    if response.status_code == requests.codes.ok:
                            break
                except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}")
                        continue
                break
        STATUS_CODE = response.status_code
        print("STATUS_CODE",STATUS_CODE)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        print("CONTENT_TYPE",CONTENT_TYPE)
        BASE_URL = 'https://cofs.lara.state.mi.us/SearchApi/Search/Search'
        res = requests.get(BASE_URL, verify=False, timeout=600,proxies=proxies)
        # print(res.cookies)
        COOKIES = ''
        COOK = res.cookies.get_dict()
        for key in COOK:
            # if COOKIES.index(key)==-1:
                COOKIES += f'{key}:{COOK[key]};'
        # print(COOKIES)

        API_URL = "https://cofs.lara.state.mi.us/SearchApi/Search/Search/GetSearchResults"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '100',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Cookie': COOKIES,
            'Host': 'cofs.lara.state.mi.us',
            'Origin': 'https://cofs.lara.state.mi.us',
            'Referer': 'https://cofs.lara.state.mi.us/SearchApi/Search/Search',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

        payload = {
            'data': "SearchValue={}&SearchType=N&SearchMethod=&StartRange=1&EndRange=25&SortColumn=&SortDirection="}

        reg_number = REG_NUMBER
        max_reg_number = 803999999
        while reg_number < max_reg_number:
            DATA = []
            filling_data = []
            people_detail2 = []
            print("ID Number: ", reg_number)
            response = requests.post(API_URL, data=payload['data'].format(reg_number), headers=headers, timeout=600,  verify=False, proxies=proxies)

            
            # COOKIES = ''
            # COOK = response.cookies.get_dict()
            # for key in COOK:
            #     COOKIES += f'{key}:{COOK[key]};'
            # print(COOKIES)

            if  not "#errorSummary" in response.text:
                fetch_url = response.text.split(
                    "',")[0].split("window.open('")[1]
            else:
                reg_number += 1
                continue
                
            # print(fetch_url)
            reg_number += 1

            # get token from url
            parsed_url = urlparse(fetch_url)
            query_params = parse_qs(parsed_url.query)
            token = query_params.get("token", [None])[0]

            response = requests.get(fetch_url,  verify=False, timeout=600, proxies=proxies)
            soup = BeautifulSoup(response.content, 'html.parser')

            viewstate = soup.find(id="__VIEWSTATE")
            viewstate_value = viewstate["value"]
            

            viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
            viewstate_generator = viewstategen["value"]

            event = soup.find(id="__EVENTVALIDATION")
            event_validation = event["value"]

            option = soup.find(
                "option", selected="selected", text="ALL FILINGS")
            lst_filling = option["value"]

            input_tag = soup.find(
                "input", attrs={"name": "ctl00$MainContent$btnViewFilings"})
            view_filling = input_tag["value"]

            BODY = {
                '__EVENTTARGET': "",
                '__EVENTARGUMENT': "",
                '__VIEWSTATE': viewstate_value,
                '__VIEWSTATEGENERATOR': viewstate_generator,
                '__SCROLLPOSITIONX': "",
                ' __SCROLLPOSITIONY': "",

                '__EVENTVALIDATION': event_validation,
                'ctl00$MainContent$lstFilings': lst_filling,
                'ctl00$MainContent$btnViewFilings': view_filling,
                'ctl00$MainContent$txtComments':  ""
            }

            table_ = soup.find("table", id="MainContent_grdOfficers")
            people_designation, people_name, people_address = "", "", ""
            if table_:

                for row in table_.find_all('tr', class_='GridRow'):
                    columns = row.find_all('td')
                    people_designation = columns[0].text.strip(
                    ) if columns[0] else ""
                    people_name = columns[1].text.strip() if columns[1] else ""
                    people_address = columns[2].text.strip(
                    ) if columns[2] else ""
                    people_detail2.append({
                        'designation': people_designation,
                        'name': people_name,
                        "address": people_address,

                    })

            try:
                registration_number = soup.find(
                    "span", id="MainContent_lblIDNumberHeader").text.strip()
            except AttributeError:
                registration_number = ""

            try:
                name_ = soup.find(
                    "span", id="MainContent_lblEntityName").text.strip()
            except AttributeError:
                name_ = ""

            try:
                type = soup.find(
                    "span", id="MainContent_lblEntityType").text.strip()
            except AttributeError:
                type = ""

            try:
                previous_registration_number = soup.find(
                    "span", id="MainContent_lblOldIDNumber").text.strip()
            except AttributeError:
                previous_registration_number = ""

            try:
                incorporation_date = soup.find(
                    "span", id="MainContent_lblOrganisationDate").text.strip()
            except AttributeError:
                incorporation_date = ""

            try:
                industries = soup.find(
                    "span", id="MainContent_lblPurpose").text.strip()
            except AttributeError:
                industries = ""

            try:
                dissolution = soup.find(
                    "span", id="MainContent_lblInactiveDate")
                dissolution_date = dissolution.find("b").text.strip()
            except (AttributeError, TypeError):
                dissolution_date = ""

            try:
                term = soup.find("span", id="MainContent_lblTerm").text.strip()
            except AttributeError:
                term = ""

            try:
                resident_agent_name = soup.find(
                    "span", id="MainContent_lblResidentAgentName").text.strip()
            except AttributeError:
                resident_agent_name = ""

            try:
                street_address = soup.find(
                    "span", id="MainContent_lblResidentStreet").text.strip()
            except AttributeError:
                street_address = ""

            try:
                apt_suit_other = soup.find(
                    "span", id="MainContent_lblaptsuiteother").text.strip()
            except AttributeError:
                apt_suit_other = ""

            try:
                city = soup.find(
                    "span", id="MainContent_lblResidentCity").text.strip()
            except AttributeError:
                city = ""

            try:
                state = soup.find(
                    "span", id="MainContent_lblResidentState").text.strip()
            except AttributeError:
                state = ""

            try:
                zip_code = soup.find(
                    "span", id="MainContent_lblResidentZip").text.strip()
            except AttributeError:
                zip_code = ""

            try:
                office_mailing_address = soup.find(
                    "span", id="MainContent_lblPrincipleStreet").text.strip()
            except AttributeError:
                office_mailing_address = ""

            try:
                mailing_apt_suit_other = soup.find(
                    "span", id="MainContent_lblaptsuiteotherlblpricipal").text.strip()
            except AttributeError:
                mailing_apt_suit_other = ""

            try:
                mailing_city = soup.find(
                    "span", id="MainContent_lblPrincipleCity").text.strip()
            except AttributeError:
                mailing_city = ""

            try:
                mailing_state = soup.find(
                    "span", id="MainContent_lblPrincipleState").text.strip()
            except AttributeError:
                mailing_state = ""

            try:
                mailing_zip_code = soup.find(
                    "span", id="MainContent_lblPrincipleZip").text.strip()
            except AttributeError:
                mailing_zip_code = ""

            try:
                act_formed_under = soup.find(
                    "span", id="MainContent_lblActsFormedUnder").text.strip()
            except AttributeError:
                act_formed_under = ""

            try:
                acts = soup.find("tr", id="MainContent_trActSubjectTo")
                acts_subject_to = acts.find("div", class_="p1").text.strip()
            except AttributeError:
                acts_subject_to = ""

            try:
                previous = soup.find(
                    "span", id="MainContent_tblEntityNameChange")
                divs = previous.find_all("div", {"class": "p1"})
                previous_name = divs[0].text.split("The name was changed from: ")[
                    1].split(" on ")[0]
            except AttributeError:
                previous_name = ""
            try:
                previous_ = soup.find(
                    "span", id="MainContent_tblEntityNameChange")
                divs_ = previous_.find_all("div", {"class": "p1"})
                change_on = divs_[0].text.split(" on ")[1]
            except AttributeError:
                change_on = ""
            try:
                previous = soup.find(
                    "span", id="MainContent_tblEntityNameChange")
                divs = previous.find_all("div", {"class": "p1"})
                previous_name = divs[0].text.split("The name was changed from: ")[
                    1].split(" on ")[0]
            except AttributeError:
                previous_name = ""

            try:
                total_authorize_share = soup.find(
                    "span", {"id": ["MainContent_lblAuthorizedShares", "MainContent_lblSum"]}).text.strip()
            except AttributeError:
                total_authorize_share = ""

            try:
                share_attribute_to_michigan = soup.find(
                    "span", id="MainContent_lblsharesattributabletomi").text.strip()
            except AttributeError:
                share_attribute_to_michigan = ""
            TABLE_API_URL = f"https://cofs.lara.state.mi.us/CorpWeb/CorpSearch/CorpSummary.aspx?token={token}"
            headers_2 = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                # 'Cookie': COOKIES,
                'Host': 'cofs.lara.state.mi.us',
                'Referer': f'https://cofs.lara.state.mi.us/CorpWeb/CorpSearch/CorpSummary.aspx?token={token}',
                'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            }

            headers_2["Referer"] = headers_2["Referer"].format(token)
           
            
            response_ = requests.post(TABLE_API_URL, data=BODY, headers=headers_2, timeout=600, verify=False, proxies=proxies)

            soup_ = BeautifulSoup(response_.content, 'html.parser')

            table_ = soup_.find("table", id="MainContent_grdSearchResults")
            # print(table)
            name_of_filing, year_filed, date_filed, filling_no, view_pdf_url = "", "", "", "", ""
            if table_:
                # Extract the table data
                rows = table_.find_all("tr")
                for row in rows[1:]:
                    cells = row.find_all("td")
                    name_of_filing = cells[1].text.strip() if cells[1] else ""
                    year_filed = cells[2].text.strip() if cells[2] else ""
                    date_filed = cells[3].text.strip() if cells[3] else ""
                    filling_no = cells[4].text.strip() if cells[4] else ""
                    view_pdf = cells[5] if cells[5] else ""
                    try:
                        view_pdf_url = view_pdf.find("a")["href"]
                    except:
                        view_pdf_url = ''
                    if year_filed:
                        meta_detail_year = {
                            'year': year_filed
                        }
                    else:
                        meta_detail_year = {}
                    filling_data.append({
                        'title': name_of_filing,
                        'meta_detail': meta_detail_year,
                        "date": date_filed,
                        "filing_code": filling_no,
                        "file_url": view_pdf_url

                    })

            record = [registration_number, name_, type, previous_registration_number, incorporation_date, industries, dissolution_date, term, resident_agent_name, street_address, apt_suit_other, city, state, zip_code, office_mailing_address,
                      mailing_apt_suit_other, mailing_city, mailing_state, mailing_zip_code, act_formed_under, acts_subject_to, previous_name, change_on, total_authorize_share, share_attribute_to_michigan, filling_data, people_detail2]
            DATA.append(record)

            record_for_db = prepare_data(
                record, category, country, entity_type, source_type, name, url, description)

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Record Inserted!")

            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e, tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'", "''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Michigan
    '''
    name = 'Licensing and Regulatory Affairs'
    description = "The Michigan Department of Licensing and Regulatory Affairs (LARA) is the state agency responsible for licensing and regulating various industries and professions in Michigan. LARA oversees occupational and professional licensing, ensuring individuals meet the necessary qualifications and maintaining disciplinary processes."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Michigan'
    category = 'Official Registry'
    url = 'https://cofs.lara.state.mi.us/SearchApi/Search/Search#'

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,category, url, name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path": file_path, "trace_back": trace_back,  "crawler": "HTML"})
    logger.log()
