"""Set System Path"""
import sys, traceback,time,re,json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from ranges import ranges

meta_data = {
    'SOURCE' :'Skatturinn - Iceland Revenue and Customs',
    'COUNTRY' : 'Iceland',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.skatturinn.is/fyrirtaekjaskra/", 
                        "Source Description": "The Directorate of Internal Revenue is a government agency in Iceland that is responsible for administering and enforcing tax laws. Its main tasks include processing tax returns, collecting various taxes such as income tax, value-added tax (VAT), and corporate tax, conducting tax audits, providing guidance to taxpayers, and ensuring compliance with tax regulations."},
    'URL' : 'https://www.skatturinn.is/fyrirtaekjaskra/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Iceland'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

ice_land_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  ice_land_crawler.get_requests_helper()

def get_table_data(th_element):
    try:
        data = []
        table = th_element.find_parent('table')
        if table:
            header_row = table.find('thead').find('tr')
            data_rows = table.find('tbody').find_all('tr')
            headers = [header.text.strip() for header in header_row.find_all('th')]
            for row in data_rows:
                cells = [cell.text.strip() for cell in row.find_all('td')]
                row_data = dict(zip(headers, cells))
                data.append(row_data)
        return data
    except AttributeError as e:
        return data

def find_next_element_text(element):
    if element is not None:
        ul_element = element.find_next_sibling('ul')
        if ul_element is not None:
            text = ul_element.text.strip()
            return text
    return ""

if len(sys.argv) > 1:
    start = int(sys.argv[1])
else:
    start = 0

