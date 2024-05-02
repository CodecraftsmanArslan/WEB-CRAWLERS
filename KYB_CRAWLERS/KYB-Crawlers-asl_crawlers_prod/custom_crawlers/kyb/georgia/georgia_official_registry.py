"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dateutil import parser

meta_data = {
    'SOURCE' :'Secretary of State',
    'COUNTRY' : 'Georgia (US State)',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ecorp.sos.ga.gov/BusinessSearch", 
                        "Source Description": "This is the official website of the Georgia Secretary of State's Corporations Division for users to access information on registered business entities in the state of Georgia."},
    'URL' : 'https://ecorp.sos.ga.gov/BusinessSearch',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Georgia (US State)'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

georgia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  georgia_crawler.get_selenium_helper()

def format_date(timestamp):
    date_str = ""
    try:
        # Parse the timestamp into a datetime object
        datetime_obj = parser.parse(timestamp)

        # Extract the date portion from the datetime object
        date_str = datetime_obj.strftime("%m-%d-%Y")

    except Exception as e:
        pass
    return date_str


# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 1

try:

    for i in range(start, 3924105):
        print(i)
        base_url = "https://ecorp.sos.ga.gov"
        url = f"{base_url}/BusinessSearch/BusinessInformation?businessId={i}"
        driver = selenium_helper.create_driver(headless=True)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        tables = soup.find_all('table')
        addresses_detail = []
        additional_detail = []
        people_detail = []
        fillings_detail = []
        previous_names_detail = []

        values = {}
        if len(tables) > 1:
            rows = tables[2].find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) == 4:
                    values[tds[0].text.replace(':', '')] = tds[1].text
                    values[tds[2].text.replace(':', '')] = tds[3].text
                elif len(tds) == 2:
                    values[tds[0].text.replace(':', '')] = tds[1].text

            NAME = values.get('Business Name').replace("%", "%%").replace("'", "''") if values.get('Business Name') is not None else ""
            registration_number = values.get('Control Number')
            type = values.get('Business Type').replace("'", "''").replace("%", "%%") if values.get('Business Type') is not None else ""

            if values.get('Principal Office Address') is not None and values.get('Principal Office Address') != "":
                addresses_detail.append({
                    "type": "office_address",
                    "address": values.get('Principal Office Address').replace("'", "''").replace("%", "%%") if values.get('Principal Office Address') is not None else ""
                })
            
            status = values.get('Status').replace("'", "''").replace("%", "%%") if values.get('Status') is not None else ""

            if values.get('NAICS Code') is not None and values.get('NAICS Code') != "":
                additional_detail.append({
                    "type": "naics_code",
                    "data": [{
                        "naics_code": values.get('NAICS Code').replace("'", "''").replace("%", "%%") if values.get('NAICS Code') is not None else "",
                        "naics_subcode": values.get('NAICS Sub Code').replace("'", "''").replace("%", "%%") if values.get('NAICS Sub Code') is not None else ""
                    }]
                })

            registration_date = format_date(values.get('Date of Formation / Registration Date'))
            jurisdiction = values.get('State of Formation').replace("'", "''").replace("%", "%%") if values.get('State of Formation') is not None else ""
            last_annual_registration_year = values.get('Last Annual Registration Year') if values.get('Last Annual Registration Year') is not None and values.get('Last Annual Registration Year') != 'NONE' else ""
            dissolution_date = values.get('Dissolved Date').replace("/", "-") if values.get('Dissolved Date') is not None else ""
            if values.get('Registered Agent Name') is not None and values.get('Registered Agent Name') != "" and values.get('Registered Agent Name') != "NONE":
                if values.get('County') != "" and values.get('County') is not None and values.get('County') != "NONE":
                    county = {
                        "county": values.get('County').replace("'", "''").replace("%", "%%")
                    }
                else:
                    county = {}
                people_detail.append({
                    "name": values.get('Registered Agent Name').replace("'", "''").replace("%", "%%"),
                    "address": values.get('Physical Address').replace("'", "''").replace("%", "%%").replace("", "").replace("NONE", "").replace("None", "").replace("none", "").replace("NULL", "").replace("Null", "").replace("null", "") if values.get('Physical Address') is not None else "",
                    "designation": "registered_agent",
                    "meta_detail": county
                })
            
            table = soup.find('table', attrs={'id': 'grid_principalList'})
            if table is not None:
                header_row = table.find('thead').find('tr')
                headers = [th.text.strip() for th in header_row.find_all('th')]
                data_rows = table.find('tbody').find_all('tr')
                for row in data_rows:
                    cells = [cell.text.strip() for cell in row.find_all('td')]
                    row_data = dict(zip(headers, cells))
                    people_detail.append({
                        "name": row_data.get("Name").replace("'", "''").replace("%", "%%") if row_data.get("Name") is not None else "",
                        "designation": row_data.get("Title").replace("'", "''").replace("%", "%%") if row_data.get("Title") is not None else "",
                        "address": row_data.get("Business Address").replace("'", "''").replace("%", "%%") if row_data.get("Business Address") is not None else ""
                    })

            filling_url = f"{base_url}/BusinessSearch/BusinessFilings?businessId={i}"
            driver.get(filling_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', attrs={'id': 'xhtml_grid'})
            if table is not None:
                data_rows = table.find('tbody').find_all('tr')
                for row in data_rows:
                    tds = row.find_all('td')
                    if len(tds) > 3:
                        fillings_detail.append({
                            "date": format_date(tds[1].text.strip()),
                            "title": tds[3].text.strip().replace("'", "''").replace("%", "%%") if tds[3].text is not None else "",
                            "file_url": urljoin(base_url, tds[3].find('a')['href']) if tds[3].find('a') else "",
                            "meta_detail": {
                                "filing_number": tds[0].text.strip(),
                                "effective_date": format_date(tds[2].text.strip())
                            }
                        })
            
            history_url = f"{base_url}/BusinessSearch/NameChangeHistory?businessId={i}"
            driver.get(history_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', attrs={'id': 'grid_NameChangeHistoryGrid'})
            if table is not None:
                rows = table.find('tbody').find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) > 4:
                        previous_names_detail.append({
                            "name": tds[1].text.strip().replace("'", "''").replace("%", "%%") if tds[1].text is not None else "",
                            "update_date": format_date(tds[4].text.strip()),
                            "meta_detail":{
                                "new_name": tds[2].text.strip().replace("'", "''").replace("%", "%%") if tds[2].text is not None else "",
                                "filing_date": format_date(tds[3].text.strip())
                            }
                        })

            if registration_number is None or registration_number == "" and NAME is None or NAME == "":
                continue

            DATA = {
                "name": NAME,
                "registration_number": registration_number,
                "type": type,
                "status": status,
                "registration_date": registration_date,
                "jurisdiction": jurisdiction,
                "last_annual_registration_year": last_annual_registration_year,
                "dissolution_date": dissolution_date,
                "people_detail": people_detail,
                "addresses_detail": addresses_detail,
                "additional_detail": additional_detail,
                "fillings_detail": fillings_detail,
                "previous_names_detail": previous_names_detail
            }

            ENTITY_ID = georgia_crawler.generate_entity_id(reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = georgia_crawler.prepare_data_object(DATA)
            ROW = georgia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)

            georgia_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    georgia_crawler.db_log(log_data)
    georgia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    georgia_crawler.db_log(log_data)