import sys, os, traceback, time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV

"""Crawler Meta Data Details"""
meta_data = {
    'SOURCE' :'Ministry of Productive Development and Plural Economy - Electronic Gazette of the Commerce Registry',
    'COUNTRY' : 'Bolivia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://miempresa.seprec.gob.bo/#/consulta-empresas?q=SA", 
                        "Source Description": "The Ministry of Productive Development and Plural Economy, created the Plurinational Commercial Registry Service (“SEPREC”), a decentralised public law entity that came into full force and effect on April 1, 2022, for purposes of replacing the administration and operation of the Commercial Registry, at a national level. This transition aims to improve efficiency, transparency, and accessibility for businesses and individuals engaging with the Commercial Registry, fostering a more productive and plural economic environment in Bolivia."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://miempresa.seprec.gob.bo/#/consulta-empresas?q=SA'
}

"""Crawler Configuration"""
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME':"Bolivia Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

bolivia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  bolivia_crawler.get_requests_helper()
session = bolivia_crawler.get_requests_session()

alphabets_digits = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0','1','2','3','4','5','6','7','8','9']
"""Input Arguments"""
arguments = sys.argv
start_alphabet= arguments[1] if len(arguments)>1 else alphabets_digits[0]

def total_pages_number(alphabets_digits, start_alphabet):
    """
    Description: Calculate total pages for a given set of alphabet digits.
    @param:
    - alphabets_digits(str): String containing alphabet digits.
    @return:
    Tuple containing:
    - STATUS_CODE (int): HTTP status code of the request.
    - DATA_SIZE (int): Size of the response data.
    - CONTENT_TYPE (str): Content type of the response.
    - total_pages (int): Total number of pages based on the API response.
    - limit (int): Number of records per page.
    - alphabet_digit (str): Current alphabet digit being processed.
    - start_alphabet (str): Start alphabet digit being processed.
    """
    
    start_alphabets_digits = alphabets_digits.index(start_alphabet)
    for alphabet_digit in range(start_alphabets_digits, len(alphabets_digits)):
        current_alphabet_digit = alphabets_digits[alphabet_digit] 
       
        base_url = f"https://servicios.seprec.gob.bo/api/empresas/buscarEmpresas?filtro={current_alphabet_digit}&tipoFiltro=nombre&limite=100"
        response = request_helper.make_request(base_url)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        resutl = response.json()
        total_records = resutl['datos']['total']
        limit = len(resutl['datos']['filas'])
        total_pages = -(-total_records // limit)
        return STATUS_CODE, DATA_SIZE,CONTENT_TYPE, total_pages, limit, current_alphabet_digit


STATUS_CODE, DATA_SIZE,CONTENT_TYPE, total_pages, limit, current_alphabet_digit = total_pages_number(alphabets_digits, start_alphabet)

def main_function(total_pages, limit, current_alphabet_digit):
    """
    Description: Main Function for inserting data in DB and papare data object.
    @param:
    - total_pages: (int)
    - limit: (int)
    - current_alphabet_digit: (str)
    @return:
    - None
    """
    for page_number in range(1, total_pages+1):
        print(f"Number of Pages {total_pages} in Alphabet:{current_alphabet_digit}")
        API_URL = f"https://servicios.seprec.gob.bo/api/empresas/buscarEmpresas?filtro={current_alphabet_digit}&tipoFiltro=nombre&limite={limit}&pagina={page_number}"
        while True:
            response_url = request_helper.make_request(method='GET',url=API_URL)
            if not response_url:
                continue
            if response_url.status_code == 200:
                data_response = response_url.json()
                break
            else:
                time.sleep(8)
        
        for row in data_response['datos']['filas']:
            id_value = row.get('id', 'No ID found')
            id_est=row.get('idEstablecimiento', 'No ID found')
            empresas_response=request_helper.make_request(f"https://servicios.seprec.gob.bo/api/empresas/informacionBasicaEmpresa/{id_value}/establecimiento/{id_est}").json()
            print(empresas_response)
            Matrícula_de_comercio=empresas_response['datos']['matricula'] if 'matricula' in empresas_response['datos'] else ""
            Matrícula_anterior=empresas_response['datos']['matriculaAnterior'] if 'matriculaAnterior' in empresas_response['datos'] else ""
            Actividad=empresas_response['datos']['razonSocial'].strip() if 'razonSocial' in empresas_response['datos'] else ""
            Tipo_de_societario = (empresas_response['datos']['codTipoUnidadEconomica']['nombre']if 'datos' in empresas_response and 'codTipoUnidadEconomica' in empresas_response['datos'] and 'nombre' in empresas_response['datos']['codTipoUnidadEconomica']else "")        
            Departamento = (empresas_response['datos']['direccion']['codDepartamento']['nombre']if empresas_response.get('datos','') and empresas_response['datos'].get('direccion') and empresas_response['datos']['direccion'].get('codDepartamento') and 'nombre' in empresas_response['datos']['direccion']['codDepartamento']else "")       
            nit=empresas_response['datos']['nit'] if "nit" in empresas_response['datos'] else ""
            Estado_matrícula = (empresas_response['datos']['codEstadoActualizacion']['nombre']if 'datos' in empresas_response and 'codEstadoActualizacion' in empresas_response['datos'] and 'nombre' in empresas_response['datos']['codEstadoActualizacion']else "")
            OBJ={
                "registration_number":Matrícula_de_comercio,
                "name":Actividad.replace("\"",""),
                "type":Tipo_de_societario,
                "jurisdiction":Departamento,
                "tax_number":nit,
                "status":Estado_matrícula,
                "previous_registration_number":Matrícula_anterior
                }
            print(OBJ)
            
            OBJ =  bolivia_crawler.prepare_data_object(OBJ)
            ENTITY_ID = bolivia_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = ""
            ROW = bolivia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            bolivia_crawler.insert_record(ROW)
            print('Searching Alphabet and Digit',current_alphabet_digit)
try:
    main_function(total_pages, limit, current_alphabet_digit)
    bolivia_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    bolivia_crawler.db_log(log_data)

except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        log_data = {"status": "fail",
                    "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

        bolivia_crawler.db_log(log_data)
           
  