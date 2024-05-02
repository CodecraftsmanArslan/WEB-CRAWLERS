import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Companies House',
    'COUNTRY' : 'Vietnam',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://companieshouse.vn/", 
                        "Source Description": "Companies House was born from our own need to quickly acquire information about shareholders, directors, and commissioners of companies we or our clients entered into negotiations."},
    'URL' : 'https://companieshouse.vn/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Vietnam Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments)>1 else 1

vietnam = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  vietnam.get_requests_helper()
s = vietnam.get_requests_session()


def extract_company_info(soup):
    event_list=[]    
    company_info_sections = soup.find_all('div', class_='flex justify-between items-center')
    for company_info_section in company_info_sections:
        company_name = company_info_section.find('h3', class_='text-1xl font-bold leading-6 text-gray-900').text
        data_elements = company_info_section.find_next('div', class_='mt-5 border-t border-gray-200')
        
        if company_name == "Company information":
            company_info = data_elements.find('dl', class_='sm:divide-y sm:divide-gray-200')
            for element in company_info.find_all('div', class_='py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5'):
                key = element.find('dt', class_='text-sm font-medium text-gray-500').text
                value = element.find('dd', class_='mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0').text
                data[key]=value
        elif company_name == "Company Events":
            event_info = data_elements.find('dl', class_='sm:divide-y sm:divide-gray-200')
            for event in event_info.find_all('div', class_='py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5'):
                event_date = event.find('dt', class_='text-sm font-medium text-gray-500').text
                event_name_element = event.find('h3', class_='truncate text-sm font-semibold leading-6 text-gray-900').text
                event_description = event.find('dd', class_='mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0').text.replace("\n","")
                event_list.append({'Date': event_date, 'Event': event_name_element, 'Description': event_description})
            data['Events'] = event_list
            for event in event_list:
                fillings_detail.append({
                    'date': event['Date'],
                    'title': event['Event'],
                    'description': event['Description']
                    })
        elif company_name == "Company Activities":
            activity_list = data_elements.find('ul', class_='list-disc')
            activity_links = activity_list.find_all('a')
            activities = [activity.text for activity in activity_links]
            formatted_activities = ", ".join(activities)
            data['Activities'] = formatted_activities
            additional_detail.append({
                    "type": "activities_information",
                    "data":[
                        {
                            "title":data.get('Activities')
                        }
                    ]
                })
    return data



try:
    for i in range(start_num,125810):
        url=f"https://companieshouse.vn/?term=C%C3%94&page={i}"
        print("page_number",i)
        response=request_helper.make_request(url)
        soup = BeautifulSoup(response.content ,"html.parser")
        table=soup.find_all('li',class_="p-2 border-b border-gray-200 hover:bg-gray-100")
        for links in table:
            link_url=links.find('a',class_="text-xs font-semibold text-blue-500 uppercase hover:text-blue-700")['href']
            response=request_helper.make_request(link_url)

            soup1=BeautifulSoup(response.content, "html.parser")
            addresses_detail = []
            people_detail = []
            fillings_detail = []
            additional_detail = []
            data={}
        

            extracted_data = extract_company_info(soup1)
            addresses_detail.append({
                "type": "head_office_address",
                "address":extracted_data.get("Head office address"," ").replace('\n',"")
            })

            people_detail.append({
                "designation": "authorized_representative",
                "name":extracted_data.get("Representative"," ").replace('\n',"")
            })


            OBJ={
                "name":extracted_data.get("Registered name"," ").replace('\n',""),
                "registration_date":extracted_data.get("Founding date"," ").replace('\n',""),
                "registration_number":extracted_data.get("NBRS ID"," ").replace('\n',""),
                "type":extracted_data.get("Legal type"," ").replace('\n',""),
                "status":extracted_data.get("Status"," ").replace('\n',""),
                "addresses_detail":addresses_detail,
                "people_detail":people_detail,
                "fillings_detail":fillings_detail,
                "additional_detail":additional_detail
            }
            OBJ =  vietnam.prepare_data_object(OBJ)
            ENTITY_ID = vietnam.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = ""
            ROW = vietnam.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            vietnam.insert_record(ROW)

    vietnam.end_crawler()
    log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    vietnam.db_log(log_data)


except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    vietnam.db_log(log_data)

