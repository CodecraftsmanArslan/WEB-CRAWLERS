"""Set System Path"""
import sys
from pathlib import Path
import traceback
from CustomCrawler import CustomCrawler
import json
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from bs4 import BeautifulSoup
import urllib.parse

ENV =  {
           'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')                 
        }

meta_data = {
    'SOURCE' :'Ministry of Commerce, Industry and Tourism',
    'COUNTRY' : 'Cyprus',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://efiling.drcor.mcit.gov.cy/DrcorPublic/SearchResults.aspx?name=AC%%20Omonia&number=%%25&searchtype=optStartMatch&index=1&tname=%%25&sc=0", 
                        "Source Description": " Department of Companies and Intellectual Property is responsible for the regulation, administration, and oversight of companies and intellectual property matters within the jurisdiction of Cyprus. The department's primary objective is to ensure a transparent and efficient business environment while safeguarding intellectual property rights."},
    'URL' : 'https://efiling.drcor.mcit.gov.cy/DrcorPublic/SearchResults.aspx?name=AC%20Omonia&number=%25&searchtype=optStartMatch&index=1&tname=%25&sc=0',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Cyprus Official Registry"
}

ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

cyprus_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  cyprus_crawler.get_requests_helper()

# Check if a command-line argument is provided
arguments = sys.argv
REG_NUMBER = int(arguments[1]) if len(arguments) > 1 else 100
# 106500
# Define the search range

flag = True

