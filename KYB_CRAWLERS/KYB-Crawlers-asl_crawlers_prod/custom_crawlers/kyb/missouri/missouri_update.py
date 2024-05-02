"""Import required library"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE': 'Missouri Secretary of State, Business Services Division',
    'COUNTRY': 'Missouri',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0",
                      "Source Description": "The Business Services Division is committed to making it easier to do business in Missouri. The Division has four primary units. The Corporations Unit handles the creation and maintenance of all business entities doing business in Missouri. The Notaries & Commissions Unit performs an array of functions including commissioning notaries public. The UCC Unit processes personal property lien filings. The Safe at Home address confidentiality program helps protect victims of domestic violence, rape, sexual assault, human trafficking, stalking, or other crimes who fear for their safety by authorizing the use of a designated address on new public records."},
    'SOURCE_TYPE': 'HTML',
    'URL': ' https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': True,
    'CRAWLER_NAME': "Missouri Official Registry",
}

missouri_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
selenium_helper = missouri_crawler.get_selenium_helper()
options = uc.ChromeOptions()
options.add_argument('--headless=true')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(version_main=114,options=options)
action = ActionChains(driver)


cookies = {
    'loggedInLobIDCookie': '1',
    '_ga': 'GA1.4.1823635208.1695279113',
    '_gid': 'GA1.4.1130506193.1695279113',
    '_gid': 'GA1.2.1130506193.1695279113',
    'tw_co_rcOZLj': '%7B%22widget_opened%22%3Afalse%7D',
    'cf_chl_2': 'a312b690a91145a',
    'cf_clearance': '1xpmhL_eqiixa95a1ewVTCUgyxV8iTi8CpeRmlTABi8-1695290885-0-1-428a3fbe.cc48a59d.158b605e-250.0.0',
    'ASP.NET_SessionId': 'oqyib4jeybykdlfu2g03r3hr',
    '_gat': '1',
    '_gat_UA-24933549-4': '1',
    '_ga': 'GA1.1.1823635208.1695279113',
    '_ga_H6GS930H55': 'GS1.1.1695291075.4.1.1695291970.0.0.0',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 'cookie': 'loggedInLobIDCookie=1; _ga=GA1.4.1823635208.1695279113; _gid=GA1.4.1130506193.1695279113; _gid=GA1.2.1130506193.1695279113; tw_co_rcOZLj=%7B%22widget_opened%22%3Afalse%7D; cf_chl_2=a312b690a91145a; cf_clearance=1xpmhL_eqiixa95a1ewVTCUgyxV8iTi8CpeRmlTABi8-1695290885-0-1-428a3fbe.cc48a59d.158b605e-250.0.0; ASP.NET_SessionId=oqyib4jeybykdlfu2g03r3hr; _gat=1; _gat_UA-24933549-4=1; _ga=GA1.1.1823635208.1695279113; _ga_H6GS930H55=GS1.1.1695291075.4.1.1695291970.0.0.0',
    'origin': 'https://bsd.sos.mo.gov',
    'referer': 'https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

driver.get("https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0")


arguments = sys.argv

def get_data(search_key):
    page_number = 1  # Initialize the page number
    enter_key=driver.find_element(By.CSS_SELECTOR,'input[class="swRequiredTextbox form-control"]')
    enter_key.clear()
    enter_key.send_keys(search_key)
    print(f"Scraping Key {search_key}")
    button_press=driver.find_element(By.CSS_SELECTOR,'div[class="swTemplateButtonIconDivTextCenter"]')
    button_press.click()

    move_on_first_page=driver.find_element(By.CSS_SELECTOR,".rgPageFirst")
    move_on_first_page.click()

    while True:

        try:
            url_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.rgRow td:nth-child(4) a'))
            )

            # Extract URLs and create a list
            unique_url = set(link.get_attribute("href") for link in url_elements)
            time.sleep(5)
            for l in unique_url:
                url = l
                while True:
                    response=requests.post(url,headers=headers, cookies=cookies)
                    STATUS_CODE = response.status_code
                    DATA_SIZE = len(response.content)
                    CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
                    if not response:
                        print("no response")
                        continue
                    if response.status_code == 200:
                        break
                    else:
                        time.sleep(8)

                soup=BeautifulSoup(response.text,"html.parser")
                name = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lBENameValue').text
                type = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lBETypeValue').text
                domesticity = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lDomesticityValue').text
                charter_No = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lBEBINValue').text
                status = soup.select_one('#ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lStatusValue').text
                home = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lStateCountryValue')
                if home.text != "":
                    home_state=home.text
                else:
                    home_state=""

                date_formed = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lCreatedValue').text.replace("/","-")
                report_element= soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lARDueValue') 
                report = report_element.text.replace("/","-") if report_element else ""

                renewal_month_element = soup.find('span', id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lFiscalMonthValue')
                renewal_month = renewal_month_element.text if renewal_month_element else ""
                registered_agent_name = soup.select_one('span[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lRegAgentValue"] div')
                agent_name=registered_agent_name.text if registered_agent_name else ""

                registered_agent_add = soup.select_one('div[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_cellRegAgentValue"] span[class="swLabelWrap"]')
                registered_agent_address_string = ' '.join([agent.text.strip() for agent in registered_agent_add]) if registered_agent_add else ""


                base="https://bsd.sos.mo.gov/BusinessEntity/"
                registered_agent_url = soup.select_one('span[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lRegAgentValue"] a')
                agent_url = base+registered_agent_url["href"] if registered_agent_url and "href" in registered_agent_url.attrs else ""


                expire=soup.select_one('span[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lExpValue"]')
                expier_date = expire.text.replace("/","-") if expire else ""

                dur=soup.select_one('span[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_lDurationValue"]')
                duration = dur.text if dur else ""


                filling_type = soup.select('table[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_pgFilings_grdFilingHistory_ctl00"] tr td:nth-child(4)')
                fill = [ty.text for ty in filling_type] if filling_type else ""

            # Extract create values and join as a single string
                create_filling = soup.select('table[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_pgFilings_grdFilingHistory_ctl00"] tr td:nth-child(5)')
                create = [cr.text for cr in create_filling] if create_filling else ""


                date_filled = soup.select('table[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_pgFilings_grdFilingHistory_ctl00"] tr td:nth-child(6)')
                dt = [d.text.replace("/","-") for d in date_filled] if date_filled else ""

                # Extract eff values and join as a single string
                eff = soup.select('table[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_pgFilings_grdFilingHistory_ctl00"] tr td:nth-child(7)')
                ev = [uk.text.replace("/","-") for uk in eff] if eff else ""


                fillings_detail = []

                for i in range(len(fill)):
                    filing_entry = {
                        "date": dt[i] if i < len(dt) else "",
                        "title": create[i] if i < len(create) else "",
                        "filing_type": fill[i] if i < len(fill) else "",
                        "meta_detail": {
                            "effective_date": ev[i] if i < len(ev) else ""
                            }
                            }
                    fillings_detail.append(filing_entry)


                owner_name=soup.select_one('tr[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEOwnerGrid_ctl00__0"] td:nth-child(2)')
                if owner_name :
                    owner_name = owner_name.text
                else:
                    owner_name=""

                owner_type=soup.select_one('tr[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEOwnerGrid_ctl00__0"] td:nth-child(3)')
                if owner_type :
                    owner_type = owner_type.text 
                else:
                    owner_type = ""

                owner_address=soup.select('tr[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEOwnerGrid_ctl00__0"] td:nth-child(4) span')
                if owner_address :
                    owner_address= ', '.join([o.text for o in owner_address])
                
                else:
                    owner_address=""

                owner_since=soup.select_one('tr[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEOwnerGrid_ctl00__0"] td:nth-child(5)')
                if owner_since:
                    owner_since= owner_since.text 
                else:
                    owner_since=""


                owner_To=soup.select_one('tr[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEOwnerGrid_ctl00__0"] td:nth-child(6) ')
                if owner_To:
                    owner_To=owner_To.text 
                else:
                    owner_To=""
                
                row = soup.select('div[id="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_BEAddressGrid"] tbody tr td')

                # Initialize variables
                
                principal_office_address = ""
                principal_office_date = ""
                reg_office_address = ""
                reg_office_date = ""
                other_address = ""
                other_address_date = ""
                mailing_address = ""
                mailing_address_date = ""

                # Iterate through the rows and find the desired addresses and dates
                i = 0
                while i < len(row):
                    label = row[i].text.strip()
                    
                    if label in ['Principal Office', 'Reg. Office', 'Other Address', 'Mailing']:
                        current_label = label
                        address = row[i + 1].text.strip().replace(",,",",")
                        date = row[i + 2].text.strip().replace("/", "-")
                        i += 3  # Move to the next group
                        if current_label == 'Principal Office':
                            principal_office_address = address
                            principal_office_date = date
                        elif current_label == 'Reg. Office':
                            reg_office_address = address
                            reg_office_date = date
                        elif current_label == 'Other Address':
                            other_address = address
                            other_address_date = date
                        elif current_label == 'Mailing':
                            mailing_address = address
                            mailing_address_date = date
                    else:
                        # Move to the next group
                        i += 1

                # Create a list of address dictionaries
                addresses_list = []

                # Append dictionaries for each address type
                if principal_office_address:
                    addresses_list.append({
                        "type": "principal_office_address",
                        "address": principal_office_address,
                        "meta_detail": {
                            "since": principal_office_date,
                        }
                    })

                if reg_office_address:
                    addresses_list.append({
                        "type": "registered_office_address",
                        "address": reg_office_address,
                        "meta_detail": {
                            "since": reg_office_date,
                        }
                    })

                if mailing_address:
                    addresses_list.append({
                        "type": "mailing_address",
                        "address": mailing_address,
                        "meta_detail": {
                            "since": mailing_address_date,
                        }
                    })

                if other_address:
                    addresses_list.append({
                        "type": "Other_addresses_detail",
                        "address": other_address,
                        "meta_detail": {
                            "since": other_address_date,
                        }
                    })

                people_details = []
                if owner_name:
                    dict = {
                        "designation":"owner",
                        "name":owner_name,
                        "address":owner_address,
                        "meta_detail":{
                            "since":owner_since,
                            "owner_type":owner_type,
                            "till":owner_To
                        }
                    }
                    people_details.append(dict)
                

                if agent_name:
                    dict2 = {
                        "designation":"registered_agent",
                        "name":agent_name,
                        "address":registered_agent_address_string,
                        "meta_detail":{
                            "source_url":agent_url
                        }
                    
                    }
                    people_details.append(dict2)


                OBJ={
                "name":name,
                "type":type,
                "status":status,
                "inactive_date":expier_date,
                "incorporation_date":date_formed,
                "registration_number":charter_No,
                "jurisdiction_code":home_state,
                "entity_type":domesticity,
                "duration":duration,
                "renewal_month":renewal_month,
                "report_due_date":report,
                "people_detail": people_details,
                "addresses_detail":addresses_list ,
                "fillings_detail":fillings_detail
                }

                if OBJ["jurisdiction_code"] == "":
                    del OBJ["jurisdiction_code"]

                OBJ =  missouri_crawler.prepare_data_object(OBJ)
                ENTITY_ID = missouri_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
                NAME = OBJ['name'].replace('%','%%')
                BIRTH_INCORPORATION_DATE = ""
                ROW = missouri_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                missouri_crawler.insert_record(ROW)
            
        except:
            pass
        
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$ContentPlaceHolderMain$ContentPlaceHolderMainSingle$ppBESearch$bsPanel$SearchResultGrid$ctl00$ctl03$ctl01$ctl04"]'))
        )
        next_button.click()
        time.sleep(10)
        page_number += 1 
        print(f"Clicking Page {page_number}")
        first_page=driver.find_element(By.XPATH,"//div[@class='rgWrap rgInfoPart']//strong[1]").text
        last_page=driver.find_element(By.XPATH,"//div[@class='rgWrap rgInfoPart']//strong[2]").text
        if first_page==last_page:
            break
        print(f"first_page{first_page}")
        print(f"last_page{last_page}")


def process_keys_and_range(keys_to_send, starting_number, ending_number):
    try:    
        for search_query in keys_to_send:
            get_data(search_key=search_query)

    # Iterate over numeric range
        for i in range(int(starting_number), int(ending_number) + 1):
            get_data(search_key=str(i))

        missouri_crawler.end_crawler()
        log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
        missouri_crawler.db_log(log_data)

    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        log_data = {"status": "fail",
                    "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

        missouri_crawler.db_log(log_data)

def main():
    keys_to_send = ["K", "F", "E", "U", "A", "I"]
    starting_number = "00000000"
    ending_number = "00999999"

    if len(arguments) > 1:
        resume_key = arguments[1].upper()
        if resume_key in keys_to_send:
            keys_to_send = keys_to_send[keys_to_send.index(resume_key):]
    

    process_keys_and_range(keys_to_send, starting_number, ending_number)

if __name__ == "__main__":
    main()