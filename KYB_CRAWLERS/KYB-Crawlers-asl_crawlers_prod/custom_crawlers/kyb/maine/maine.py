"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE': 'Maine Secretary of State, Bureau of Corporations',
    'COUNTRY': 'Maine',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://apps1.web.maine.gov/nei-sos-icrs/ICRS?MainPage=x",
                      "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://apps1.web.maine.gov/nei-sos-icrs/ICRS?MainPage=x'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Maine"
}

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv

search_range = "00000000 - 99999999"

maine_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = maine_crawler.get_requests_helper()

letters = ["B", "D", "I", "L", "M", "N", "F", "R", "CP", "DC", "DP", "LP", "LN", "ND", "RC", "RD", "RI", "RN", "RP", "RR", "CR", "FC", "FP", "LF", "LR", "NF", "NR", "PR"]

def crawl():

    if len(sys.argv) > 1:
        start_letter = arguments[2].upper()
    else:
        start_letter = letters[0]

    flag = True

    for letter in letters:
        if flag and start_letter != letter:
             continue
        else:
             flag = False

        start_record = int(arguments[1]) if len(arguments)>1 else 19000000

        for i in range(start_record, 99999999):

            sign = "+" if len(letter) <= 1 else ""

            info_url = f"https://apps1.web.maine.gov/nei-sos-icrs/ICRS?CorpSumm={i}{sign}{letter}"
            other_url = f"https://apps1.web.maine.gov/nei-sos-icrs/ICRS?CorpFilings={i}{sign}{letter}"
            additional_url = f"https://apps1.web.maine.gov/nei-sos-icrs/ICRS?Login=norm&Action=addl_address&corp_id={i}{sign}{letter}"

            main_info = request_helper.make_request(url=info_url)
            main_data = main_info.text
            other_info = request_helper.make_request(url=other_url)
            other_data = other_info.text
            additional_info = request_helper.make_request(url=additional_url)
            additional_data = additional_info.text

            SATAUS_CODE = main_info.status_code
            DATA_SIZE = len(main_info.content)
            CONTENT_TYPE = main_info.headers['Content-Type'] if 'Content-Type' in main_info.headers else 'N/A'

            get_data(main=main_data, other=other_data, additional=additional_data, number=i, letter=letter, sign=sign)

    return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE


def get_data(main, other, additional, number, letter, sign):
            
            print(f"Scraping data for Registration No: {number}{sign}{letter}")

            soup = BeautifulSoup(main, "html.parser")
            table = soup.find('table')
            if table:
                first_row = table.find_all("tr")[7]
                if first_row.text.strip() != "":
                    first_row_data = first_row.find_all("td")
                    name_ = first_row_data[0].text.lower().capitalize()
                    registration_number = first_row_data[1].text.lower()
                    type = first_row_data[2].text.strip().replace("  ", "").lower().capitalize()
                    status = first_row_data[3].text.lower().strip().capitalize()
                    incorporation_date = table.find_all("td")[18].text.replace("/", "-")
                    inactive_date = table.find_all("td")[19].text.replace("N/A", "").replace("/", "-")
                    jurisdiction = table.find_all("td")[20].text

                    second_row = table.find_all("tr")[10]
                    second_row_data = second_row.find_all("td")    
                    other_names = [name.text.strip() for name in second_row_data]
                    if other_names[0] != "NONE":
                        filtered_other_names = [{"name": item, "type": other_names[index+1]} for index, item in enumerate(other_names) if item not in ['A', 'F']]
                        
                        for data in filtered_other_names:
                            if data["type"] == "A":
                                data["type"] = "assumed"
                            elif data["type"] == "F":
                                data["type"] = "former"
                    else:
                        filtered_other_names = []
                            
                    third_row = table.find_all("tr")[10+len(filtered_other_names)+2]
                    third_row_data = third_row.find("td")
                    agent_name = third_row_data.get_text(separator='<br>').split('<br>')[0].strip()

                    try:
                        agent_address = third_row_data.get_text(separator='<br>').split('<br>')[1].strip() + ", " + third_row_data.get_text(separator='<br>').split('<br>')[2].strip()
                    except IndexError:
                        agent_address = ""
                    

                    soup = BeautifulSoup(other, "html.parser")
                    table_data = soup.find("table")
                    filings_data = table_data.find_all("tr")[6:-2]
                    filing_details = [{"title": details[0].text.strip(), "date": details[1].text.strip().replace("/", "-")} for data in filings_data for details in [data.find_all("td")]]

                    for data in filing_details:
                        if data["title"] == "order":
                            data["title"] = ""

                    soup = BeautifulSoup(additional, "html.parser")
                    table3 = soup.find("table")
                    addresseses = table3.find_all("tr")[9]
                    address_data = addresseses.find_all("td")
                    general_address = {}
                    general_address["type"] = "general_address"
                    general_address["address"] = address_data[0].text.strip().replace("\n", ", ")
                    mailing_address = {}
                    mailing_address["type"] = "mailing_address"
                    mailing_address["address"] = address_data[1].text.strip().replace("\n", ", ")


                    
                    OBJ = {
                        "name": name_,
                        "type": type,
                        "status": status,
                        "incorporation_date": incorporation_date,
                        "registration_number": registration_number,
                        "inactive_date": inactive_date,
                        "jurisdiction": jurisdiction,
                        "additional_detail": [
                            {
                                "type": "other_name_information",
                                "data": filtered_other_names
                            }
                        ],
                        "people_detail": [
                            {
                                "designation": "registered_agent",
                                "name": agent_name,
                                "address": agent_address
                            }
                        ],
                        "fillings_detail": filing_details,
                        "addresses_detail": [general_address, mailing_address]
                    }

                    if OBJ["people_detail"][0]['name'] == "No Clerk/Registered Agent on file -- Contact Name":
                        del OBJ["people_detail"]

                    OBJ = maine_crawler.prepare_data_object(OBJ)
                    ENTITY_ID = maine_crawler.generate_entity_id(
                        OBJ['registration_number'], OBJ['name'])
                    NAME = OBJ['name']
                    BIRTH_INCORPORATION_DATE = ''
                    ROW = maine_crawler.prepare_row_for_db(
                        ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                    maine_crawler.insert_record(ROW)
                
                else:
                    print(f"No record found for {number}{sign}{letter}")
                    pass
            
try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML"}
    maine_crawler.db_log(log_data)
    maine_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    maine_crawler.db_log(log_data)