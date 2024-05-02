import sys, os, traceback,requests,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from CustomCrawler import CustomCrawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'Government of Alberta',
    'COUNTRY' : 'Alberta',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "http://www.servicealberta.gov.ab.ca/find-if-business-is-licenced.cfm", 
                        "Source Description": "The Government of Alberta website is the official online portal and primary source for information and services from the provincial government. It provides details on government departments, programs, services, news and events in Alberta."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'http://www.servicealberta.gov.ab.ca/find-if-business-is-licenced.cfm'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Alberta Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

display = Display(visible=0,size=(800,600))
display.start()
Alberta_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = Alberta_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False, Nopecha=False, timeout=300)



driver.set_page_load_timeout(180)
driver.get("http://www.servicealberta.gov.ab.ca/find-if-business-is-licenced.cfm")

wait = WebDriverWait(driver, 120)
submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="Submit"]')))
submit_button.click()


data= BeautifulSoup(driver.page_source, "html.parser")

reg_number=""
base_url = "http://www.servicealberta.gov.ab.ca/"
for row in data.find_all('td', attrs={"colspan": "4"}):
    item = {}
    people_detail = []
    address_detail = []
    if row.find('a'):
        link = row.a["href"]
        url=f"{base_url}{link}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        def extract_table_data(table):
            table_data = {}
            for trs in table.find_all('tr'):
                tds = trs.find_all("td")
                if len(tds) == 2:
                    key = tds[0].find("b").text.strip()
                    value = tds[1].get_text(separator=" ", strip=True).replace("\xa0\r\n\t\t\t\t","")
                    table_data[key] = value
            return table_data

        link_data = {}  # Create a dictionary to store data for this link

        try:
            table1 = soup.find_all("table", class_="font")[0]
            name_element = table1.find("td", colspan="2")
            if name_element:
                name_text = name_element.find("b").text.strip()
                if name_text:
                    # Remove digits from the 'name' text
                    name = re.sub(r'\d', '', name_text)
                    link_data["Name"] = name  # Store 'name' in link_data


            reg = table1.find("td", colspan="2")
            if reg:
                reg_text = reg.find("b").text.strip()
                if reg_text:
                    # Remove digits from the 'name' text
                    reg_text = re.sub(r'[A-Za-z]', '', reg_text)
                    link_data["registration_number"] = reg_text  # Store 'name' in link_data

                    
            # Extract 'alias' from the data
            data = table1.find('td', colspan="2")
            if data is not None:
                alias = data.text.strip().split("d.b.a")[-1]
                link_data["Alias"] = alias  # Store 'alias' in link_data

            link_data['Table1']= extract_table_data(table1)


        except Exception as e:
            print(f"Error extracting Table1: {e}")

        try:
        
            table2 = soup.find_all("table", class_="font")[1]
            data_= extract_table_data(table2)
            people_detail.append({
                "name": data_.get('Inspector Name:'),
                "designation": data_.get('License Type:')
              
            })

            item["alternate_name"]=data_.get("Business Name:")
           
        except Exception as e:
            print(f"Error extracting Table2: {e}")

        try:
            table3 = soup.find_all("table", class_="font")[2]
            data_= extract_table_data(table3)
            people_detail.append({
                "name": data_.get('Inspector Name:'),
                "designation": data_.get('License Type:')
            })
        except Exception as e:
            print(f"Error extracting Table3: {e}")




        if "Table1" in link_data and "Address:" in link_data["Table1"]:
            # Replace the pattern "(.....)" in the registration number with an empty string
            reg_number = re.sub(r'\(\.\.\.\)\s+\.', '', link_data["registration_number"])
            address_detail.append({
                "type": "general_address",
                "address": link_data["Table1"]["Address:"]
            })
        
        try:
            item["name"] = link_data["Name"]
        except:
            pass
        item["source_url"] = url[1:-1] if url.startswith("(") and url.endswith(")") else url
        item["registration_number"] = reg_number if reg_number is not None else ""
        item["d.b.a"]=link_data["Alias"]
        item["license_type"] = link_data["Table1"]["License Type:"]
        item["license_year"] = link_data["Table1"]["License Year:"]
        item["expiry_date"] = link_data["Table1"]["Expiry Date:"]
        try:
            item["bonded"] = link_data["Table1"]["Bonded:"]
        except:
            pass
        item["people_detail"] = people_detail
        item["addresses_detail"] = address_detail
        OBJ =  Alberta_crawler.prepare_data_object(item)
        ENTITY_ID = Alberta_crawler.generate_entity_id(company_name=OBJ['name'], reg_number=OBJ['registration_number'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = Alberta_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        Alberta_crawler.insert_record(ROW)


try:
    Alberta_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Alberta_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Alberta_crawler.db_log(log_data)
display.stop()