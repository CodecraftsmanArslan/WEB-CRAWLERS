"""Import required library"""
import traceback,sys,time, requests
from bs4 import BeautifulSoup
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from multiprocessing import Pool, Process, freeze_support
import multiprocessing
from load_env.load_env import ENV
import os


meta_data = {
    'SOURCE' :'Agjencia e Regjistrimit të Bizneseve Kosovo (ARBK)',
    'COUNTRY' : 'Kosovo',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://arbk.rks-gov.net/page.aspx?id=2,1", 
                        "Source Description": "The Agjencia e Regjistrimit të Bizneseve Kosovo (ARBK) serves as the central authority for business registration and regulation in Kosovo. Its primary role is to facilitate the establishment and operation of businesses by providing efficient and transparent registration services."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://arbk.rks-gov.net/page.aspx?id=2,1'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Kosovo Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
START_ID = int(arguments[1]) if len(arguments)>1 else 1

kosovo_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  kosovo_crawler.get_requests_helper()



if ENV["ENVIRONMENT"] == "LOCAL":
    FILE_PATH = os.path.dirname(os.getcwd())+ "/kosovo"
else:
    FILE_PATH = os.path.dirname(os.getcwd())+ "/KYB-Crawlers/crawlers_v2/official_registries/kosovo"

URL = 'https://arbk.rks-gov.net/page.aspx?id=1,38,000001'

def generate_urls(start_id, end_id):
        base_url = "https://arbk.rks-gov.net/page.aspx?id=1,38,{:06d}"
        urls = []

        for id_num in range(start_id, end_id + 1):
            url = base_url.format(id_num)
            urls.append(url)

        return urls


def process_url(url):
        print(url)
        try:
            response = request_helper.make_request(url,timeout = 100, max_retries=6)
            if response.status_code == 500:
                return {"status": "skipped", "url": url, "message": "Skipped due to status code 500"}
            STATUS_CODE= response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            soup = BeautifulSoup(response.content,'html.parser')
            table1 = soup.find_all('table',class_ = 'views-table')[0]
            table2 = soup.find_all('table', class_ = 'views-table')[1]
            table3 = soup.find_all('table', class_ = 'views-table')[2]
            table4 = soup.find_all('table', class_ = 'views-table')[4]
            # table 1
            trs = table1.find_all('tr')
            data_dict = {}
            for tr in trs:
                with open(f"{FILE_PATH}/crawled_records.txt", "r") as crawled_records:
                    file_contents = crawled_records.read()
                    if url in file_contents:
                          continue
                cells = tr.find_all('td')
                keys  =cells[0].find('b').text.strip()
                values = cells[1].text.strip()
                data_dict[keys] = values
            # table 2
            table2_trs = table2.find_all('tr')
            for tr in table2_trs:
                cells = tr.find_all('td')
                name = cells[0].text.strip()
                last_name = cells[1].text.strip()
                designation = cells[2].text.strip()
                power = cells[3].text.strip()
                data_dict['name'] = name
                data_dict['last_name'] = last_name
                data_dict['designation'] = designation
                data_dict['power'] = power 
            #table 3
            table3_trs = table3.find_all('tr')
            for tr_ in table3_trs[1:]:
                cell = tr_.find_all('td')
                name_surname = cell[0].text.strip()
                capital_in = cell[1].text.strip()
                capital_in_ = cell[2].text.strip()
                data_dict['name_surname'] = name_surname
                data_dict['capital_€'] =  capital_in if capital_in != '€' else ''
                data_dict['capital_%'] =  capital_in_ if capital_in_ != '%' else ''
            # table 4
            rows = table4.find_all('tr') 
            activity_information = []
            for row in rows[1:]:
                table_cell = row.find_all('td')
                code = table_cell[0].text.strip()
                description = table_cell[1].text.strip()
                type = table_cell[2].text.strip()
                activity = {
                    'activity_code':code,
                    "name":description,
                    "activity_type":type
                }
                activity_information.append(activity)
            #Data Object
            OBJ = {
                    "name": data_dict['Emri i biznesit'],
                    "aliases":data_dict['Emri tregtar'].replace("///","").replace("\"",""),
                    "type":data_dict['Lloji biznesit'].replace("///",""),
                    "registration_number":data_dict['Numri unik identifikues'].replace("///",""),
                    "business_number":data_dict['Numri i biznesit'].replace("///",""),
                    "fiscal_number":data_dict['Numri fiskal'].replace("///",""),
                    "tax_number":data_dict['Numri certifikues KTA'].replace("///",""),
                    "number_of_employees":data_dict['Numri punëtorëve'].replace("///",""),
                    "registration_date":data_dict['Data e regjistrimit'].replace("/","-"),
                    "jurisdiction":data_dict.get('Komuna',""),
                    "addresses_detail":[
                        {
                            "type":"general_address",
                            "address":data_dict['Adresa'].replace(', ,','')
                        }
                    ], 
                    "contacts_detail":[
                        {
                            "type":"telephone_number",
                            "value":data_dict['Telefoni'].replace("///","")
                        },
                        {
                            "type":"email",
                            "value":data_dict['E-mail'].replace("///","")
                        },
                    ],
                    "status":data_dict['Statusi në ARBK'],
                    "capital":data_dict['Kapitali'] if data_dict['Kapitali'] != "€" else "",
                    "tax_authority_status":data_dict['Statusi në ATK'].replace("///",""),
                    "additional_detail":[
                        {
                            "type": "activity_information",
                            "data":activity_information
                        }
                        
                    ],
                    "people_detail":[
                        {
                            "name":data_dict["name"]+' '+data_dict['last_name'],
                            "designation":data_dict['designation'],
                            "meta_detail":{
                                "power":data_dict['power'].replace("%","%%")
                            }     
                        },
                        {
                            "name": data_dict.get('name_surname',''),
                            "designation": 'owner/shareholder',
                            "meta_detail": {
                                "capital_€": data_dict.get('capital_€',''),
                                "capital_%%": data_dict.get('capital_%','').replace("%","%%")
                            }
                        }
                    ] 
                }
            OBJ =  kosovo_crawler.prepare_data_object(OBJ)
            ENTITY_ID = kosovo_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = kosovo_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            kosovo_crawler.insert_record(ROW)
            with open(f"{FILE_PATH}/kosovo_crawled_records.txt", "a") as crawled_records:
                    crawled_records.write(url + "\n")

          

        except Exception as e:
            tb = traceback.format_exc()
            log_data = {"status": "fail", "error": str(e), "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"), "crawler": "HTML"}
            kosovo_crawler.db_log(log_data)
    



def main():

        # Divide all_urls into chunks
        range1_start_id = START_ID
        range1_end_id = 199782

        range2_start_id = 200780
        range2_end_id = 247778
        all_urls = generate_urls(range1_start_id, range1_end_id) + generate_urls(range2_start_id, range2_end_id)
        
        
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
             results = pool.map(process_url, all_urls)


        for result in results:
            kosovo_crawler.db_log(result)

        kosovo_crawler.end_crawler()
        log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
        kosovo_crawler.db_log(log_data)

if __name__ == "__main__":
    main()


