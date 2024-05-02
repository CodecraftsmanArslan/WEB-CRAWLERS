"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import warnings
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
warnings.filterwarnings('ignore')

meta_data = {
    'SOURCE' :'Handelsregister des Fürstentums',
    'COUNTRY' : 'Liechtenstein',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.oera.li/cr-portal/suche/suche.xhtml", 
                        "Source Description": "The Commercial Register of the Principality of Liechtenstein is a governmental registry that records all companies and business entities registered in Liechtenstein. It serves the purpose of documenting and providing transparency regarding economic activities in the country. The Commercial Register contains information such as company names, legal forms, registered offices, directors, and shareholdings of the registered entities, which are made publicly accessible."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.oera.li/cr-portal/suche/suche.xhtml'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Liechtenstein Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


liechtenstein_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  liechtenstein_crawler.get_requests_helper()
session =  liechtenstein_crawler.get_requests_session()
selenium_helper = liechtenstein_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

def get_seeion_values(url):
    
    headers = {
        "Accept":"application/xml, text/xml, */*; q=0.01",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest"
    }

    res = session.get(url, headers=headers)
    
    soup = BeautifulSoup(res.text, 'lxml')
    view_state = soup.find('input',id='j_id1:javax.faces.ViewState:0').get('value')
    script_nonce = soup.find('script').get('nonce')

    session_id = session.cookies.get('JSESSIONID')
    return headers ,view_state, script_nonce, session_id

def get_hinput(alphabet, municipality):
    driver.get('https://www.oera.li/cr-portal/suche/suche.xhtml')
    input_element = driver.find_element(By.ID, "idSucheForm:idFirma")
    input_element.send_keys(alphabet)
    drop_down_element = driver.find_element(By.CLASS_NAME, "ui-accordion-header")
    drop_down_element.click()
    time.sleep(3)
    search_element = driver.find_element(By.ID, "idSucheForm:panel:idSitz_input")
    search_element.send_keys(municipality)
    time.sleep(3)
    li_element = driver.find_element(By.CLASS_NAME, "ui-autocomplete-item")
    li_element.click()
    time.sleep(4)
    value_element = driver.find_element(By.ID, "idSucheForm:panel:idSitz_hinput")
    idSitz_hinput = value_element.get_attribute("value")
    
    return  alphabet , municipality, idSitz_hinput
    
try:
    
    API = 'https://www.oera.li/cr-portal/suche/suche.xhtml'
    headers ,view_state, script_nonce, session_id = get_seeion_values(API)
    Alphabets = ['__a', '__b', '__c', '__d', '__e', '__f', '__g', '__h', '__i', '__j', '__k', '__l', '__m', '__n', '__o', '__p', '__q', '__r', '__s', '__t', '__u', '__v', '__w', '__x', '__y', '__z', 'Vaduz', 'Schaan', 'Triesen', 'Balzers', 'Eschen', 'Mauren', 'Triesenberg', 'Ruggell', 'Gamprin', 'Planken', 'Schellenberg']
    Municipalites = ['Vaduz', 'Schaan', 'Triesen', 'Balzers', 'Eschen', 'Mauren', 'Triesenberg', 'Ruggell', 'Gamprin', 'Planken', 'Schellenberg']
    for alphabet in Alphabets:
        for municipality in Municipalites:
            alphabet , municipality, idSitz_hinput = get_hinput(alphabet, municipality)
                                                                                
            res2 = session.post(API+f';jsessionid={session_id}',headers=headers,data=f'javax.faces.partial.ajax=true&javax.faces.source=idSucheForm%3Aj_idt143&javax.faces.partial.execute=%40all&javax.faces.partial.render=idSucheForm&idSucheForm%3Aj_idt143=idSucheForm%3Aj_idt143&idSucheForm=idSucheForm&idSucheForm%3AidFirma={alphabet}&idSucheForm%3Apanel%3AidRechtsform_focus=&idSucheForm%3Apanel%3AidRechtsform_input=&idSucheForm%3Apanel%3AidSitz_input={municipality}&idSucheForm%3Apanel%3AidSitz_hinput={idSitz_hinput}&idSucheForm%3Apanel%3AidShabDatum_input=&idSucheForm%3Apanel%3AidShabNummer=&idSucheForm%3Apanel_active=-1%2C0&javax.faces.ViewState={view_state}&primefaces.nonce={script_nonce}')
            for i in range(0, 500, 10):
                if i % 4 == 0:
                    payload = f'javax.faces.partial.ajax=true&javax.faces.source=idSucheForm%3AresultTable&javax.faces.partial.execute=idSucheForm%3AresultTable&javax.faces.partial.render=idSucheForm%3AresultTable&idSucheForm%3AresultTable=idSucheForm%3AresultTable&idSucheForm%3AresultTable_pagination=true&idSucheForm%3AresultTable_first={i}&idSucheForm%3AresultTable_rows=20&idSucheForm%3AresultTable_skipChildren=true&idSucheForm%3AresultTable_encodeFeature=true&idSucheForm=idSucheForm&idSucheForm%3AidFirma={alphabet}&idSucheForm%3Apanel%3AidRechtsform_focus=&idSucheForm%3Apanel%3AidRechtsform_input=&idSucheForm%3Apanel%3AidSitz_input={municipality}&idSucheForm%3Apanel%3AidSitz_hinput={idSitz_hinput}&idSucheForm%3Apanel%3AidShabDatum_input=&idSucheForm%3Apanel%3AidShabNummer=&idSucheForm%3Apanel_active=-1%2C0&idSucheForm%3AresultTable%3Aj_idt150%3Afilter=&idSucheForm%3AresultTable%3Aj_idt153%3Afilter=&idSucheForm%3AresultTable%3Aj_idt156%3Afilter=&idSucheForm%3AresultTable%3Aj_idt159%3Afilter=&idSucheForm%3AresultTable_selection=&javax.faces.ViewState={view_state}&primefaces.nonce={script_nonce}'
                    
                    print(payload)
                    api_response = session.post(API, headers=headers,data=payload)
                    STATUS_CODE = api_response.status_code
                    DATA_SIZE = len(api_response.content)
                    CONTENT_TYPE = api_response.headers['Content-Type'] if 'Content-Type' in api_response.headers else 'N/A'
                    soup2 = BeautifulSoup(api_response.text,'lxml')
                    rows = soup2.find_all('tr', class_ = 'ui-datatable-even')
                    
                    for row in rows:
                        data = {}
                        cells = row.find_all('td')
                        registration_number = cells[0].text.strip()
                        company_name = cells[1].text.strip()
                        municipality = cells[2].text.strip()
                        company_type = cells[3].text.strip()
                        data['registration_number'] = registration_number
                        data['company_name'] = company_name
                        data['municipality'] = municipality
                        data['company_type'] = company_type
                        
                        base_url = f'https://www.oera.li/cr-portal/auszug/auszug.xhtml?uid={registration_number}'
                        
                        res2_ = session.get(base_url, headers=headers)
                        soup2_ = BeautifulSoup(res2_.text, 'lxml')
                        view_state_ = soup2_.find('input',id='j_id1:javax.faces.ViewState:0').get('value')
                        script_nonce_ = soup2_.find('script').get('nonce')

                        second_payload = {
                            "javax.faces.partial.ajax":True,
                            "javax.faces.source":"idAuszugForm:auszugContentPanel",
                            "primefaces.ignoreautoupdate":True,
                            "javax.faces.partial.execute":"idAuszugForm:auszugContentPanel",
                            "javax.faces.partial.render":"idAuszugForm:auszugContentPanel",
                            "idAuszugForm:auszugContentPanel":"idAuszugForm:auszugContentPanel",
                            "idAuszugForm:auszugContentPanel_load":True,
                            "idAuszugForm":"idAuszugForm",
                            "javax.faces.ViewState":"",
                            "primefaces.nonce":"",
                        }

                        second_payload['javax.faces.ViewState'] = view_state_
                        second_payload['primefaces.nonce'] = script_nonce_

                        auszug_url = 'https://www.oera.li/cr-portal/auszug/auszug.xhtml'

                        auszug_response = session.post(auszug_url,data = second_payload, headers=headers)
                        soup3 = BeautifulSoup(auszug_response.text, 'lxml')
                        table1 = soup3.find_all('table', class_ = 'table')[2]
                        table2 = soup3.find_all('table',class_ = 'table')[3]
                        try:
                            table3 = soup3.find_all('table',class_ = 'table')[4]
                        except:
                            table3 = soup3.find_all('table',class_ = 'table')[3]

                        table1_rows = table1.find_all('tr')
                        for table_row in table1_rows[1:]:
                            table_cells = table_row.find_all('td')
                            ei_num = table_cells[0].text.strip()
                            address = table_cells[2].text.strip()
                            data['ei_num'] = ei_num
                            data['address'] = address
                        
                        additional_data = []
                        table2_rows = table2.find_all('tr')
                        for table_row2 in table2_rows[1:]:
                            table2_cells = table_row2.find_all('td')
                            ref = table2_cells[0].text.strip()
                            try:
                                tr_nr = table2_cells[1].text.strip()
                            except:
                                tr_nr = ""
                            try:
                                tr_datum = table2_cells[2].text.strip().replace(".","-")
                            except:
                                tr_datum = ""
                            if ref or tr_nr or tr_datum:
                                data_dict = {
                                    "reference_number":ref,
                                    "daily_register_number":tr_nr,
                                    "daily_register_date":tr_datum
                                }
                                additional_data.append(data_dict)
                        
                        table3_rows = table3.find_all('tr')
                        for table_row3 in table3_rows[1:]:
                            table3_cells = table_row3.find_all('td')
                            ref_ = table3_cells[0].text.strip()
                            try:
                                tr_nr_ = table3_cells[1].text.strip()
                            except:
                                tr_nr_ = ""
                            try:
                                tr_datum_ = table3_cells[2].text.strip().replace(".","-")
                            except:
                                tr_datum_ = ""
                            if ref_ or tr_nr_ or tr_datum_:
                                data_dict_ = {
                                    "reference_number":ref_,
                                    "daily_register_number":tr_nr_,
                                    "daily_register_date": tr_datum_
                                }
                                additional_data.append(data_dict_)

                        OBJ = {
                                "name":data['company_name'],
                                "type":data['company_type'],
                                "registration_number":data['registration_number'],
                                "registration_date":data.get('daily_register_date',""),
                                "municipality":data['municipality'],
                                "addresses_detail":[
                                    {
                                        "type":"general_address",
                                        "address": data['address'],
                                        "meta_detail":{
                                            "reference_number":data['ei_num']
                                        }
                                    }
                                ], 
                                "additional_detail":[
                                        {
                                            "type": "daily_register_information",
                                            "data": additional_data
                                        }
                                ], 
                            }
                        
                        OBJ =  liechtenstein_crawler.prepare_data_object(OBJ)
                        ENTITY_ID = liechtenstein_crawler.generate_entity_id(OBJ['registration_number'],company_name=OBJ['name'])
                        NAME = OBJ['name']
                        BIRTH_INCORPORATION_DATE = ""
                        ROW = liechtenstein_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                        liechtenstein_crawler.insert_record(ROW)

    liechtenstein_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    liechtenstein_crawler.db_log(log_data)
    driver.close()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    liechtenstein_crawler.db_log(log_data) 
    driver.close()          