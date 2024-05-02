"""Import required library"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
import json
import string


meta_data = {
    'SOURCE': 'Registro Público de la Propiedad',
    'COUNTRY': 'Nicaragua',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.registropublico.gob.ni/Servicios/Consultas/ConsultaSociedad.aspx",
                      "Source Description": "The 'Registro Público de la Propiedad' (Public Registry of Property) in Nicaragua is a government institution responsible for maintaining and recording the ownership rights and legal status of real estate properties within the country. It is a centralized database that holds official records related to property ownership, mortgages, liens, and other encumbrances."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.registropublico.gob.ni/Servicios/Consultas/ConsultaSociedad.aspx'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Nicaragua"
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = _crawler.get_requests_helper()
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
          'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
API_URL = (
    f'https://ventanilla.registropublico.gob.ni/VentanillaPrivada/API/VentanillaLinea/ObtenerEstadoSociedad?pTipoBusqueda=Nombre&pValorBusqueda=')

"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv

if len(sys.argv) > 1:
        start_letter = arguments[1].lower()
else:
    start_letter = 'a'

if start_letter < 'a' or start_letter > 'z':
    print("Invalid start letter. The letter should be from 'a' to 'z'.")    
else:
        alphabet = string.ascii_lowercase[string.ascii_lowercase.index(start_letter):]


def crawl():
    for letter in alphabet:
        print(f"Scrapping data of alphabet {letter}")
        res = request_helper.make_request(API_URL + letter)
        SATAUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        api_data = res.json()
        json_data = json.loads(api_data)

        for data in json_data:
            registration_number = data["NumeroUnico"]
            name_ = data["RazonSocial"]
            aliases = data["abreviatura"]
            status = data["EstadoSociedad"]
            location = data["Ubicacion"]
            trade_name = data["NombreComercial"] if data["NombreComercial"] is not None else ""

            OBJ = {
                "registration_number": registration_number,
                "name": name_,
                "aliases": aliases if aliases is not None else "",
                "status": status if status is not None else "",
                "location": location,
                "trade_name": trade_name.replace("%", "%%")
            }
            OBJ = _crawler.prepare_data_object(OBJ)
            ENTITY_ID = _crawler.generate_entity_id(
                OBJ['registration_number'], OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ''
            ROW = _crawler.prepare_row_for_db(
                ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
            _crawler.insert_record(ROW)

        return SATAUS_CODE, DATA_SIZE, CONTENT_TYPE


try:
    SATAUS_CODE, DATA_SIZE, CONTENT_TYPE = crawl()
    _crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": "",  "crawler": "HTML"}
    _crawler.db_log(log_data)
    _crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    _crawler.db_log(log_data)
