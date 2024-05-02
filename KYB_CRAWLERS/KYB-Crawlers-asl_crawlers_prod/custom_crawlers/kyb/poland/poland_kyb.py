"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import os base64
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util import Padding
from dateutil import parser

meta_data = {
    'SOURCE' :'Portal Rejestrów Sądowych',
    'COUNTRY' : 'Poland',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://wyszukiwarka-krs.ms.gov.pl/", 
                        "Source Description": "The ''Portal Rejestrów Sądowych'' is the official online portal for court registers in Poland. It provides access to various registers and databases related to legal entities, including commercial registers, associations registers, and cooperative registers. The portal allows users to search and retrieve information about registered entities, such as company names, addresses, registration numbers, shareholders, and other relevant details."},
    'URL' : 'https://wyszukiwarka-krs.ms.gov.pl/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Poland'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

poland_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  poland_crawler.get_requests_helper()

def get_encrypted_id(uid: str):
    content = uid
    bs = AES.block_size
    secretKey = "TopSecretApiKey1"
    key = secretKey.encode()
    iv = secretKey.encode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    body = Padding.pad(content.encode('utf-8'), bs)
    cipherText = b64encode(cipher.encrypt(body)).decode('utf-8')
    return cipherText

def format_date(timestamp):
    date_str = ""
    try:
        # Parse the timestamp into a datetime object
        datetime_obj = parser.parse(timestamp)
        # Extract the date portion from the datetime object
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 101

