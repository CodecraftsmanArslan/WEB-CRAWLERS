"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Powrbot Inc.',
    'COUNTRY' : 'Sri Lanka',
    'CATEGORY' : 'Unofficial Source',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.listcompany.org/Sri_Lanka_Country.html", 
                        "Source Description": "Powrbot Inc. is a passionate company working on problems using data analytics, automation & machine learning. Their goal is to automate the boring stuff."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.listcompany.org/Sri_Lanka_Country.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Sri Lanka Unofficial Source Two"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

srilanka_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = srilanka_crawler.get_requests_helper()
selenium_helper = srilanka_crawler.get_selenium_helper()
arguments = sys.argv
page_number = int(arguments[1]) if len(arguments)>1 else 1

try:
    for number in range(page_number,245):
        print("\npage number", number,'\n')
        URL = f'https://powrbot.com/companies/list-of-companies-in-sri-lanka/?page={number}'
        url_response = request_helper.make_request(URL)
        STATUS_CODE = url_response.status_code
        DATA_SIZE = len(url_response.content)
        CONTENT_TYPE = url_response.headers['Content-Type'] if 'Content-Type' in url_response.headers else 'N/A'
        
        soup2 = BeautifulSoup(url_response.content, 'html.parser')
        g_my = soup2.find('div','g-my-50')
        ul = g_my.find('ul')
        links = ul.find_all('a')
        base_url = 'https://powrbot.com'
        
        for link in links:
            url = base_url+link['href']
            while True:
                response = request_helper.make_request(url)
                if not response:
                    continue
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    break
                else:
                    time.sleep(8)

            rows = soup.find('tbody').find_all('tr')
            data = {}
            for row in rows:
                key = row.find('th').get_text(separator = '',strip = True)
                value = row.find('td').get_text(separator = '',strip = True)
                data[key] = value
                
            try:
                type_ = data['Type of business']
            except:
                type_ = data.get('Type','')
            try:     
                parent_organisation = data['Parent Company']
            except:
                parent_organisation = data.get('Parent','')
            #get all people_detail
            people_detail = []
            if data.get("Owner",'') !="":
                people_detail.append({
                    "name":data.get("Owner",'').split("(")[0].strip(),
                    "designation":"owner",
                    "meta_detail":{
                        "ownership_percentage":data.get("Owner",'').split("(")[-1].replace(")","").strip()
                    }
                })
            if data.get("Founder(s)","") != "":
                people_detail.append({
                    "name":data.get("Founder(s)",""),
                    "designation":"founder"
                })
            if data.get('Key people','') != '':
                people_detail.append({
                    "name":data.get('Key people','').split("(")[0].strip(),
                    "designation":data.get('Key people','').split("(")[-1].split(')')[0].strip()
                })
            if data.get("Chancellor","") != "":
                people_detail.append({
                    "name":data.get('Chancellor',''),
                    "designation":"chancellor"
                })
            if data.get('Vice Chancellor', "") != "":
                people_detail.append({
                    "name":data.get('Vice Chancellor',''),
                    "designation":"vice_chancellor"
                })
            

            #get all additional_detail
            additional_detail = []
            try:
                academic_staff_count = data['Administrative Staff']
            except:
                academic_staff_count = data.get('Academic Staff','')
            if academic_staff_count != "":
                additional_detail.append({
                    "type":"employee_body_info",
                    "data":[
                        {
                            "academic_staff_count":academic_staff_count
                        }
                    ]
                })
            try:
                student_body_size = data['Students']
            except:
                try:
                    no_of_undergraduates = data['Undergraduates']
                except:    
                    no_of_undergraduates = data.get('Postgraduates','')

            if no_of_undergraduates and student_body_size != "":
                additional_detail.append({
                    "type":'student_body_info',
                    "data":[
                        {
                            "student_body_size":student_body_size,
                            "no_of_undergraduates":no_of_undergraduates
                        }
                    ]
                })
            motto_in_english = data.get('Motto in English','')
            Motto = data.get('Motto','')
            if motto_in_english and Motto != "":
                additional_detail.append({
                    "type":"motto_info",
                    "data":[
                        {
                            "motto_in_english":motto_in_english,
                            "motto": data.get('Motto','')
                        }
                    ]
                })

            if data.get('Predecessor','') != '':
                additional_detail.append({
                    "type":"predecessor_info",
                    "data":[
                        {
                            "name":data.get('Predecessor','').split("(")[0].strip(),
                            'active_time_period':data.get('Predecessor','').split("(")[-1].replace(")","").strip()
                        }
                    ]
                })
            try:
                Employees = data['Employees']
            except:
                Employees = data.get('Number of employees','')

            if Employees != '':
                additional_detail.append({
                    "type":"employees_info",
                    "data":[
                        {
                            "employee_body_size_range":data.get('Size range',''),
                            "total_employees":Employees.split('(')[0].strip(),
                            "year_info_last_updated":Employees.split("(")[-1].split(")")[0].strip()
                        }
                    ]
                })
            
            try:
                website = data['Website']
            except:
                website = data.get('website','')
            try:
                aliases = data['Native name']
            except:
                aliases = data.get('Native Name','')
            try:
                status = data.get('Current status','')
            except: 
                status = data.get('Current Status','')
            OBJ = {
                "name":data.get('Company Name',''),
                "aliases":aliases,
                "trade_name":data.get('Trading name',''),
                "company_description":data.get('Snippet',''),
                "year_founded":data.get('Founded',''),
                "revenue":data.get('Revenue',''),
                "services":data.get('Services',''),
                "status":status,
                "subsidiaries":data.get('Subsidiaries',''),
                "headquarters":data.get('Headquarters',''),
                "registration_status":data.get('Registration',''),
                "area_served":data.get('Area served',''),
                "is_commercial":data.get('Commercial',''),
                "type_of_site":data.get('Type of site',''),
                "site_language":data.get('Available in',''),
                "alexa_rank":data.get('Alexa rank',''),
                "isin_id":data.get('ISIN',''),
                "type":type_,
                "rating":data.get('Rating',''),
                "industries":data.get('Industry',''),
                "divisions":data.get('Divisions',''),
                "traded_as":data.get('Traded as',''),
                "total_assets":data.get('Total assets',''),
                "operating_income":data.get("Operating income",''),
                "previous_names_detail":[
                    {
                        "name":data.get('Formerly','')
                    }
                ],
                "parent_organisation":parent_organisation,
                "products":data.get('Products',''),
                "locations_info":data.get('Number of locations',''),
                "capital_ratio":data.get('Capital Ratio',''),
                "successor":data.get('Successor',''),
                "fate":data.get('Fate',''),
                "defunct_since":data.get('Defunct',''),
                "production_output":data.get('Production output',''),
                "brands":data.get('Brands',''),
                "hubs":data.get('Hubs',''),
                "IATA":data.get('IATA',''),
                "profit":data.get('Profit',''),
                "alliance":data.get('Alliance',''),
                "fleet_size":data.get('Fleet size',''),
                "destinations":data.get('Destinations',''),
                "commenced_operations":data.get('Commenced operations',''),
                "frequent_flyer_program":data.get('Frequent flyer program',''),
                "commenced_operations":data.get('Commenced operations',''),
                "campus_size":data.get('Campus',''),
                "total_athletics_teams":data.get('Athletics',''),
                "endowment":data.get('Endowment',''),
                "established":data.get('Established',''),
                "affiliations":data.get('Affiliations',''),
                "contacts_detail":[
                    {
                        "type":'website',
                        "value":website
                    }
                ],
                "people_detail":people_detail,
                "additional_detail":additional_detail    
            }
            OBJ =  srilanka_crawler.prepare_data_object(OBJ)
            ENTITY_ID = srilanka_crawler.generate_entity_id(company_name=OBJ['name'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = ''
            ROW = srilanka_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            srilanka_crawler.insert_record(ROW)

    srilanka_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    srilanka_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    srilanka_crawler.db_log(log_data)
