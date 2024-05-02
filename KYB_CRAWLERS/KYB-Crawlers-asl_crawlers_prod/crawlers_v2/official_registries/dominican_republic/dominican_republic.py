import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import requests
from CustomCrawler import CustomCrawler
from datetime import datetime
from dateutil import parser


meta_data = {
    'SOURCE' :'Oficina Nacional De La Propiedad Industrial',
    'COUNTRY' : 'Dominican Republic',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.onapi.gov.do/index.php/busqueda-consulta-de-invenciones", 
                        "Source Description": "ONAPI is an Institution attached to the Ministry of Industry, Commerce and MSMEs (MICM), with technical autonomy and its own assets, which manages everything related to the granting, maintenance and validity of the different modalities of Industrial Property (Invention Patents). , Utility Models, Registry of Industrial Designs and Distinctive Signs)."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.onapi.gov.do/index.php/busqueda-consulta-de-invenciones'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME':  "Dominican Republic"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

dominican_republic = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  dominican_republic.get_requests_helper()
s = dominican_republic.get_requests_session()



url = "https://www.onapi.gob.do/busqapi/patentes?solicitud=&titulo=__&resumen=&solicitante=&paissol=&inventor=&tipo=&cip=&numreg=&paisprio=&prioridad=&tipoExped=&serexped=0&numexped=0"

payload = {}
headers = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Referer': 'https://www.onapi.gob.do/busquedas2021/patentes/buscar',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"'
}
def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

try:
    response = requests.request("GET", url, headers=headers, data=payload).json()
    for item in response:
        data_list = []
        people_detail=[]

        number = item.get("tipoExpediente")
        series = item.get("serieExpediente")
        exper = item.get("numeroExpediente")
        id=f"{number}{series}-{exper}"
        registration=item["numRegistro"]
        titulo = item.get("titulo")
        titulares = item.get("titulares")

        inventores = item.get("inventores")
        people_detail.append({
            "designation": "founder",
            "name":inventores
        })

        apoderados = item.get("apoderados")
        people_detail.append({
            "designation": "registered_agent",
            "name":apoderados
        })

        publicacion = format_date(item.get("fechaPublicacion"))
        presentacion = format_date(item.get("fechaPresentacion"))

        status=item.get("status")

        priorities=item.get("prioridades")
        cip=item.get("cip")

        OBJ = {
            "id":id,
            "registration_number":registration,
            "description": titulo,
            "name": titulares,
            "people_detail":people_detail,
            "registration_date":publicacion,
            "application_date":presentacion,
            'status':status,
            'priorities':priorities,
            'cip':cip
        }
        OBJ =  dominican_republic.prepare_data_object(OBJ)
        ENTITY_ID = dominican_republic.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'],)
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = dominican_republic.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        dominican_republic.insert_record(ROW)

    dominican_republic.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    dominican_republic.db_log(log_data)

except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        log_data = {"status": "fail",
                    "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

        dominican_republic.db_log(log_data)