try:

    for i in range(start, 1043098):
        additional_detail = []
        contacts_detail = []
        people_detail = []
        addresses_detail = []
        number = str(i).zfill(10)
        print("Record No. ", number)
        krs = get_encrypted_id(number)
        url = f"https://prs-openapi2-prs-prod.apps.ocp.prod.ms.gov.pl/api/wyszukiwarka/danepodmiotu"
        payload = {"krs": krs}
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(str(payload))),
            'Host': 'prs-openapi2-prs-prod.apps.ocp.prod.ms.gov.pl',
            'x-api-key': 'TopSecretApiKey'
        }
        response = request_helper.make_request(url, method="POST", json=payload, headers=headers)

        try:
            data = response.json()
        except:
            continue

        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        NAME = data.get('nazwa').replace('"', '').replace("%", "%%") if data.get('nazwa') is not None else ""
        registration_number = data.get('numerKRS') if data.get('numerKRS') is not None else ""
        register = "Rejestr Przedsiębiorców"
        tax_identification_number = data.get('nip') if data.get('nip') is not None else ""
        regon = data.get('regon') if data.get('regon') is not None else ""
        legal_form = data.get('formaPrawna').replace("%", "%%") if data.get('formaPrawna') is not None else ""
        registration_date = data.get('dataWpisuDoRP')
        if registration_date is None or registration_date == "":
            registration_date  = data.get('dataWpisuDoRS') if data.get('dataWpisuDoRS') is not None else ""
        removal_date = data.get('dataWykresleniaZRP')
        if removal_date is None or removal_date == "":
            removal_date = data.get('dataWykresleniaZRS') if data.get('dataWykresleniaZRS') is not None else ""
        dissolution_date = data.get('dataUprawomocnieniaWykresleniaZKRS')
        if data.get('dataWznowieniaDzialalnosci') is not None and data.get('dataWznowieniaDzialalnosci') != "" or data.get('dataZawieszeniaDzialalnosci') is not None and data.get('dataZawieszeniaDzialalnosci') != "":
            additional_detail.append({
                "type": "suspension_information",
                "data": [{
                    "suspension_date": data.get('dataWznowieniaDzialalnosci').replace("%", "%%") if data.get('dataWznowieniaDzialalnosci') is not None else "",
                    "resumption date": data.get('dataZawieszeniaDzialalnosci').replace("%", "%%") if data.get('dataZawieszeniaDzialalnosci') is not None else ""
                }]
            })

        if data.get('adres') is not None and data.get('adres') != "":
            office_address = f"{data.get('wojewodztwo')}, {data.get('powiat')}, {data.get('gmina')}, {data.get('miejscowosc')}, {data.get('adres')}, {data.get('kodPocztowy')}"
            if office_address is not None and office_address.strip().replace(",","") != "":
                addresses_detail.append({
                    "type": "office_address",
                    "address": office_address.replace(', ,', ',').replace("%", "%%")
                })

        if data.get("adresWWW") is not None and data.get("adresWWW") != "":
            contacts_detail.append({
                "type": "website_link",
                "value": data.get("adresWWW").replace("%", "%%")
            })
        if data.get("email") is not None and data.get("email") != "":
            contacts_detail.append({
                "type": "email",
                "value": data.get("email").replace("%", "%%")
            })
        
        bankrupcy_detail = data.get("daneDotyczaceUpadlosci")
        if bankrupcy_detail is not None and "nazwaOrganu" in bankrupcy_detail:
            additional_detail.append({
                "type": "Bankruptcy_proceeding_information",
                "data": [{
                    "authority_name": bankrupcy_detail.get("nazwaOrganu").replace("%", "%%") if bankrupcy_detail.get("nazwaOrganu") is not None else "",
                    "legal_act_signature": bankrupcy_detail.get("sygnaturaAktuPraw").replace("%", "%%") if bankrupcy_detail.get("sygnaturaAktuPraw") is not None else "",
                    "issue_date": format_date(bankrupcy_detail.get("dataWydaniaAktuPraw")),
                    "conducting_manner": bankrupcy_detail.get('sposobProwadzeniaPostPraw').replace("%", "%%") if bankrupcy_detail.get('sposobProwadzeniaPostPraw') is not None else "",
                    "completion_date": format_date(bankrupcy_detail.get('dataZakonczeniaPostUpad')),
                    "completion_manner": bankrupcy_detail.get("sposobZakonczeniaPostUpad").replace("%", "%%") if bankrupcy_detail.get("sposobZakonczeniaPostUpad") is not None else ""
                }]
            })

        if data.get('nazwaOrganuRep') is not None and data.get('nazwaOrganuRep') != "":
            additional_detail.append({
                "type": "representation_body_information",
                "data": [{
                    "name": data.get('nazwaOrganuRep').replace("%", "%%"),
                    "way_of_representation": data.get('sposobRep').replace("%", "%%") if data.get('sposobRep') is not None else ""
                }]
            })
        
        members = data.get('listaCzlonkowReprezentacji')
        if members is not None and len(members) > 0:
            for member in members:
                member_name = f"{member.get('nazwisko')}, {member.get('nazwa')}, {member.get('imiePierwsze')}, {member.get('imieDrugie')}"
                if member_name is not None and member_name.strip().replace(',', '') != "":
                    people_detail.append({
                        "name": member_name.replace(', ,', ',').replace("%", "%%"),
                        "designation": member.get("funkcja").replace("%", "%%") if member.get("funkcja") is not None else ""
                    })

        DATA = {
            "name": NAME,
            "registration_number": registration_number,
            "register_name": register,
            "tax_number": tax_identification_number,
            "business_number": regon,
            "type": legal_form,
            "registration_date": format_date(registration_date),
            "removal_date": format_date(removal_date),
            "dissolution_date": format_date(dissolution_date),
            "additional_detail": additional_detail,
            "contacts_detail": contacts_detail,
            "people_detail": people_detail,
            "addresses_detail": addresses_detail
        }

        ENTITY_ID = poland_crawler.generate_entity_id(reg_number=registration_number)
        BIRTH_INCORPORATION_DATE = ''
        DATA = poland_crawler.prepare_data_object(DATA)
        ROW = poland_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
        poland_crawler.insert_record(ROW)


    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    poland_crawler.db_log(log_data)
    poland_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    poland_crawler.db_log(log_data)