updated_ranges = sorted(ranges, key=lambda x: x[0])
base_url = "https://www.skatturinn.is"
try:
    for num in range(start, 799999+1):
        security_number = str(num).zfill(6)
        print(security_number)
        url = f"{base_url}/fyrirtaekjaskra/leit?nafn=&heimili=&kt={security_number}&vsknr="
        response = request_helper.make_request(url, method="GET")
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        html_content = response.text
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find('table')
        if table is None:
            continue
        rows = table.find('tbody').find_all('tr')
        security_links = []
        for row in rows:
            link_element = row.find('a')
            if link_element is not None:
                security_links.append(link_element['href'])

        for link in security_links:
            time.sleep(1)
            addresses_detail = []
            additional_detail = []
            fillings_detail = []
            people_detail = []
            url = f"{base_url}{link}"
            response = request_helper.make_request(url, method="GET")
            html_content = response.text
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            header_div = soup.find('div', class_='boxbody cart-open')
            if soup.find('h1') is None:
                continue
            h1 = soup.find('h1').text.strip()
            if '(' not in h1:
                continue
            NAME = h1.split('(')[0].strip().replace("%", "%%").replace("-","")
            registration_number = h1.split('(')[1].replace(')', '').strip()
            registration_date = header_div.find('h2').text.split(":")[1].strip().replace(".", "-") if header_div.find('h2') is not None and len(header_div.find('h2').text.split(":")) >= 2 else ""
            type_ = ""
            th_element = soup.find('th', string='Póstfang')
            addresses_detail_data = get_table_data(th_element)
            for row in addresses_detail_data:
                if row.get('Póstfang') is not None and row.get('Póstfang') != "":
                    addresses_detail.append({
                        "type": "postal_address",
                        "address": row.get('Póstfang').replace("  ", " ")
                    })
                if row.get('Lögheimili') is not None and row.get('Lögheimili') != "":
                    addresses_detail.append({
                        "type": "office_address",
                        "address": row.get('Lögheimili').replace("  ", " ")
                    })
                if row.get('Sveitarfélag') is not None and row.get('Sveitarfélag') != "":
                    addresses_detail.append({
                        "type": "general_address",
                        "address": row.get('Sveitarfélag').replace("  ", " ")
                    })
                type_ = row.get('Rekstrarform')
            h3_element = soup.find('h3', string='ÍSAT Atvinnugreinaflokkun')
            industries = find_next_element_text(h3_element)

            th_element = soup.find('th', string='Númer')
            vat_detail_data = get_table_data(th_element)
            for row in vat_detail_data:
                additional_detail.append({
                    "type": "vat_detail",
                    "data": [{
                        "number": row.get('Númer'),
                        "start_date": row.get('Skráning').replace(".", "-") if row.get('Skráning') is not None else "",
                        "end_date": row.get('Afskráning').replace(".", "-") if row.get('Afskráning') is not None else "",
                        "activity": row.get('ÍSAT nr.').replace("  ", "").replace("\n\n", " ") if row.get('ÍSAT nr.') is not None else ""
                    }]
                })

            th_element = soup.find('th', string='Rek. ár')
            fillings_detail_data = get_table_data(th_element)
            for row in fillings_detail_data:
                if row.get('Rek. ár') is not None and row.get('Rek. ár') != "" and row.get('Rek. ár') != "NONE":
                    meta_detail = {
                            "filing_year": row.get('Rek. ár')
                        }
                else: 
                    meta_data = {}
                fillings_detail.append({
                    "title": row.get('Nafn').replace("%", "%%") if row.get('Nafn') is not None else "",
                    "date": row.get('Skiladagsetning').replace(".", "-") if row.get('Skiladagsetning') is not None else "",
                    "filing_code": row.get('Nr. ársreiknings'),
                    "meta_detail": meta_detail
                })
            
            th_element = soup.find('th', string='Fæðingarár/mán')
            if th_element is not None:
                h4_tag = th_element.find_previous('h4')
                if h4_tag is not None:
                    beneficial_owner_name = h4_tag.text
                else:
                    beneficial_owner_name = ""
                    
            beneficial_owner_data = get_table_data(th_element)
            for row in beneficial_owner_data:
                additional_detail.append({
                    "type": "beneficial_owner",
                    "data": [{
                        "name": beneficial_owner_name,
                        "date_of_birth": row.get('Fæðingarár/mán').replace("'", "").replace("%", "%%") if row.get('Fæðingarár/mán') is not None else "",
                        "nationality": row.get('Búsetuland').replace("'", "").replace("%", "%%") if row.get('Búsetuland') is not None else "",
                        "address": row.get('Ríkisfang').replace("'", "").replace("%", "%%") if row.get('Ríkisfang') is not None else "",
                        "ownership_percentage": row.get('Eignarhlutur').replace("'", "").replace("%", "%%") if row.get('Eignarhlutur') is not None else "",
                        "type": row.get('Tegund eignahalds').replace("'", "").replace("%", "%%") if row.get('Tegund eignahalds') is not None else ""
                    }]
                })

            h3_element = soup.find('h3', string='Forráðamaður')
            element_text = find_next_element_text(h3_element)
            try:
                if ' - ' in element_text:
                    people_name, people_designation = element_text.split(' - ')
                    if len(element_text.split(' - ')) > 0:
                        people_detail.append({
                            "name": people_name.replace("\n", ""),
                            "designation": people_designation.replace("\n", "")
                        })
            except:
                pass
            # Find the element with class 'boxbody'
            boxbody_element = soup.find(class_='boxbody')
            # Find all elements with class 'highlight' within the 'boxbody' element
            highlight_elements = boxbody_element.find_all(class_='highlight')
            status = ', '.join(element.text.strip().replace('(', '').replace(')', '') for element in highlight_elements)
            type_element = soup.find('h2', string='Rekstrarform')
            type = type_element.find_next_sibling(string=True).strip() if type_element is not None else ""
            if type != "" and type_ != "":
                type = f"{type}, {type_}" 
            if type == "":
                type = type_

            DATA = {
                "name": NAME,
                "registration_number": registration_number,
                "registration_date": registration_date,
                "addresses_detail": addresses_detail,
                "type": type,
                "status": status,
                "industries": industries,
                "additional_detail": additional_detail,
                "fillings_detail": fillings_detail,
                "people_detail": people_detail,
            }
            ENTITY_ID = ice_land_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
            BIRTH_INCORPORATION_DATE = ''
            DATA = ice_land_crawler.prepare_data_object(DATA)
            ROW = ice_land_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)

            ice_land_crawler.insert_record(ROW)
            
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    ice_land_crawler.db_log(log_data)
    ice_land_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    ice_land_crawler.db_log(log_data)
