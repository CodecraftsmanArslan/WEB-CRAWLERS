"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from datetime import datetime
import  random, os, tabula, math, requests
from CustomCrawler import CustomCrawler

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
FILE_PATH = os.path.dirname(os.getcwd()) + '/russia/pdf/'

meta_data = {
    'SOURCE' :'Federal Tax Service of Russia (FTS)',
    'COUNTRY' : 'Russia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://egrul.nalog.ru/index.html", 
                        "Source Description": "The Federal Tax Service of Russia (FTS) is the government agency responsible for administering tax laws and regulations in Russia. It operates under the authority of the Ministry of Finance of the Russian Federation."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://egrul.nalog.ru/index.html'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Russia",
}

russia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = russia_crawler.get_requests_helper()

def make_request(url, method="GET", data=None, max_retries=10, params=None, timeout=60):
    for retry in range(max_retries):
        try:
            response = requests.request(method, url, params=params, data=data, timeout=timeout, proxies=get_proxy(), verify=True)
            return response
        except:
            pass

def get_proxy():
    url = "https://proxy.webshare.io/api/v2/proxy/list/download/cwymlooolhnjbmymhtyzggjwlnhvudhahzxsfcuw/-/any/username/direct/japan/"
    res = requests.get(url=url)
    data = res.text
    if ':' in data and len(data.split(':')) ==4:
        host, port, username, password = data.replace('\r', '').replace('\n', '').split(':')
        proxies = {
            'http': f'http://{username}:{password}@{host}:{port}',
            'https': f'http://{username}:{password}@{host}:{port}',
        }
        return proxies
    return {}

def format_table_one(table):
    val = ""
    data_array = []
    for row_num, row in enumerate(table.values.tolist(), start=1):
        if row_num >= 3:
            if math.isnan(float(row[0])):
                val += " " + row[1]
            else:
                if len(val) > 0:
                    data_array.append(val)
                val = row[1]
    data_array.append(val)
    return data_array

def format_table_two(table):
    data_array = []
    val = list(table.columns)
    data_array.append(val)
    for row in table.values.tolist():
        data_array.append(row)
    return data_array

def format_third_table(table):
    data_array = []
    val = list(table.columns)
    data_array.append(val)
    for row in table.values.tolist():
        data_array.append(row)
    return data_array

def get_data_from_pdf():
    print("data get from pdf")
    # Path to the PDF file
    pdf_file_path = f"{FILE_PATH}pdf_file.pdf"

    result = {}
    addresses_detail = []
    additional_detail = []
    tables = tabula.read_pdf(pdf_file_path, pages='all', multiple_tables=True)
    first_data = format_table_one(tables[0])
    second_data = format_table_two(tables[1])
    data_ = format_third_table(tables[2])

    add_name = ""
    add_address = ""
    tax_registration_reason_code = ""
    date_of_registration_with_the_tax_authority = ""
    information_about_the_tax_authority = ""
    termination_date = ""
    termination_reason = ""
    legal_entity_termination_date = ""

    for val in first_data:
        if "Полное наименование на русском языке" in val:
            result["name"] = val.replace("Полное наименование на русском языке", "").strip()
        elif "ОГРН" in val and  "." not in val:
            result["registration_number"] = val.replace("ОГРН", "").strip()
        elif "Дата присвоения ОГРН" in val:
            result["assignment_date"] = val.replace("Дата присвоения ОГРН", "").strip().replace(".", "-")
        elif val.startswith("Адрес юридического лица"):
            addresses_detail.append({
                "type": "general_address",
                "address": val.replace("Адрес юридического лица", "").strip()
            })

    for val in second_data:
        if "Регистрационный номер, присвоенный до 1\rиюля 2002 года" in val:
            result["previous_registration_number"] = val[2]
        elif "Дата регистрации до 1 июля 2002 года" in val:
            result["incorporation_date"] = val[2].replace(".", "-")
        elif "Наименование регистрирующего органа" in val:
            add_name = val[2]
        elif "Адрес регистрирующего органа" in val:
            add_address = val[2]
        elif "ИНН юридического лица" in val:
            result["tax_number"] = val[2]
        elif "ГРН и дата внесения в ЕГРЮЛ записи,\rсодержащей указанные сведения" in val:
            result["registration_date"] = val[2:3][0].split('\r')[1].replace(".", "-")
        elif "Причина внесения записи в ЕГРЮЛ" in val:
            result["reason_for_entering_record"] = val[2]
        elif "КПП юридического лица" in val:
            tax_registration_reason_code = val[2]
        elif "Дата постановки на учет в налоговом\rоргане" in val:
            date_of_registration_with_the_tax_authority = val[2].replace(".", "-")
        elif "Сведения о налоговом органе, в котором\rюридическое лицо состоит (для\rюридических лиц, прекративших\rдеятельность - состояло) на учете" in val:
            information_about_the_tax_authority = val[2]
        elif "Дата прекращения" in val:
            termination_date = val[2].replace(".", "-")
        elif "Способ прекращения" in val:
            termination_reason = val[2]
        elif "Наименование органа, внесшего запись о\rпрекращении юридического лица" in val:
            legal_entity_termination_date = val[2]

    if termination_date != "" and termination_reason != "" and legal_entity_termination_date != "":
        additional_detail.append({
            "type": "termination_information",
            "data": [{
                "termination_date": termination_date,
                "termination_reason": termination_reason,
                "legal_entity_termination_date": legal_entity_termination_date
            }]
        })

    if tax_registration_reason_code != "" and date_of_registration_with_the_tax_authority != "" and information_about_the_tax_authority != "":
        additional_detail.append({
            "type": "tax_authority_information",
            "data": [{
                "tax_registration_reason_code": tax_registration_reason_code,
                "date_of_registration_with_the_tax_authority": date_of_registration_with_the_tax_authority,
                "information_about_the_tax_authority": information_about_the_tax_authority
            }]
        })

    if add_name != "":
        additional_detail.append({
            "type": "registration_authority_information",
            "data":[{
                "name": add_name,
                "address": add_address
            }]
        })

    document_info = {}
    for val in data_:
        if isinstance(val[0], str):
            if "Наименование документа" in val[0]:
                document_info["document_name"] = val[0][val[0].find("Наименование документа") + len("Наименование документа"):].strip()
            elif "Номер документа" in val[0]:
                document_info["document_number"] = val[0][val[0].find("Номер документа") + len("Номер документа"):].strip()
            elif "Дата документа" in val[0]:
                document_info["document_date"] = val[0][val[0].find("Дата документа") + len("Дата документа"):].strip().replace(".", "-")
            
            if all(key in document_info for key in ["document_name", "document_number", "document_date"]):
                additional_detail.append({
                    "type": "document_information",
                    "data": [{
                        "document_name": document_info["document_name"],
                        "document_number": document_info["document_number"],
                        "date": document_info["document_date"]
                    }]
                })
                
                document_info = {}

        result["additional_detail"] = additional_detail
        result["addresses_detail"] = addresses_detail

    return result