def crawl():  
    reg_number = REG_NUMBER
    max_reg_number = 447977
    while reg_number < max_reg_number:
        # organization_details
        print("Reg Number",reg_number)
        API_URL = "https://efiling.drcor.mcit.gov.cy/DrcorPublic/SearchResults.aspx?name=%25&number={}&searchtype=optStartMatch&index=1&tname=%25&sc=".format(reg_number)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '3477',
            'Host': 'efiling.drcor.mcit.gov.cy',
            'Origin': 'https://efiling.drcor.mcit.gov.cy',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        payload = {
            'name': '%',
            'number': str(reg_number),
            'searchtype': 'optStartMatch',
            'index': '1',
            'tname': '%',
            'sc': ''
        }
        ses = request_helper.create_requests_session()
        response = ses.get(API_URL, data=payload, headers=headers, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
      
        viewstate = soup.find(id="__VIEWSTATE")
        viewstate_value = urllib.parse.quote(viewstate["value"])
  
        viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
        viewstate_generator = viewstategen["value"]
       
        event = soup.find(id="__EVENTVALIDATION")
        event_validation = urllib.parse.quote(event["value"])
    
        event1 = soup.find(id="__EVENTTARGET")
        event_target= 'ctl00%24cphMyMasterCentral%24GridView1'

        event2 = soup.find(id="__EVENTARGUMENT")
        event_argument= 'Select%240'

        view_state= soup.find(id="__VIEWSTATEENCRYPTED")
        event_state_encrypted= urllib.parse.quote(view_state["value"])
   

        previous = soup.find(id="__PREVIOUSPAGE")
        previous_page = urllib.parse.quote(previous["value"])

        input_tag = soup.find(
            "input", attrs={"name": "ctl00$cphMyMasterCentral$ucSearch$Group1"})
        serach_group1 = input_tag["value"]

        input_tag1 = soup.find(
            "input", attrs={"name": "ctl00$cphMyMasterCentral$ucSearch$txtNumber"})
        txt_number= input_tag1["value"]
        # Set the session ID in the Cookie header
      
        # BODY = f'__EVENTTARGET={event_target}&__EVENTARGUMENT={event_argument}&__VIEWSTATE={viewstate_value}&__VIEWSTATEGENERATOR={viewstate_generator}&__VIEWSTATEENCRYPTED={event_state_encrypted}&__PREVIOUSPAGE={previous_page}&__EVENTVALIDATION={event_validation}&ctl00$cphMyMasterCentral$ucSearch$Group1={serach_group1}&ctl00$cphMyMasterCentral$ucSearch$txtName=&ctl00$cphMyMasterCentral$ucSearch$txtNumber={txt_number}'
        BODY = f'__EVENTTARGET=ctl00%24cphMyMasterCentral%24GridView1&__EVENTARGUMENT=Select%240&__VIEWSTATE={viewstate_value}&__VIEWSTATEGENERATOR={viewstate_generator}&__VIEWSTATEENCRYPTED=&__PREVIOUSPAGE={previous_page}&__EVENTVALIDATION={event_validation}&ctl00%24cphMyMasterCentral%24ucSearch%24Group1=optStartMatch&ctl00%24cphMyMasterCentral%24ucSearch%24txtName=&ctl00%24cphMyMasterCentral%24ucSearch%24txtNumber={txt_number}'
        
        headers['Referer'] = API_URL
        response_ = ses.post(API_URL, data=BODY, headers=headers, timeout=600)
        if response_.status_code == 500:
            reg_number += 1  # Increment the registration number
            continue
       
        # Preview Folder Documents
        viewstate1 = soup.find(id="__VIEWSTATE")
        viewstate_value1 = urllib.parse.quote(viewstate1["value"])
        viewstategen1 = soup.find(id="__VIEWSTATEGENERATOR")
        viewstate_generator1 = viewstategen1["value"]
        event1 = soup.find(id="__EVENTVALIDATION")
        event_validation1 = urllib.parse.quote(event1["value"])
        event11 = soup.find(id="__EVENTTARGET")
        event_target1= ''
        event21 = soup.find(id="__EVENTARGUMENT")
        event_argument1= urllib.parse.quote(event21["value"])
        previous1 = soup.find(id="__PREVIOUSPAGE")
        previous_page1 = urllib.parse.quote(previous1["value"])
        # Preview Folder Documents
        response_text = response_.text
        action_soup = BeautifulSoup(response_text, 'html.parser')
        form = action_soup.find('form', {'name': 'aspnetForm'})

        if form is not None:
            action = form.get('action')
            
            action_url = "https://efiling.drcor.mcit.gov.cy/DrcorPublic/" + action
            new_url = action_url.replace("OrganizationDetails.aspx", "OrganizationFileContents.aspx")
            
            headers_1 = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '7123',
                'Host': 'efiling.drcor.mcit.gov.cy',
                'Origin': 'https://efiling.drcor.mcit.gov.cy',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            # Preview Folder Documents
            BODY1 = f'__EVENTTARGET={event_target1}&__EVENTARGUMENT={event_argument1}&__LASTFOCUS&__VIEWSTATE={viewstate_value1}&__VIEWSTATEGENERATOR={viewstate_generator1}&__PREVIOUSPAGE={previous_page1}&__EVENTVALIDATION={event_validation1}'
            headers_1['Referer'] = API_URL
            response_1 = ses.post(new_url, data=BODY1, headers=headers_1, timeout=600)   
            soup_ = BeautifulSoup(response_.content, 'html.parser', from_encoding="windows-1252")
            table = soup_.find('table', class_="tbDetSummary")  
            if table is not None:
                NAME = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblName").text
                registration_number = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblNumber").text.replace(" ", "")
                type = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblType").text
                name_status = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblNameStatus").text
                registration_date = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblRegistrationDate").text
                status = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblStatus").text
                status_date = table.find('span', id="ctl00_cphMyMasterCentral_ucOrganizationDetailsSummary_lblstatusDate").text
                # Rest of the code...
                table1 = soup_.find('table', id="ctl00_cphMyMasterCentral_OfficialsGrid")
                
                if table1 is not None:
                    rows = table1.find_all('tr', class_=["gridRow", "gridAlternateRow"])
                    people_details = []   
                    # Iterate over each row
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) == 2:
                            people_name = cells[0].text.strip()
                            people_designation = cells[1].text.strip()
                            
                            # Create a dictionary for each person's details
                            people_detail = {
                                "name": people_name,
                                "designation": people_designation,
                            }
                            # Append the dictionary to the list of people_details
                            people_details.append(people_detail)
                else:
                    people_details = [{}]
                street = soup_.find('span', id="ctl00_cphMyMasterCentral_Street").text
                building = soup_.find('span', id="ctl00_cphMyMasterCentral_Building").text
                parish = soup_.find('span', id="ctl00_cphMyMasterCentral_Parish").text
                territory = soup_.find('span', id="ctl00_cphMyMasterCentral_Teritory").text
                address = street + '' + building + '' + parish + '' + territory
                last_updated_date = soup_.find('span', id="ctl00_cphMyMasterCentral_lblFileLastUpdateVal").text
                
                # Preview Folder Documents
                soup_1 = BeautifulSoup(response_1.content, 'html.parser', from_encoding="windows-1252")
                table_1 = soup_1.find('table', id="ctl00_cphMyMasterCentral_grdFileContent")
                if table_1 is not None:
                    rows = table_1.find_all('tr') 
                    fillings_details = []   
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) == 6:
                            title = cells[0].text.strip()
                            filling_code = cells[1].text.strip()
                            description = cells[2].text.replace("'", "").strip()
                            date = cells[3].text.strip()
                            
                            fillings_detail = {
                                "title": title,
                                "filing_code": filling_code,
                                "description": description,
                                "date": date.replace("/","-")
                            }
                            
                            fillings_details.append(fillings_detail)
                    # Print the data with keys for fillings_detail
                    for detail in fillings_details:
                        pass
                else:
                    fillings_details = [{}]
                
                DATA = {
                    "name": NAME,
                    "registration_number": bytes(registration_number,'unicode_escape').decode('unicode_escape'),
                    "type": type,
                    "name_status": name_status,
                    "registration_date": registration_date.replace("/","-"),
                    "status": status,
                    "status_date": status_date.replace("/","-"),
                    "last_update_date": last_updated_date.replace("/","-"),
                    "addresses_detail": [
                        {
                            "address": address,
                            "type": "general_address"
                        }
                    ],
                    "fillings_detail": fillings_details,
                    "people_detail": people_details
                }
                ENTITY_ID = cyprus_crawler.generate_entity_id(reg_number=registration_number)
                BIRTH_INCORPORATION_DATE = ''
                DATA = cyprus_crawler.prepare_data_object(DATA)
                ROW = cyprus_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                
                cyprus_crawler.insert_record(ROW)          
            reg_number += 1 # Increment the registration number

    log_data = {
        "status": 'success',
        "error": "",
        "url": meta_data['URL'],
        "source_type": meta_data['SOURCE_TYPE'],
        "data_size": DATA_SIZE,
        "content_type": CONTENT_TYPE,
        "status_code": STATUS_CODE,
        "trace_back": "",
        "crawler": "HTML"
    }

    cyprus_crawler.db_log(log_data)
    cyprus_crawler.end_crawler()


try:
    crawl()
except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {
        "status": 'fail',
        "error": str(e),
        "url": meta_data['URL'],
        "source_type": meta_data['SOURCE_TYPE'],
        "data_size": DATA_SIZE,
        "content_type": CONTENT_TYPE,
        "status_code": STATUS_CODE,
        "trace_back": tb.replace("'", "''"),
        "crawler": "HTML"
    }
    
    cyprus_crawler.db_log(log_data)
