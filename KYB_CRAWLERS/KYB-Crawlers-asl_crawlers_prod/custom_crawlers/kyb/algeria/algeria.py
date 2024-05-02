"""Import required library"""
import sys,traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from datetime import datetime
import traceback,sys
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'El Mouchir Directory of Algerian Companies',
    'COUNTRY' : 'Algeria',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://elmouchir.caci.dz/toutesentreprises?entreprise_search=bank#titre_page", 
                        "Source Description": "The El Mouchir directory is a file of addresses of Algerian companies in the industry, commerce, and service sectors, designed by the Algerian Chamber of Commerce and Industry (CACI) and developed with the collective of Chambers of Commerce and Industry (CCI). It is spread over 700 activities in Arabic, French, and English."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://elmouchir.caci.dz/toutesentreprises?entreprise_search=bank#titre_page'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Algeria Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

algeria_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = algeria_crawler.get_requests_helper()
arguments = sys.argv
start_page = int(arguments[1]) if len(arguments)>1 else 1
end_page = 1797
try:
    for page_number in range(start_page, end_page):
        print("\nPage Number", page_number)
        URL = f'https://elmouchir.caci.dz/toutesentreprises?page={page_number}'

        response = request_helper.make_request(URL)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        soup = BeautifulSoup(response.content,'html.parser')

        card_footers = soup.find_all('div',class_ = 'card-footer')
        for footer in card_footers:
            detail_url = footer.find('a')['href']
            response2 = request_helper.make_request(detail_url)
            soup2 = BeautifulSoup(response2.content,'html.parser')
            C_NAME = soup2.find('h1').get_text(strip=True, separator=" ") if soup2.find('h1').get_text(strip=True, separator=" ") else ""
            try:
                NAME = C_NAME.split("/")[1].strip()
            except:
                NAME = C_NAME
            try:
                agency = C_NAME.split("/")[2].strip()
            except:
                agency = ""
            try:
                directorate = C_NAME.split("/")[3].strip()
            except:
                directorate = ""
            other_details = soup2.find_all('ul',class_ = 'ts-list-colored-bullets ts-text-color-light ts-column-count-3 ts-column-count-md-2')
            try:
                ownership_status = other_details[2].get_text(strip=True)
                certificates = other_details[-1].get_text(strip=True)
                type_ = other_details[1].get_text(strip=True)
                nature =  other_details[0].get_text(strip=True)
            except:
                ownership_status, certificates, type_, nature = "", "", "", ""
            about = soup2.find('section', {"id":"description"}).get_text(strip=True, separator=" ") if soup2.find('section', {"id":"description"}) else ""
            staff_count = soup2.select_one('#quick-info > div > div > div:nth-child(1) > div > figure').get_text(strip=True) if soup2.select_one('#quick-info > div > div > div:nth-child(1) > div > figure') else ""
            start_year = soup2.select_one('#quick-info > div > div > div:nth-child(2) > div > figure').get_text(strip=True) if soup2.select_one('#quick-info > div > div > div:nth-child(2) > div > figure') else ""
            capital = soup2.select_one('#quick-info > div > div > div:nth-child(3) > div > figure').get_text(strip=True) if soup2.select_one('#quick-info > div > div > div:nth-child(3) > div > figure') else ""
            ts_description = soup2.find('dl',class_ = 'ts-description-list__line') if soup2.find('dl',class_ = 'ts-description-list__line') else ""
            services = soup2.select_one('#agency-info > div > div > div > div.col-md-8 > div.py-4 > div.scrollbar2 > div > dd > b > a').get_text(strip=True) if soup2.select_one('#agency-info > div > div > div > div.col-md-8 > div.py-4 > div.scrollbar2 > div > dd > b > a') else "" 
            industries = soup2.select_one('#agency-info > div > div > div > div.col-md-8 > div.py-4 > div.scrollbar2 > div > ul > li > a').get_text(strip=True) if soup2.select_one('#agency-info > div > div > div > div.col-md-8 > div.py-4 > div.scrollbar2 > div > ul > li > a') else ''
            try:
                industries_url = soup2.select_one('#agency-info > div > div > div > div.col-md-8 > div.py-4 > div.scrollbar2 > div > ul > li > a').find('a')['href']
            except:
                industries_url = ""

            data = {}
            try:
                for dt, dd in zip(ts_description.find_all('dt'), ts_description.find_all('dd')):
                    key = dt.text.strip().replace(':', '')
                    value = dd.text.strip()
                    data[key] = value
            except:
                data = {}
            
            additional_detail = [] 
            organization = soup2.find('a',class_ = 'btn btn-light btn-xs mb-2 mb-sm-0').get_text(strip=True) if soup2.find('a',class_ = 'btn btn-light btn-xs mb-2 mb-sm-0') else ""
            organization_url = soup2.find('a',class_ = 'btn btn-light btn-xs mb-2 mb-sm-0')['href'] if soup2.find('a',class_ = 'btn btn-light btn-xs mb-2 mb-sm-0') else ''
            members = soup2.find('small',class_ = "ts-opacity__50").get_text(strip=True, separator=" ") if soup2.find('small',class_ = "ts-opacity__50") else ''
            member_since = members.split("(")[0].replace("Membre:","").strip()
            last_updated = members.split("(")[-1].replace("Dernière mise à jour:","").replace(")","").strip()
            if organization !="" or members != "":
                additional_detail.append({
                    "type":"agency_details",
                    "data":[
                        {
                            "organization":organization,
                            "url":organization_url
                        },
                        {
                            "member_since":member_since,
                            "last_updated":last_updated
                        }
                    ]
                })
        
            OBJ = {
                "name":NAME,
                "ownership_status":ownership_status,
                "certificates":certificates,
                "type":type_,
                "services":services,
                "industries":industries,
                "industries_url":industries_url,
                "nature":nature,
                "about":about,
                "staff_count":staff_count,
                "start_year":start_year.replace("/","-"),
                "capital":capital,
                "agency":agency,
                "directorate":directorate,
                "addresses_detail":[
                    {
                        "type":"general_address",
                        "address":data.get('Adresse','')
                    }
                ],
                "contacts_detail":[
                    {
                        "type":"email",
                        "value":data.get('Email','')
                    },
                    {
                        "type":"phone_number",
                        "value":data.get('Téléphone fixe','')
                    },
                    {
                        "type":"mobile_number",
                        "value":data.get('Téléphone portable','')
                    },
                    {
                        "type":"fax_number",
                        "value":data.get('Fax','')
                    },
                    {
                        "type":"social_media",
                        "value":data.get('Email','')
                    },
                    {
                        "type":"website",
                        "value":data.get('Site Web','')
                    }
                ],
                "working_hours":data.get('Horaires de travail',''),
                "brand_name":data.get('Marque',''),
                "additional_detail":additional_detail,
            }

            OBJ =  algeria_crawler.prepare_data_object(OBJ)
            ENTITY_ID = algeria_crawler.generate_entity_id(OBJ.get('registration_number',''), OBJ["name"])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date","")
            ROW = algeria_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            algeria_crawler.insert_record(ROW)

    algeria_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    algeria_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    algeria_crawler.db_log(log_data)
  
