"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'State Register of Legal Entities',
    'COUNTRY' : 'Armenia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.e-register.am/am/search", 
                        "Source Description": "The Agency of the State Register of Legal Entities is a department within the Ministry of Justice of the Republic of Armenia. It is responsible for managing and maintaining the State Register of Legal Entities, which is a centralized database containing information about registered legal entities in Armenia."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.e-register.am/am/search'
}
crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Armenia State Register"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

armenia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = armenia_crawler.get_requests_helper()
selenium_helper =  armenia_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)

driver.get('https://www.e-register.am/am/search')
time.sleep(5)
try:
    # words = ['Ա', 'Բ','ԱԲ']
    armenian_alphabet = [
    "Ա", "Բ", "Գ", "Դ", "Ե", "Զ", "Է", "Ը", "Թ", "Ժ", "Ի", "Լ", "Խ", "Ծ", "Կ", "Հ",
    "Ձ", "Ղ", "Ճ", "Մ", "Յ", "Ն", "Շ", "Ո", "Չ", "Պ", "Ջ", "Ռ", "Ս", "Վ", "Տ", "Ր",
    "Ց", "Ւ", "Փ", "Ք", "Օ", "Ֆ"]
    start_char = sys.argv[1] if len(sys.argv) > 1 else "Ա"
    start_index = armenian_alphabet.index(start_char)
    for i in range(start_index, len(armenian_alphabet)):
        word = armenian_alphabet[i]
        print("Word:",word)
        send_key = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/form[1]/table/tbody/tr[1]/td/input[1]')
        send_key.clear()
        send_key.send_keys(word)
        search_button = driver.find_element(By.XPATH,'/html/body/div/div[1]/div/form[1]/table/tbody/tr[1]/td/input[2]')
        search_button.click()
        time.sleep(5)
        datarows = driver.find_elements(By.XPATH,'/html/body/div/div[1]/div/table[2]/tbody/tr/td/a')
        for datarow in datarows:
            next_link = datarow.get_attribute('href')
            respone = request_helper.make_request(next_link)
            STATUS_CODE = respone.status_code 
            if STATUS_CODE != 200:
                continue
            DATA_SIZE = len(respone.content)
            CONTENT_TYPE = respone.headers['Content-Type'] if 'Content-Type' in respone.headers else 'N/A'
            soup = BeautifulSoup(respone.content,'html.parser')    
            compname = soup.find('div',class_ = 'compname')
            data = {}
            data["name"] = compname.text.strip()
            table = soup.find('table',class_ = 'formtbl')
            rows = table.find_all('tr')
            for row in rows:
                cell = row.find_all('td')
                key = cell[0].text.strip()
                value = cell[1].text.strip()
                data[key] = value
            OBJ = {
                    "name":data['name'],
                    "aliases":data['name'],
                    "status":data['Կարգավիճակ'],
                    "registration_authority":data['Գրանցող մարմին'],
                    "addresses_detail":[
                            {
                                "type":"general_address",
                                "address":data['Գտնվելու վայրը'].replace("null", "").replace("  ", "").replace("None", "").replace("none", "").replace('NONE', '').replace("none,","").replace("Ոչ ոք","").replace("ՈՉ ՈՔ","").replace("դատարկ","").replace("ոչ ոք,","").replace("  ", "").strip()
                            }
                        ], 
                    "registration_date":data['Գրանցման համար'].split('/')[-1].strip(),
                    "registration_number":data['Գրանցման համար'].split('/')[0].strip(),
                    "tax_number":data['ՀՎՀՀ'],
                    "z-code":data['ՁԿԴ']
                }
            if OBJ['tax_number'] == "":
                del OBJ['tax_number']
            OBJ =  armenia_crawler.prepare_data_object(OBJ)
            ENTITY_ID = armenia_crawler.generate_entity_id(OBJ['registration_number'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = armenia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            armenia_crawler.insert_record(ROW)
    
    driver.close()
    armenia_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    armenia_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    armenia_crawler.db_log(log_data)