try:
    if len(sys.argv) > 1:
        start_region = int(sys.argv[1])
        start_character = sys.argv[2].upper()
    else:
        start_region = 77
        start_character = 'А'
    CHARACTERS = ['А','Б','В','Г','Д','Е','Ё','Ж','З','И','Й','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ъ','Ы','Ь','Э','Ю','Я','0','1','2','3','4','5','6','7','8','9']
    REGIONS = [77, 78, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 83, 86, 87, 89, 91, 92, 99]
    region_index = REGIONS.index(start_region)
    character_index = CHARACTERS.index(start_character)
    base_url = "https://egrul.nalog.ru/"
    for char in CHARACTERS[character_index:]:
        for region in REGIONS[region_index:]:
            region = f"{region:02d}"
            page_number = 0
            while page_number < 5000:
                payload = {
                    "vyp3CaptchaToken": "",
                    "page": page_number,
                    "query": char,
                    "region": region,
                    "PreventChromeAutocomplete":""
                }
                response = make_request(url=base_url, method="POST", data=payload)
                if response is None: continue
                res = response.json()
                t_ = res.get('t')
                random_number = random.randint(10 ** (13 - 1), (10 ** 13) - 1)
                params = {
                    "r": random_number,
                    "_": random_number + 1
                }
                response = make_request(url=f"{base_url}search-result/{t_}", params=params)
                if response is None: continue
                rows = response.json()
                if 'rows' in rows:
                    for i, row in enumerate(rows['rows']):
                        print(f"region {region} - character {char} - page {page_number}")
                        response = make_request(url=f"{base_url}vyp-request/{row['t']}")
                        response = make_request(url=f"{base_url}vyp-status/{row['t']}")
                        response = make_request(url=f"{base_url}vyp-download/{row['t']}")
                        if response is None: continue
                        FILENAME = f"pdf_file.pdf"
                        if response.status_code == 200:
                            with open(os.path.join(FILE_PATH, FILENAME), 'wb') as pdf_file:
                                pdf_file.write(response.content)
                            try: data = get_data_from_pdf()
                            except: continue
                            print(data)
                            NAME = data.get('name') if data.get('name') is not None else ""
                            registration_number = data.get('registration_number') if data.get('registration_number') is not None else ""
                            if registration_number == "" or NAME == "":
                                continue
                            ENTITY_ID = russia_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
                            BIRTH_INCORPORATION_DATE = ''
                            DATA = russia_crawler.prepare_data_object(data)
                            print(DATA)
                            ROW = russia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                            russia_crawler.insert_record(ROW)
                page_number += 1


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    russia_crawler.db_log(log_data)
    russia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    russia_crawler.db_log(log_data)
