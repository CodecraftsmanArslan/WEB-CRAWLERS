import sys, traceback,time,re, requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Kansas Secretary of State, Business Services',
    'COUNTRY' : 'Kansas',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.kansas.gov/bess/flow/main;jsessionid=F955DF1CC9C70289AF6BDC9C0DB6C839.aptcs03-inst1?execution=e1s3", 
                        "Source Description": "Among the many duties of the Office of the Kansas Secretary of State is maintaining primary responsibility for administering elections, collecting certain records of Kansas businesses and publishing the official publications for the State of Kansas."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.kansas.gov/bess/flow/main;jsessionid=F955DF1CC9C70289AF6BDC9C0DB6C839.aptcs03-inst1?execution=e1s3'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Kansas"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'



Kansas_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)

selenium_helper = Kansas_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True)
request_helper =  Kansas_crawler.get_requests_helper()
s = Kansas_crawler.get_requests_session()


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0000000


driver.get("https://www.kansas.gov/bess/flow/main?execution=e1s11")

time.sleep(5)

first_button=driver.find_element(By.CSS_SELECTOR,'a[class="progressiveLink"]')
first_button.click()

time.sleep(5)
radio_button=driver.find_element(By.CSS_SELECTOR,'a[id="byEntityNumberLink"]')
radio_button.click()

time.sleep(5)

