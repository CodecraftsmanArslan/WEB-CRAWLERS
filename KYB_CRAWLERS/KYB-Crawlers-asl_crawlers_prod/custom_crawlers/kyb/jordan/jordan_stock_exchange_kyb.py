"""Set System Path"""
from cgitb import text
from pydoc import stripid
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @return dict
    '''
    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['stock_symbol'] = record[2].replace("'","''")
    meta_detail['address'] = record[3].replace("'","''")
    meta_detail['phone_number'] = record[4].replace("'","''")
    meta_detail['P.O.Box Number'] = record[5].replace("'","''")
    meta_detail['Email Address'] = record[6].replace("'","''")
    meta_detail['Fax Number'] = record[7].replace("'","''")
    meta_detail['Date of Registration'] = record[8].replace("'","''")
    meta_detail['Listing Date'] = record[9].replace("'","''")
    meta_detail['Main Objectives'] = record[10].replace("'","''")
    meta_detail['Number of Branches'] = record[11].replace("'","''")
    meta_detail['Market Capitalization (JD)'] = record[-4].replace("'","''")
    meta_detail['Assets'] = record[-5].replace("'","''")
    meta_detail['Liabilities'] = record[-6].replace("'","''")
    num_of_emp = dict()
    num_of_emp['type'] = "number_of_empolyee"
    num_of_emp['description'] = ""
    num_of_emp['meta_details'] = {"Jordanian":record[-3],"Non Jordanian":record[-2],"Total":record[-1]}

    people_detail = dict()
    people_detail['type'] = "peoples_detail"
    people_detail['description'] = ""
    people_detail['meta_details'] = {
    "genral_manager": str(record[-7]).replace("'", "''"),
    "name_": str(record[-9]).replace("'", "''"),
    "nationality": str(record[-8]).replace("'", "''"),
    "nationality_": str(record[-10]).replace("'", "''"),
    "total": str(record[-11]).replace("'", "''")
}

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": record[1],
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.Jordan.Jordan_financial_services_kyb",
        "country_name": "Jordan",
        "company_fetched_data_status": "",
        'number_of_empolyee':[num_of_emp],
        'peoples_detail':[people_detail],
        "meta_detail": meta_detail
    }

    
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{str(record[1])}-{str(url)}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
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
        headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(SOURCE_URL, headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Use pandas to read the HTML table from the webpage
        soup_ = BeautifulSoup(response.content, 'html.parser')
        tables = soup_.find_all('table', class_='table')
        trs  = soup_.find_all('tr')
        base_url = 'https://www.ase.com.jo'
        DATA = []  
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if not tds:  # Skip empty rows
                continue

            link = tds[0].find('a')
            if link:
                next_url = base_url + link.get('href')
                print(next_url)
            next_response = requests.get(next_url,headers= headers)
            soup = BeautifulSoup(next_response.text, 'html.parser')
            uls = soup.find_all('nav',class_ = "tabs")
            for ul in  uls:
                financial_url = base_url+ul.find_all('li')[-1].find('a').get('href')
           
                fin_info_response = requests.get(financial_url,headers= headers)
                fin_info_soup = BeautifulSoup(fin_info_response.text, 'html.parser')

                # Find the table rows for Market Capitalization, Total Assets, and Total Liabilities
                market_cap_row = fin_info_soup.find("tr", class_="table-row-market_capital")

                total_assets_row = fin_info_soup.find("tr", class_="table-row-total_assets")
                total_liabilities_row = fin_info_soup.find("tr", class_="table-row-total_liabilities")

                # Extract the data from the table rows
                market_cap_columns = market_cap_row.find_all("td") if market_cap_row else ""

                total_assets_columns = total_assets_row.find_all("td") if total_assets_row else ""
                total_liabilities_columns = total_liabilities_row.find_all("td") if total_liabilities_row else ""

                market_cap_values = [column.get_text(strip=True) for column in market_cap_columns]
                total_assets_values = [column.get_text(strip=True) for column in total_assets_columns]
                total_liabilities_values = [column.get_text(strip=True) for column in total_liabilities_columns]

                market_capitalization = "- ".join(market_cap_values)
                total_assets = " - ".join(total_assets_values)
                total_liabilities = " -".join(total_liabilities_values)
                # print("Market Capitalization (JD):", "- ".join(market_cap_values))
                # print("Total Assets:", " - ".join(total_assets_values))
                # print("Total Liabilities:", " -".join(total_liabilities_values))
                # input()
                ######################################################################
                information_url = base_url+ul.find_all('li')[-2].find('a').get('href')
                financial_url = base_url+ul.find_all('li')[-1].find('a').get('href')
                info_response = requests.get(information_url,headers= headers)
                info_soup = BeautifulSoup(info_response.text, 'html.parser')
                comapny_name = info_soup.h1.contents[0].strip()
                # print('Comapny_name:',comapny_name)
                views_row = info_soup.find_all('div', class_ = "views-row")
                for rows in views_row:
                    keys_vals = rows.find_all('div',class_ = "views-field")
                    code = keys_vals[0].get_text(strip = True).split(":")[-1]
                    symbol = keys_vals[1].get_text(strip = True).split(":")[-1]
                    address = keys_vals[2].get_text(strip = True).split(":")[-1]
                    telephone = keys_vals[3].get_text(strip = True).split(":")[-1]
                    p_o_box = keys_vals[4].get_text(strip = True).split(":")[-1]
                    email = keys_vals[5].get_text(strip = True).split(":")[-1]
                    fax_num = keys_vals[6].get_text(strip = True).split(":")[-1]
                    date_of_registration = keys_vals[7].get_text(strip = True).split(":")[-1]
                    listing_date = keys_vals[8].get_text(strip = True).split(":")[-1]
                    main_obj= keys_vals[9].get_text(strip = True).split(":")[-1]
                    num_of_branchers = keys_vals[10].get_text(strip = True).split(":")[-1]
                    boad_of_directors = keys_vals[11].find('a').get('href')
                    shareholder = keys_vals[12].find('a').get('href')
                    genral_manager = keys_vals[13].get_text(strip = True).split(":")[-1]
                    no_of_emp=keys_vals[14].get_text(strip = True)
                    ######################################################################
                    jordanian_value = ''
                    non_jordanian_value = ''
                    total_value = ''
                    matches = re.findall(r'\d+', no_of_emp)
                    if len(matches) >= 1:
                        jordanian_value = ''.join(matches[0])
                    if len(matches) >= 2:
                        non_jordanian_value = ''.join(matches[1])
                    if len(matches) >= 3:
                        total_value = ''.join(matches[2])
                    share_nationalities=[]
                    totals=[]
                    response = requests.get(shareholder, headers=headers)
                    soup_s = BeautifulSoup(response.text, "html.parser")

# Find the table with the desired attributes
                    table = soup_s.find("table", class_="main_data_table", cellpadding="2")

                    # Find all rows in the table
                    rows = table.find_all("tr")

                    # Iterate over the rows and extract the nationality and total percentage
                    for row in rows[3:]:
                        cells = row.find_all("td")
                    
                        share_nationality = cells[0].find("strong").text.strip() if 'strong' in str(cells[0]).lower() else cells[0].text
                        total_percentage = cells[6].find('strong').text.strip() if 'strong' in str(cells[6]).lower() else cells[6].text
                        totals.append(total_percentage)
                        share_nationalities.append(share_nationality)
                        # print("Nationality:", nationality)
                        # print("Total %:", total_percentage)
                        # print("---____")
                        
                    ######################################################################
                    response = requests.get(boad_of_directors, headers=headers)
                    html_content = response.text
                    soup_b = BeautifulSoup(html_content, "html.parser")

                    table = soup_b.find("table", {"id": "pres"})

                    names = []
                    nationalities = []
                    if table:
                        # Iterate over each row in the table skipping the first two header rows
                        rows = table.find_all("tr")[2:]
                        for row in rows:
                            # Extract the name and nationality from each row
                            columns = row.find_all("td")
                            # Check if there are enough columns in the row
                            if len(columns) >= 4:
                                name = columns[2].text.strip()
                                nationality = columns[3].text.strip()
                                # Exclude rows with unwanted information
                                if name != "Name" and nationality != "Nationality" and name != "Qualifying Shares" and nationality != "Termination date":
                                    names.append(name)
                                    nationalities.append(nationality)
                        # Print the extracted names and nationalities, skipping the first two entries
                        for name, nationality in zip(names[2:], nationalities[2:]):
                            # print("Name:", name)
                            # print("Nationality:", nationality)
                            print("")
                           
                    else:
                        print("Table not found")
                        ######################################################################
                    DATA.append([comapny_name,code,symbol,address,telephone,p_o_box,email,fax_num,date_of_registration,listing_date,main_obj,num_of_branchers,boad_of_directors,shareholder,totals,share_nationalities,names,nationalities,genral_manager,total_liabilities,total_assets,market_capitalization,jordanian_value,non_jordanian_value,total_value])
                      
        for record in DATA:
            print(record)
            record_for_db = prepare_data(record, category,country, entity_type, source_type, name, url, description)
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("stored in database\n")
            crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Jordan
    '''
    name = 'Amman Stock Exchange (ASE)'
    description = "The Amman Stock Exchange (ASE) was established in March 1999 as a non-profit independent institution; authorized to function as a regulated market for trading securities in Jordan."
    entity_type = 'Company/Organization'
    source_type = 'HTML'
    countries = 'Jordan'
    category = 'Stock Market'
    url = "https://www.ase.com.jo/en/products-services/securties-types/shares"
    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
