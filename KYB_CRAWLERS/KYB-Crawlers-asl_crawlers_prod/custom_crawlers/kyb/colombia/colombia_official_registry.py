"""Set System Path"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE' :'Cámara de Comercio de Bogotá',
    'COUNTRY' : 'Colombia (Bogota chamber of commerce)',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://linea.ccb.org.co/ccbConsultasRUE/Consultas/RUE/consulta_resultado.aspx", 
                        "Source Description": "The Chamber of Commerce in Colombia, known as ''Cámara de Comercio,'' is a non-profit organization that represents the interests of businesses and promotes economic development in the country. It serves as a bridge between the government, businesses, and entrepreneurs, providing various services and resources to support the growth and success of the business community."},
    'URL' : 'https://linea.ccb.org.co/ccbConsultasRUE/Consultas/RUE/consulta_resultado.aspx',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': True,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Colombia (Bogota chamber of commerce)'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

colombia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  colombia_crawler.get_requests_helper()

def get_paras(url):
    response = request_helper.make_request(url)
    soup = BeautifulSoup(response.text, "html.parser")
    viewstate = soup.find(id="__VIEWSTATE")
    viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
    event = soup.find(id="__EVENTVALIDATION")
    
    res = {
        "viewstate_value": viewstate["value"] if viewstate else "",
        "viewstate_generator": viewstategen["value"] if viewstategen else "",
        "event_validation": event["value"] if event else ""
    }
    
    return res

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 1

try:
    url = "https://linea.ccb.org.co/ccbConsultasRUE/Consultas/RUE/consulta_empresa.aspx"
    params = get_paras(url)
    for i in range(start, 3692904):
        record_num = str(i).zfill(10)
        print('Record No. ', record_num)
        
        if i % 10000 == 0:
            params = get_paras(url)

        payload = {
            "__VIEWSTATE": params.get('viewstate_value'),
            "__VIEWSTATEGENERATOR": params.get('viewstate_generator'),
            "__EVENTVALIDATION": params.get('event_validation'),
            "ddlTipId": "01",
            "tipo": "rbtMatricula",
            "txtMatricula": record_num,
            "btnIr.x":82,
            "btnIr.y":10
        }
        response = request_helper.make_request(url, method="POST", data=payload)
        if response is None:
            continue

        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        html_content = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find('table', attrs={'id': 'dtgResultados'})

        if table is None:
            continue

        # Find all table rows except the header row
        rows = soup.find_all('tr', class_='contenidos10p')

        # Create a list to hold the dictionaries of each row
        data = []
        for row in rows:
            # Extract the row data
            columns = row.find_all('td')
            camara_de_comercio = columns[0].text.strip().replace("'", "").replace("%", "%%") if columns[0].text is not None else ""
            matricula = columns[1].a.text.strip().replace("'", "").replace("%", "%%") if columns[1].text is not None else ""
            razon_social = columns[2].text.strip().replace("'", "").replace("%", "%%") if columns[2].text is not None else ""
            organizacion_juridica = columns[3].text.strip().replace("'", "").replace("%", "%%") if columns[3].text is not None else ""
            ultimo_ano_renovado = columns[4].text.strip().replace("'", "").replace("%", "%%") if columns[4].text is not None else ""
            estado = columns[5].text.strip().replace("'", "").replace("%", "%%") if columns[5].text is not None else ""
            
            if matricula is None and razon_social is None:
                continue

            DATA = {
                'jurisdiction': camara_de_comercio,
                'registration_number': matricula,
                'name': razon_social,
                'type': organizacion_juridica,
                'last_year_renewed': ultimo_ano_renovado,
                'status': estado
            }

            ENTITY_ID = colombia_crawler.generate_entity_id(company_name=razon_social, reg_number=matricula)
            BIRTH_INCORPORATION_DATE = ''
            DATA = colombia_crawler.prepare_data_object(DATA)
            ROW = colombia_crawler.prepare_row_for_db(ENTITY_ID, razon_social, BIRTH_INCORPORATION_DATE, DATA)

            colombia_crawler.insert_record(ROW)
            
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    colombia_crawler.db_log(log_data)
    colombia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    colombia_crawler.db_log(log_data)