try:
    for i in range(start_num, 10000000):
        enter_value = driver.find_element(By.CSS_SELECTOR, 'input[id="searchFormForm:entityNumber"]')
        enter_value.clear()
        enter_value.send_keys(str(i).zfill(7))
        print("enter_value",i)

        search_button=driver.find_element(By.CSS_SELECTOR,'input[id="searchFormForm:j_id13"]')
        search_button.click()

        time.sleep(10)


        data_general=[]
        additional_detail=[]
        people_detail=[]
        addresses_detail=[]
        filling_detail=[]
        previous_names_detail=[]
        value_pair={}

        soup=BeautifulSoup(driver.page_source,"html.parser")
        table = soup.find('table', {'width': '90%'})
        if table:
            header_row = table.find('tr')
            keys = [re.sub(r'\s+', ' ', th.text.strip()) for th in header_row.find_all('th')]
            value_row = header_row.find_next('tr')
            values = [re.sub(r'\s+', ' ', td.text.strip()) for td in value_row.find_all('td')]

            for key, value in zip(keys, values):
                formatted_key = key
                formatted_value = value
                value_pair[formatted_key]=formatted_value 

        p_elements = soup.find_all('p')

        date_of_formation = ''
        business_type = ''
        state_of_organization = ''
        current_status = ''
        next_annual_value=''
        note_value=''
        tax=''
        annual_report=''
        text_following_forfeiture_element=''
        text_following_resident_agent=''
        text_following_resident_agent_office=''
        value=''


        for p in p_elements:
            text = p.get_text()
            if "Date of Formation in Kansas:" in text:
                date_of_formation = text.replace("Date of Formation in Kansas:", "").replace("/","-").strip()
            if "Business Entity Type:" in text:
                business_type = text.replace("Business Entity Type:", "").strip()
            if "State of Organization:" in text:
                state_of_organization = text.replace("State of Organization:", "").strip()
            if "Current Status:" in text:
                current_status = text.replace("Current Status:", "").strip()
            if "Tax Closing Month:" in text:
                tax= text.replace("Tax Closing Month:", "").strip()

            if "The Last Annual Report on File:" in text:
                annual_report= text.replace("The Last Annual Report on File:", "").replace("/","-").strip()



        forfeiture_element = soup.find('strong', string='Forfeiture Date:')
        if forfeiture_element:
            text_following_forfeiture_element = forfeiture_element.find_next_sibling(string=True).replace("/","-")


        note = soup.find('strong', string='Annual Reports')
        if note:
            note_value=note.find_next("p").text.replace("\n\t\t\t"," ").strip()


        next_annual = soup.find("input", {"value":"File Online"})
        if next_annual:
            next_annual_value=next_annual.parent.parent.find_previous_sibling().text.replace("Next", "").replace("Annual Report Due:","").replace("/","-").strip()

        additional_detail.append({
            'type':'type annual_reports_info',
            'data':[
                { 
                    'note':note_value,
                    'tax_closing_month':tax,
                    'last_annual_report_on_file':annual_report,
                    'next_annual_report_due':next_annual_value,
                    'forfeiture_date':text_following_forfeiture_element,

                }
            ]
            
        })


        previous_names_value = soup.find('strong', text='Previous Names:')
        if previous_names_value:
            previous_element = previous_names_value.find_next('br').next_sibling.strip()
            previous_names_detail.append(
                {
                    'name':previous_element
                }
            )


        div_element = soup.find('div', style='float: left; font-size: 90%;')
        if div_element:
            address_text = div_element.get_text(strip=True)
            if "Current Mailing Address" in address_text:
                address = address_text.replace("Current Mailing Address:", "").strip()
                addresses_detail.append({
                    'type': 'mailing_address',
                    'address':address
                })
            
        resident_agent_element = soup.find('strong', string='Resident Agent:')
        if resident_agent_element:
            text_following_resident_agent = resident_agent_element.find_next_sibling(string=True)


        resident_agent_office = soup.find('strong', string='Registered Office:')
        if resident_agent_office:
            text_following_resident_agent_office = resident_agent_office.find_next_sibling(string=True)

        people_detail.append({
            'designation': 'registered_agent',
            'name':text_following_resident_agent,
            'address':text_following_resident_agent_office

        })


        input_element = soup.find('input', {'name': 'id'})
        if input_element:
            value = input_element.get('value')


        url = f"https://www.kssos.org/filed_doc_viewer/view_entity.aspx?id={value}&submit=View+History+and+Documents"

        headers = {
            'authority': 'www.kssos.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.kssos.org',
            'referer': 'https://www.kssos.org/filed_doc_viewer/view_entity.aspx?id=01091995222222208&submit=View+History+and+Documents',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        def get_paras(url):
            response = request_helper.make_request(url)
            soup = BeautifulSoup(response.text, "html.parser")
            viewstate = soup.find('input',id="__VIEWSTATE")
            viewstategen = soup.find('input',id="__VIEWSTATEGENERATOR")
            event = soup.find('input',id="__EVENTVALIDATION")
            encrypt=soup.find('input',id="__VIEWSTATEENCRYPTED")
    
            res = {
                "viewstate_value": viewstate["value"] if viewstate else "",
                "viewstate_generator": viewstategen["value"] if viewstategen else "",
                "event_validation": event["value"] if event else "",
                "viewstate_encrypted":encrypt["value"] if event else ""
            }
            return res
        
        params = get_paras(url)
        payload = {
            "__VIEWSTATE": params.get('viewstate_value'),
            "__VIEWSTATEGENERATOR": params.get('viewstate_generator'),
            "__EVENTVALIDATION": params.get('event_validation'),
            "__VIEWSTATEENCRYPTED":params.get('viewstate_encrypted'),
            'chkDeclare': 'on',
            'btnLogin': 'Next',
           
        }
        response = request_helper.make_request(method="POST", url=url, headers=headers, data=payload)
        filling_detail=[]
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'id': 'gvEntityFilings'})
            if table:
                rows = table.find_all('tr')[1:]

                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 4:
                        date = columns[2].find('span').text.strip()
                        document_type = columns[3].find('span').text.strip()

                        filling_detail.append({
                            'date': date.replace("/","-"),
                            'filing_type': document_type,
                            'title': document_type
                        })


        OBJ={
            'name':value_pair.get("Current Entity Name", ''),
            'registration_number':value_pair.get("Business Entity ID Number",''),
            'addresses_detail':addresses_detail,
            'type':business_type,
            'registration_date':date_of_formation,
            'jurisdiction':state_of_organization,
            'status':current_status,
            'people_detail':people_detail,
            'additional_detail':additional_detail,
            'fillings_detail':filling_detail,
            'previous_name_detail':previous_names_detail

        }
        OBJ =  Kansas_crawler.prepare_data_object(OBJ)
        ENTITY_ID = Kansas_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'],)
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = Kansas_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        Kansas_crawler.insert_record(ROW)
        driver.back()

    log_data = {"status": "success",
            "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
            "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    Kansas_crawler.db_log(log_data)
    Kansas_crawler.end_crawler()

except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        log_data = {"status": "fail",
            "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
            "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

        Kansas_crawler.db_log(log_data)

