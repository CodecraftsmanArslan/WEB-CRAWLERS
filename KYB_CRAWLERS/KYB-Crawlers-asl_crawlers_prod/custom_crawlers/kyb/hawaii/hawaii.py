"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from datetime import datetime
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Department of Commerce & Consumer Affairs',
    'COUNTRY' : 'Hawaii',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://hbe.ehawaii.gov/documents/business.html?fileNumber=101C5", 
                        "Source Description": "The Business Registration Division, part of the Department of Commerce & Consumer Affairs in Hawaii, oversees the Hawaii Business Express platform, which provides streamlined and online services for business registration and related activities. Hawaii Business Express is an integrated online system that simplifies the process of starting, maintaining, and expanding a business in Hawaii."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://hbe.ehawaii.gov/documents/business.html?fileNumber=101C5'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Hawaii Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

hawaii_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = hawaii_crawler.get_requests_helper()
try:
    def generate_numbers():
        if len(sys.argv) == 3:
            start_number = int(sys.argv[1])
            end_number = int(sys.argv[2])
        else:
            print("Usage: python3 script.py <start_number> <end_number>")
            return
        specific_alphabets = ['C7', 'ZZ', 'R5', 'R6', 'R7', 'T8', 'D1', 'F1', 'F2', 'G1']

        for alphabet in specific_alphabets:
            for number in range(start_number, end_number + 1):
                yield f"{number}{alphabet}"

    # Example usage
    for number in generate_numbers():
        print("\nFile Numbers=",number)
        URL = f'https://hbe.ehawaii.gov/documents/business.html?fileNumber={number}'
        response = request_helper.make_request(URL)

        if "PAGE NOT FOUND" in response.content.decode('utf-8') or "Page not found" in response.content.decode('utf-8'):
            print("Page not found")
            continue

        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.content, 'html.parser')

        data = {}
        dt_elements = soup.find_all("dt")
        dd_elements = soup.find_all("dd")

        for dt, dd in zip(dt_elements, dd_elements):
            key = dt.text.strip()
            value = dd.get_text(separator = " ", strip = True)
            data[key] = value
        
        # Get all people_detail
        def map_keys(key):
            return data.get(key, key) 
    
        people_detail = []
        if data.get("AGENT NAME","") !="":
            people_detail1 = {
                "name":data.get("AGENT NAME",""),
                "designation":"registered_agent",
                "address":data.get("AGENT ADDRESS","").replace("\n\t",""),
            }
            people_detail.append(people_detail1)
    
        try:
            for m in range(1,5):
                section3 =  soup.find_all('section')[m].find('h2')
                if section3.text.strip() == 'Member/MGR' or section3.text.strip() == 'Officers':
                    people_detail_table = section3.find_next('table', {"id":"officersTable"})
                    people_detail_rows = people_detail_table.find_all('tr')
                    for people_detail_row in people_detail_rows[1:]:
                        people_cells = people_detail_row.find_all('td')
                        Name = people_cells[0].get_text(separator = " ", strip = True)
                        office_keys = people_cells[1].get_text(separator=" ", strip=True).split()
                        offices = [map_keys(key) for key in office_keys] 
                        Date_ = people_cells[2].get_text(separator = " ", strip = True)
                        people_detail2 = {
                            "name":Name,
                            "designation":" ".join(offices),
                            "meta_detail":{
                                "date":Date_
                                }
                        }
                        people_detail.append(people_detail2)
                    break

        except:
            people_detail2  = {}
            people_detail.append(people_detail2)

        #get previous_names_detail
        previous_names_detail = []
        try:
            for t in range(1,6):
                section5 =  soup.find_all('section')[t].find('h2')
                if section5.text.strip() == 'Trade Names':
                    base_url = "https://hbe.ehawaii.gov/documents"
                    Trade_table = section5.find_next('table')
                    Trade_rows = Trade_table.find_all('tr')
                    for Trade_row in Trade_rows[1:]:
                        Trade_cells = Trade_row.find_all('td')
                        Trade_Name = Trade_cells[0].get_text(separator = " ", strip = True)
                        record_url = Trade_cells[0].find('a')['href']
                        Trade_type = Trade_cells[1].get_text(separator=" ", strip=True)
                        Trade_category = Trade_cells[2].get_text(separator=" ", strip=True)
                        Registration_Date_ = Trade_cells[3].get_text(separator = " ", strip = True)
                        Expiration_Date_ = Trade_cells[4].get_text(separator = " ", strip = True)
                        Trade_status = Trade_cells[5].get_text(separator = " ", strip = True)
                        Trade2 = {
                            "name":Trade_Name,
                            "meta_detail":{
                                "type":Trade_type,
                                "category":Trade_category,
                                "date_registered":Registration_Date_,
                                "date_expired":Expiration_Date_,
                                "status":Trade_status,
                                "record_url":base_url+record_url
                                } 
                        }
                        previous_names_detail.append(Trade2)
                    break
        except:
            previous_names_detail = []
            
            
        
        # get additional_detail
        additional_detail = []
        try:
            for s in range(1,6):
                Stocks =  soup.find_all('section')[s].find('h2')
                stocks_data = []
                if Stocks.text.strip() == 'Stocks':
                    Stocks_table = Stocks.find_next('table')
                    Stocks_rows = Stocks_table.find_all('tr')
                    for Stocks_row in Stocks_rows[1:]:
                        Stocks_cells = Stocks_row.find_all('td')
                        Stocks_Name = Stocks_cells[0].get_text(separator = " ", strip = True)
                        class_ = Stocks_cells[1].get_text(separator=" ", strip=True)
                        shares = Stocks_cells[2].get_text(separator=" ", strip=True)
                        paid_shares = Stocks_cells[3].get_text(separator = " ", strip = True)
                        par_value = Stocks_cells[4].get_text(separator = " ", strip = True)
                        Stocks_status = Stocks_cells[5].get_text(separator = " ", strip = True)
                        Stocks2 = {
                            "date":Stocks_Name,
                            "class":class_,
                            "shares":shares,
                            "paid_shares":paid_shares,
                            "par_value":par_value,
                            "stock_amount":Stocks_status
                            
                        }
                        stocks_data.append(Stocks2) 

                    additional_detail.append({
                        "type":"stocks_information",
                        "data":stocks_data
                    })
                    break
        except:
            additional_detail = []
        
        
        #Get all Fillings_detail
        Fillings_detail = []
        try:
            for j in range(1,8):
                annual_filings_section = soup.find_all('section')[j].find('h2')
                if annual_filings_section.text.strip() == 'Annual Filings':
                    filling_table = annual_filings_section.find_next('table')
                    rows = filling_table.find_all('tr')
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        filing_year = cells[0].get_text(separator = " ", strip = True)
                        date = cells[1].get_text(separator = " ", strip = True)
                        Status = cells[2].get_text(separator = " ", strip = True)
                        filling_dict = {
                            "title":"annual_filing",
                            "date":date,
                            "meta_detail":{
                                "filing_year":filing_year,
                                "status":Status,
                            }
                        }
                        Fillings_detail.append(filling_dict)
                    break
        except:
            Fillings_detail = []
        
        try:
            for i in range(1,8):
                section4 =  soup.find_all('section')[i].find('h2')
                if section4.text.strip() == 'Other Filings':
                    filling_table1 = section4.find_next('table', {"id":"otherFilingsTable"})
                    rows1 = filling_table1.find_all('tr')
                    for row1 in rows1[1:]:
                        cells1 = row1.find_all('td')
                        Date = cells1[0].get_text(separator = " ", strip = True)
                        Description = cells1[1].get_text(separator = " ", strip = True)
                        Remarks = cells1[2].get_text(separator = " ", strip = True)
                        filling_dict = {
                            "title":Description,
                            "date":Date,
                            "description":Remarks,
                        }
                        Fillings_detail.append(filling_dict)
                    break
        except:
            Fillings_detail = []
            
        
        OBJ = {
            "name":data.get("MASTER NAME") if "MASTER NAME" in data else data.get("Service Mark",""),
            "type":data.get("BUSINESS TYPE",""),
            "registration_number":data.get("FILE NUMBER") if "FILE NUMBER" in data else data.get("File Number",""),
            "purpose":data.get("PURPOSE") if "PURPOSE" in data else data.get("Purpose",""),
            "status":data.get("STATUS") if "STATUS" in data else data.get("Status","Status"),
            "jurisdiction":data.get("ORGANIZED IN",""),
            "certificate_id":data.get("Certificate Number",""),
            "industries":data.get('CATEGORY') if "CATEGORY" in data else data.get("Category",""),
            "work_id":data.get("Work Item Number",""),
            "other_name":data.get("CROSS REFERENCE NAME",""),
            "description":data.get("Description",""),
            "addresses_detail":[
                {
                    "type":"postal_address",
                    "address":data.get("MAILING ADDRESS").replace("\n\t","") if "MAILING ADDRESS" in data else data.get("Mailing Address","")
                }
            ],
            "registration_date":data.get("REGISTRATION DATE") if "REGISTRATION DATE" in data else data.get("Registration Date",""),
            "term":data.get("TERM",""),
            "managed_by":data.get("MANAGED BY",""),
            "people_detail":people_detail,
            "fillings_detail":Fillings_detail,
            "additional_detail":additional_detail,
            "previous_names_detail":previous_names_detail
        }
        
        OBJ =  hawaii_crawler.prepare_data_object(OBJ)
        ENTITY_ID = hawaii_crawler.generate_entity_id(OBJ['registration_number'], OBJ["name"])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date","")
        ROW = hawaii_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        hawaii_crawler.insert_record(ROW)

    hawaii_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    hawaii_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    hawaii_crawler.db_log(log_data)