"""Set System Path"""
# Import necessary modules
import sys, traceback, math, os
from pathlib import Path
# Append parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
# Import required modules and functions
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from load_env.load_env import ENV
from urllib.parse import urljoin
from helper.helper import timestamp_to_str
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from multiprocessing import Process, freeze_support, Pool
from datetime import datetime

# Metadata regarding the data source
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

# Configuration for the crawler
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Georgia (US State)'
}

# Define constants
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = "https://ecorp.sos.ga.gov"
FILE_PATH = os.path.dirname(os.getcwd()) + "/georgia_state"

start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end_number = int(sys.argv[2]) if len(sys.argv) > 2 else 3924105

# Initialize the CustomCrawler instance and get the Selenium helper
georgia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  georgia_crawler.get_selenium_helper()

# Function to retrieve HTML content using Selenium
def get_html(url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # Set a timeout value (in seconds)
            timeout = 10
            browser = selenium_helper.create_driver(headless=True)

            # Apply the timeout
            browser.set_page_load_timeout(timeout)

            browser.get(url)

            # Wait for the presence of an element to ensure the page is loaded
            WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # If the page has loaded successfully, create BeautifulSoup object
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            return soup
        except TimeoutException:
            # Handle the case when the page doesn't load within the specified time
            print(f"Page load timed out. Retrying... ({retries + 1}/{max_retries})")
            retries += 1

    print("Exceeded maximum retries. Unable to load the page.")
    return None

# Function to retrieve fillings detail
def get_fillings(filling_url):
    fillings_detail = []
    soup = get_html(filling_url)
    if soup is not None:
        table = soup.find('table', attrs={'id': 'xhtml_grid'})
        if table is not None:
            data_rows = table.find('tbody').find_all('tr')
            for row in data_rows:
                tds = row.find_all('td')
                if len(tds) > 3:
                    fillings_detail.append({
                        "date": timestamp_to_str(tds[1].text.strip()),
                        "title": tds[3].text.strip().replace("'", "''").replace("%", "%%") if tds[3].text is not None else "",
                        "file_url": urljoin(BASE_URL, tds[3].find('a')['href']) if tds[3].find('a') else "",
                        "meta_detail": {
                            "filing_number": tds[0].text.strip(),
                            "effective_date": timestamp_to_str(tds[2].text.strip())
                        }
                    })
    return fillings_detail

# Function to retrieve previous names detail
def get_previous_names_detail(history_url):
    previous_names_detail = []
    soup = get_html(history_url)
    if soup is not None:
        table = soup.find('table', attrs={'id': 'grid_NameChangeHistoryGrid'})
        if table is not None:
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) > 4:
                    previous_names_detail.append({
                        "name": tds[1].text.strip().replace("'", "''").replace("%", "%%") if tds[1].text is not None else "",
                        "update_date": timestamp_to_str(tds[4].text.strip()),
                        "meta_detail":{
                            "new_name": tds[2].text.strip().replace("'", "''").replace("%", "%%") if tds[2].text is not None else "",
                            "filing_date": timestamp_to_str(tds[3].text.strip())
                        }
                    })
    return previous_names_detail

def main_func(start_num, end_num):
    print(f"Processing range: {start_num} to {end_num}\n")
    # Loop through the range of numbers to retrieve data
    for i in range(start_num, end_num):
        reg_num = str(i).zfill(7)
        with open(f"{FILE_PATH}/crawled_record.txt", "r") as crawled_records:
            file_contents = crawled_records.read()
            if str(reg_num) in file_contents:
                continue
        print(f"Record No: {reg_num}")
        BASE_URL = "https://ecorp.sos.ga.gov"
        # Construct URL for each business ID
        url = f"{BASE_URL}/BusinessSearch/BusinessInformation?businessId={i}"
        # Get HTML content from the URL
        soup = get_html(url)
        # Process retrieved HTML content if available
        if soup is None: continue
        # Extract data from HTML tables
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

            registration_date = timestamp_to_str(values.get('Date of Formation / Registration Date'))
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

            filling_url = f"{BASE_URL}/BusinessSearch/BusinessFilings?businessId={reg_num}"
            fillings_detail.extend(get_fillings(filling_url))
            
            history_url = f"{BASE_URL}/BusinessSearch/NameChangeHistory?businessId={reg_num}"
            previous_names_detail.extend(get_previous_names_detail(history_url))

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
            # Prepare data for storage or database insertion
            ENTITY_ID = georgia_crawler.generate_entity_id(reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = georgia_crawler.prepare_data_object(DATA)
            ROW = georgia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
            # Insert processed data into the database
            georgia_crawler.insert_record(ROW)
            with open(f"{FILE_PATH}/crawled_record.txt", "a") as crawled_records:
                crawled_records.write(reg_num + "\n")

    # Logging success after processing
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    georgia_crawler.db_log(log_data)
    georgia_crawler.end_crawler()

# Main execution in a try-except block
try:
    # Main process handling using multiprocessing
    if __name__ == '__main__':
        # Ensure the freeze_support() call is used for Windows compatibility
        freeze_support()

        # Number of processes to run concurrently
        num_processes = 4
        
        # Calculate the segment size based on the number of processes
        segment_size = math.ceil((end_number - start_number) / num_processes)

        # Create a list of tuples representing the start and end points of each segment
        _segments = [(i * segment_size + start_number, (i + 1) * segment_size + start_number) for i in range(num_processes)]
        
        # Create a pool of processes
        with Pool(processes=num_processes) as pool:
            # Map the main processing function to the segments and run concurrently
            pool.starmap(main_func, _segments)

# Handling exceptions
except Exception as e:
    # Log and handle exceptions
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    georgia_crawler.db_log(log_data)