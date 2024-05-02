"""Set System Path"""
import traceback
from CustomCrawler import CustomCrawler
import os, re, sys
from dotenv import load_dotenv
load_dotenv()
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

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
    'SOURCE' :'Registre National du Commerce et des Sociétés - Centre de Madagascar',
    'COUNTRY' : 'Madagascar',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.rcsmada.mg/index.php?pgdown=recherche2", 
                        "Source Description": '"Registre National du Commerce et des Sociétés - Centre de Madagascar." It is the National Register of Commerce and Companies for the Central region of Madagascar. The RNCS-CM is responsible for the registration and administration of businesses and corporate entities operating within the central region of Madagascar.'},
    'URL' : 'https://www.rcsmada.mg/index.php?pgdown=recherche2',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED':False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Madagascar Official Registry"
}

ZIP_CODES = ""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

madagascar_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  madagascar_crawler.get_requests_helper()
flag = True

def get_request_param(url, greffe):
    params = {}
    payload = {
        'TypeSociete': 'Null',
        'Immatriculation': '',
        'Greffe': greffe,
        'DateInscrit': '',
        'Nom': '',
        'NomCommercial': '',
        'Denomination': '',
        'FormeJuridiq':'Null',
        'Sigle': '',
        'Enseigne': ''
    }
    res = request_helper.make_request(url, method="POST", data=payload)
    soup = BeautifulSoup(res.content, 'html.parser')
    button_span = soup.find_all('div', class_="corps")
    anchor_tags = button_span[1].find_all('a')
    for anchor_tag in anchor_tags:
        href_url = anchor_tag.get('href')
        parsed_url = urlparse(href_url)
        query_params = parse_qs(parsed_url.query)
        req_val = query_params.get('req', [''])[0]
        if req_val:
            params['req'] = req_val
            break

    pattern = re.compile(r'Nombre de page : (\d+)')  # Regular expression to capture the number
    p_tags = soup.find_all('p')
    for p_tag in p_tags:
        match = pattern.search(p_tag.get_text())
        if match:
            params['number'] = match.group(1)
            break

    return params


def crawl():  
    
        API_URL="https://www.rcsmada.mg/index.php?pgdown=recherche2"
        greffe_values = [1, 2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                        22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
                        37, 38, 39, 40, 41]

        start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        for greffe in greffe_values:
                if start > greffe:
                    continue
                req_param = get_request_param(API_URL, greffe)
                for page in range(int(req_param['number'])+1):
                    print(f"Page: {page}")
                    try:
                        res = request_helper.make_request(f"https://www.rcsmada.mg/index.php?pgdown=recherche2&page={page}&req={req_param['req']}==&deb={page}")
                    except:
                        continue
                    soup = BeautifulSoup(res.content, 'html.parser')
                    t_body = soup.find('tbody')
                    dinfos_links = t_body.find_all('a', string=lambda text: "d'Infos" in text)
                    for link in dinfos_links:
                        print(f"Record No: {greffe}")
                        href_info=link['href']
                        new_url="https://www.rcsmada.mg/"+href_info
                        response = request_helper.make_request(new_url)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        table = soup.find('table', class_='simple2')
                        rows = table.find_all('tr')
                        data_dict = {}
                        for row in rows:
                            tds = row.find_all('td')
                            key = tds[0].text.strip()
                            value = tds[1].text.strip()
                            if key in data_dict:
                                continue
                            data_dict[key] = value
                        NAME = data_dict.get('Denomination', '').replace(":","").replace("\"","").replace("%", "%%")
                        taxable_type = data_dict.get("Type d'entreprise", '')
                        type = data_dict.get('Forme juridique', '')
                        reg_number = data_dict.get('Immatriculation', '')
                        address = data_dict.get('Adresse', '')
                        reg_date = data_dict.get("Date d'immatriculation", '')
                        matching_keys = [key for key in data_dict.keys() if 'Date de' in key]
                        if matching_keys:
                            key_to_get = matching_keys[0]
                            incorporation_date = data_dict[key_to_get].strip()
                        else:
                            incorporation_date = ""
                        capital = data_dict.get('Capital', '')
                        matching_keys = [key for key in data_dict.keys() if 'Activit' in key]
                        if matching_keys:
                            key_to_get = matching_keys[0]
                            industries = data_dict[key_to_get].strip()
                        else:
                            industries = ""
                        aliases = data_dict.get('Sigle', '')
                        matching_keys = [key for key in data_dict.keys() if 'Civilit' in key]
                        if matching_keys:
                            key_to_get = matching_keys[0]
                            civility = data_dict[key_to_get].strip()
                        else:
                            civility = ""
                        acronym = data_dict.get('Enseigne', '')
                        trade_name = data_dict.get('Nom commercial')
                        dirigeant_tables = table.find_all('table')
                        people_detail = []
                        for dirigeant_table in dirigeant_tables:
                            rows = dirigeant_table.find_all('tr')
                            arr = []
                            for row in rows:
                                columns = row.find_all('td')
                                designation = columns[0].get_text(strip=True)
                                data = columns[1].get_text(strip=True)
                                arr.append(data)
                            people_detail.append({
                                "designation": arr[0].replace(":","").replace("%", "%%"),
                                "name": arr[1].replace(":","").replace("%", "%%"),
                                "address": arr[2].replace(":","").replace("%", "%%"),
                                "meta_detail": {
                                    "date_of_birth": arr[3].replace('\n', '').replace('\t', '').replace("/", "-").replace(":",""),
                                    "spouse": arr[4].replace('\n', '').replace('\t', '').replace("/", "-").replace(":","") if len(arr) > 4 else ""
                                }
                            })
                        DATA = {
                            "name":NAME,
                            "aliases":aliases.replace(":",""),
                            "type":type.replace('\n', '').replace('\t', ''),
                            "capital":capital.replace("%", "%%"),
                            "incorporation_date":incorporation_date.replace("/", "-").replace(":",""),
                            "industries":industries.replace("%", "%%"),
                            "registration_number":reg_number,
                            "registration_date":reg_date.replace("/", "-").replace(":",""),
                            "taxable_type":taxable_type,
                            "civility": civility,
                            "acronym": acronym,
                            "trade_name": trade_name,
                            "addresses_detail": [
                                {
                                    "address": address.replace(":","").replace("%", "%%"),
                                    "type": "general_address"
                                }
                            ],
                            "people_detail":people_detail
                        }
                        ENTITY_ID = madagascar_crawler.generate_entity_id(company_name=NAME, reg_number=reg_number)
                        BIRTH_INCORPORATION_DATE = incorporation_date.replace("/", "-").replace(":","")
                        DATA = madagascar_crawler.prepare_data_object(DATA)
                        ROW = madagascar_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
                        madagascar_crawler.insert_record(ROW)          
        return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
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
    madagascar_crawler.db_log(log_data)
    madagascar_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    madagascar_crawler.db_log(log_data)
