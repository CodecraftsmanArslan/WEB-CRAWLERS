"""Import required library"""
import sys, traceback,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup


"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

"""Crawler Meta Data Details"""
meta_data = {
    'SOURCE' :'Rhode Island Secretary of State',
    'COUNTRY' : 'Rhode Island',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearch.aspx", 
                        "Source Description": "The Rhode Island Secretary of State website serves as the official online platform for the Office of the Secretary of State in the state of Rhode Island, USA. It provides a wide range of services and resources related to business filings, elections, and government information. The website offers various tools and features to assist individuals, businesses, and organizations in accessing important information and conducting official transactions."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearch.aspx'
}

"""Crawler Configuration"""
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Rhode Island Official Registry"
}

rhode_island_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = rhode_island_crawler.get_requests_helper()

def get_view_stats(soup):
    """
    Extracts dynamic values from a BeautifulSoup object representing a webpage.
    
    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the webpage.

    Returns:
    Tuple[str, str, str, str, str]: A tuple containing the extracted dynamic values in the following order:
        - viewstate_value (str): The value of the "__VIEWSTATE" input field.
        - viewstate_generator (str): The value of the "__VIEWSTATEGENERATOR" input field.
        - event_validation (str): The value of the "__EVENTVALIDATION" input field.
        - lst_filling (str): The value of the "ALL FILINGS" option in the "select" element.
        - view_filling (str): The value of the "ctl00$MainContent$btnViewFilings" input field.
    """
    if soup:
        viewstate = soup.find(id="__VIEWSTATE")
        viewstate_value = viewstate["value"]
        viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
        viewstate_generator = viewstategen["value"]
        event = soup.find(id="__EVENTVALIDATION")
        event_validation = event["value"]
        option = soup.find("option", selected="selected", string="ALL FILINGS")
        lst_filling = option["value"]
        input_tag = soup.find("input", attrs={"name": "ctl00$MainContent$btnViewFilings"})
        view_filling = input_tag["value"]

        return viewstate_value, viewstate_generator, event_validation, lst_filling, view_filling

