"""Import required library"""
import sys, traceback,time,re, io
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import traceback,sys, PyPDF2
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Skráseting Føroya',
    'COUNTRY' : 'Faroe Islands',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx", 
                        "Source Description": "The Authority is responsible for the information about companies registered with the Authority. The Authority registers new companies and changes to already registered companies."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Faroe Islands Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

faroe_islands_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = faroe_islands_crawler.get_requests_helper()


def extract_pdf_data(pdf_url):
    pdf_data = {}
    pdf_response = request_helper.make_request(pdf_url)
    pdf_content = pdf_response.content
    with io.BytesIO(pdf_content) as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages
        
        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            page_text = page.extractText()
            
            for line in page_text.split('\n \n'):
                # Split line into key and value using the first colon found
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    pdf_data[key] = value
    
    return pdf_data
arguments = sys.argv
page = int(arguments[1]) if len(arguments)>1 else 1
try:
    while True:
        print("\nPage Number", page)
        SOURCE_URL = f'https://www.skraseting.fo/en/companies/search-companies?&name=_&page={page}'
        response = request_helper.make_request(SOURCE_URL, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table',class_= 'tblResult')
        DATA = []
        trs = table.find_all('tr')
        if len(trs) == 1:
            break
        for tr in trs[1:]:
            tds = tr.find_all('td')
            Reg_no= tds[0].get_text(strip=True)
            Name = tds[1].get_text(strip=True)
            Date = tds[2].get_text(strip=True).split("S")[0]
            onclick_value = re.search(r"skrPopup\((.*?)\)", str(tds[1])).group(1).replace("'","").split(",")
            id_ = onclick_value[1]
            s = onclick_value[-1]
            pdf_url = f"https://www.skraseting.fo/api/Skraseting/FelagPdf?id={id_}&s={s}"
            try:
                onclick_value_ = re.search(r"skrPopup\((.*?)\)", str(tds[3])).group(1).replace("'","").split(",")
                ad_id = onclick_value_[1]
                ad_s = onclick_value_[-1]
                adds_url = f"https://www.skraseting.fo/api/Skraseting/LysingPdf?id={ad_id}&s={ad_s}"
            except:
                adds_url = ""
            extract_data = extract_pdf_data(pdf_url)
            
            people_details = []
            try:
                Stjóri = extract_data.get('Stjóri','')
        
                try:
                    directors_designation_ = Stjóri.split("\n")[0].split(" ")[0]
                    directors_names_  = Stjóri.split("\n")[0].split(directors_designation_)[1].strip()
                    directors_address_ = Stjóri.replace(directors_designation_, "").replace(directors_names_, "").replace("\n", " ").strip()
                except:
                    directors_names_, directors_address_, directors_designation_ = "","",""
                if directors_names_ != "":
                    people_details.append({
                        "name":directors_names_,
                        "address":directors_address_,
                        "designation":directors_designation_
                    })
            except:
                Stjóri = extract_data.get('Stjórn','')
                try:
                    directors_designation = Stjóri.split("\n")[0].split(" ")[0]
                    directors_names  = Stjóri.split("\n")[0].split(directors_designation)[1].strip()
                    directors_address = Stjóri.replace(directors_designation, "").replace(directors_names, "").replace("\n", " ").strip()
                except:
                    directors_names, directors_address, directors_designation = "","",""
                if directors_names !="":
                    people_details.append({
                        "name":directors_names,
                        "address":directors_address,
                        "designation":directors_designation
                    })
            try:
                Nevnd = extract_data.get('Nevnd','')
                list_ = Nevnd.replace("\nNev", ",,Nev").split(",,")
                for people in list_:
                    designation = people.split("\n")[0].split(" ")[0]
                    name  = people.split("\n")[0].split(designation)[-1].strip()
                    address = people.replace(designation, "").replace(name, "").strip()
                    the_dict = {
                        "designation": designation,
                        "name": name,
                        "address": address.replace("\n", "")
                    }
                    people_details.append(the_dict)
            except:
                the_dict = {}
                people_details.append(the_dict)
        
            
            previous_names_detail = []
            try:
                others_name = extract_data.get('Hjánøvn','')
                names_list = others_name.split("\n")
                for name in names_list:
                    data = {}
                    data['name'] = name
                    if data['name'] != "":
                        previous_names_detail.append(data)
            except Exception as e:
                print(e)
            
            try:    
                accounting_date = extract_data.get('Roknskapir dato','').split(',')
                accounting_date_1 = accounting_date[0].strip()
                accounting_date_2 = accounting_date[1].strip()
                accounting_date_3 = accounting_date[2].split('\n')[0].strip()
            except:
                accounting_date_1, accounting_date_2, accounting_date_3 = "","",""
            OBJ = {
                "registration_number":extract_data.get('Skrásetingar-nr',''),
                "registration_date":Date,
                "name":extract_data.get('Navn','').replace('\"',''),
                'municipality':extract_data.get('Kommuna','').split('\n')[0],
                "purpose":extract_data.get('Endamál',''),
                'recruitment_rules':extract_data.get('Tekningarreglur','').split('\n')[0],
                'accounting_date_1':accounting_date_1,
                'accounting_date_2':accounting_date_2,
                'accounting_date_3':accounting_date_3,
                'participation_fee':extract_data.get('Partapeningur',''),
                "addresses_detail":[
                    {
                    "type": "registered_address",
                    "address":extract_data.get('Adressa','').replace("\n"," "),
                    "meta_detail":{
                        "address_url":adds_url
                    }
                    }
                ],
                "people_detail":people_details,
                "previous_names_detail":previous_names_detail
            }

            OBJ =  faroe_islands_crawler.prepare_data_object(OBJ)
            ENTITY_ID = faroe_islands_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ''
            ROW = faroe_islands_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            faroe_islands_crawler.insert_record(ROW)
       
        page += 1
            
    faroe_islands_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    faroe_islands_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    faroe_islands_crawler.db_log(log_data)