def main_function(start_id , end_id):
    """
    This function retrieves and processes business information from the Rhode Island Secretary of State website.
    @params:
    - start_id (int): The starting identification number for business records.
    - end_id (int): The ending identification number for business records.
    @return:
    - tuple: A tuple containing the HTTP status code, data size, and content type of the request.
    """
    for id_number in range(start_id, end_id + 1):
        id_number = str(id_number).zfill(9)
        print("record number", id_number)
        api_url = f'https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSummary.aspx?FEIN={id_number}' 
        response =  request_helper.make_request(api_url)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        soup = BeautifulSoup(response.text, "html.parser")

        if "MainContent_lblMessage" in response.text:
            print("record not exist of id :", id)
            continue

        people_list = list()
        data = dict()

        data['name'] = soup.find(id='MainContent_lblEntityName').text.strip() if soup.find(id='MainContent_lblEntityName') else ""
        data['entity_type'] = soup.find(id='MainContent_lblEntityType').text.strip() if soup.find(id='MainContent_lblEntityType') else ""
        data['identification_number'] = soup.find(id='MainContent_lblIDNumber').text.split(':')[-1].strip() if  soup.find(id='MainContent_lblIDNumber') else ""
        data['incorporation_date'] = soup.find(id='MainContent_lblOrganisationDate').text.strip() if  soup.find(id='MainContent_lblOrganisationDate') else ''
        data['effective_date'] = soup.find(id='MainContent_lblEffectiveDate').text.strip() if  soup.find(id='MainContent_lblEffectiveDate') else ''
        data['dissolution_date'] = soup.find(id='MainContent_lblInactiveDate').text.strip() if soup.find(id='MainContent_lblInactiveDate') else ''
        data['address'] = soup.find(id='MainContent_lblPrincipleStreet').text.strip() if soup.find(id='MainContent_lblPrincipleStreet') else ''
        data['city'] = soup.find(id='MainContent_lblPrincipleCity').text.strip() if soup.find(id='MainContent_lblPrincipleCity') else ''
        data['state'] = soup.find(id='MainContent_lblPrincipleState').text.strip() if soup.find(id='MainContent_lblPrincipleState') else ''
        data['zip'] = soup.find(id='MainContent_lblPrincipleZip').text.strip() if soup.find(id='MainContent_lblPrincipleZip') else ''
        data['country'] = soup.find(id='MainContent_lblPrincipleCountry').text.strip() if soup.find(id='MainContent_lblPrincipleCountry') else ''
        
        previous_name_details = []
        try:
            NameChange = soup.find(id= 'MainContent_tblNameChange')
            pattern = re.compile(r'<div class="p1"><b>The name was changed from: </b>(.*?)<b> on </b>(.*?)</div>')
            matches = pattern.findall(str(NameChange))
            previous_name_details = [{"name": name, "update_date": date} for name, date in matches]
        except:
            previous_name_details = []
        try:
            FictitiousName = soup.find(id= 'MainContent_tblFictitiousName')
            pattern_ = re.compile(r'<div class="p1"><b>The fictitious name of: </b>(.*?)<b> was filed on </b>(.*?)</div>')
            matches_ = pattern_.findall(str(FictitiousName))
            fictitious_data = [{"name": match[0], "date": match[1], "description": f'The fictitious name of:{match[0]} was filed on {match[1]}'} for match in matches_]
        except:
            fictitious_data = []
        registered_agent_name = soup.find(id='MainContent_lblResidentAgentName').text.strip() if soup.find(id='MainContent_lblResidentAgentName') else ''
        registered_agent_address = soup.find(id='MainContent_lblResidentStreet').text.strip() if soup.find(id='MainContent_lblResidentStreet') else ''
        registered_agent_city = soup.find(id='MainContent_lblResidentCity').text.strip() if soup.find(id='MainContent_lblResidentCity') else ''
        registered_agent_state = soup.find(id='MainContent_lblResidentState').text.strip() if soup.find(id='MainContent_lblResidentState') else ''
        registered_agent_zip = soup.find(id='MainContent_lblResidentZip').text.strip() if soup.find(id='MainContent_lblResidentZip') else ''
        registered_agent_country = soup.find(id='MainContent_lblResidentCountry').text.strip() if soup.find(id='MainContent_lblResidentCountry') else ''

        # Get registered_agent for people details
        registered_agent = dict()
        registered_agent['name'] = registered_agent_name
        components = [registered_agent_address, registered_agent_city, registered_agent_state, registered_agent_zip, registered_agent_country]
        registered_agent['address'] = ' '.join(component for component in components if component)
        registered_agent['designation'] = "registered_agent"
        people_list.append(registered_agent) if registered_agent_name else ''
        
        table_people_data = soup.find(id='MainContent_grdOfficers')
        if table_people_data:
            table_rows = table_people_data.find_all('tr')
            for row in table_rows[1:]:
                cells = row.find_all('td')
                if len(cells) > 1:
                    people = dict()
                    people['designation'] = cells[0].text.strip()
                    people['name'] = cells[1].text.strip()
                    people['address'] = cells[2].text.strip()
                    people_list.append(people) if people['name'] != '' else ''

        data['people_list'] = people_list

        table_stock_data = soup.find(id='MainContent_grdStocks')
        if table_stock_data:
            table_rows = table_stock_data.find_all('tr')
            for row in table_rows:
                cells = row.find_all('td')
                if len(cells) > 3:
                    data['stock_class'] = cells[0].text.strip()
                    data['series'] = cells[1].text.strip()
                    data['share_per_value'] = cells[2].text.strip()
                    data['authorized_share'] = cells[3].text.strip()
                    data['issued_share'] = cells[4].text.strip()
                else:
                    data['stock_class'] = ''
                    data['series'] = ''
                    data['share_per_value'] = ''
                    data['authorized_share'] = ''
                    data['issued_share'] = ''
        else:
            data['stock_class'] = ''
            data['series'] = ''
            data['share_per_value'] = ''
            data['authorized_share'] = ''
            data['issued_share'] = ''

        naics_code_element = soup.find('input',id="MainContent_txtNIACS")

        if naics_code_element:
            data['naics_code'] = naics_code_element.get('value', '')

        purpose = soup.find(id='MainContent_txtComments') if soup.find(id='MainContent_txtComments') else ''
        data['purpose'] = purpose.text.strip().replace('\n', '').replace('\r', '') if purpose else ''

        viewstate = soup.find(id="__VIEWSTATE")
        viewstate_value = viewstate["value"]
        

        viewstategen = soup.find(id="__VIEWSTATEGENERATOR")
        viewstate_generator = viewstategen["value"]

        event = soup.find(id="__EVENTVALIDATION")
        event_validation = event["value"]

        option = soup.find(
            "option", selected="selected", text="ALL FILINGS")
        lst_filling = option["value"]

        input_tag = soup.find(
            "input", attrs={"name": "ctl00$MainContent$btnViewFilings"})
        view_filling = input_tag["value"]

        BODY = {
            '__EVENTTARGET': "",
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': viewstate_value,
            '__VIEWSTATEGENERATOR': viewstate_generator,
            '__SCROLLPOSITIONX': 0,
            ' __SCROLLPOSITIONY': 0,
            '__EVENTVALIDATION': event_validation,
            'ctl00$MainContent$txtComments':  "",
            'ctl00$MainContent$txtNIACS': "",
            'ctl00$MainContent$lstFilings': lst_filling,
            'ctl00$MainContent$btnViewFilings': view_filling,
        }

        nine_number_format = "{:09d}".format(int(id_number))

        file_url = f"https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSummary.aspx?FEIN={nine_number_format}"

        filling_response =  request_helper.make_request(file_url, method='POST', data=BODY)
        filling_soup = BeautifulSoup(filling_response.text, "html.parser")

        filling_details = list()
        filing_table =  filling_soup.find("table", id="MainContent_grdSearchResults")
        base_url  ='https://business.sos.ri.gov/CorpWeb/CorpSearch/'
        if filing_table:
            table_rows = filing_table.find_all('tr')
            for row in table_rows[1:]:
                cells = row.find_all('td')
                filling_obj = dict()
                filling_obj['title'] = cells[1].text.strip()
                filling_obj['date'] = cells[3].text.strip().split(" ")[0].replace("/", "-")
                filling_obj['filing_code'] = cells[4].text.strip()
                try:
                    file_link = base_url+cells[5].find('a')['href']
                except:
                    file_link = ""
                filling_obj['file_url'] = file_link
                if cells[2]:
                    filling_obj['meta_detail'] = {
                        'year': cells[2].text.strip()
                    }

                filling_details.append(filling_obj)


        data['fillings_detail'] = filling_details
        
        # Get all additional_detail
        additional_detail = []
        if (data.get('stock_class','') or data.get('series','') or data.get('share_per_value','') or data.get('authorized_share','') or data.get('issued_share','') != ''):
            share_information = {
                'type': "share_information",
                'data': [
                    {
                        'stock_class': data['stock_class'],
                        'series': data['series'],
                        'share_per_value': data['share_per_value'],
                        'authorized_share': data['authorized_share'],
                        'issued_share': data['issued_share'],
                    },
                ],
            }
            additional_detail.append(share_information)

        if data.get('naics_code','') != '':
            naics_information = {
                'type': "naics_code",
                'data': [
                    {
                        'naics_code': data.get('naics_code',''),
                    },
                ],
            }
            additional_detail.append(naics_information)
        if fictitious_data != []:
            fictitious_names = {
                "type":"fictitious_name_details",
                "data":fictitious_data
            }
            additional_detail.append(fictitious_names)

        #Get addresses_detail
        general_address = data['address']+' '+data['city']+' '+data['state']+' '+data['zip']+' '+data['country']
        if general_address != "":
            addresses_detail = [
                {
                    'type' : 'general_address',
                    'address' : general_address
                }
            ]

        OBJ = {
            "name": data['name'],
            "registration_number": data['identification_number'],
            "type": data['entity_type'],
            "addresses_detail": addresses_detail,
            'effective_date' : data['effective_date'],
            "purpose": data['purpose'],
            "people_detail": data['people_list'],
            "fillings_detail": data['fillings_detail'],      
            "incorporation_date": data['incorporation_date'],
            "dissolution_date": data['dissolution_date'],
            "additional_detail": additional_detail,
            "previous_names_detail":previous_name_details,
        }

        OBJ =  rhode_island_crawler.prepare_data_object(OBJ)
        ENTITY_ID = rhode_island_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
        ROW = rhode_island_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        rhode_island_crawler.insert_record(ROW)
    
    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    """Input Arguments"""
    arguments = sys.argv
    start_id = int(arguments[1]) if len(arguments)>1 else 1
    end_id = int(arguments[2]) if len(arguments)>2 else 1800000
    
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = main_function(start_id, end_id)

    """Success DB logs"""
    rhode_island_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    rhode_island_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    """Error DB logs with path"""
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    rhode_island_crawler.db_log(log_data)